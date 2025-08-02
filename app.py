# ===== IMPORTS & DEPENDENCIES =====
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from google import genai
from google.genai import types
import os
import json
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import tempfile
import uuid
import pickle

# ===== CONFIGURATION & CONSTANTS =====
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['DATA_FOLDER'] = os.path.join(tempfile.gettempdir(), 'code_analyzer_data')

# Progress bar duration in seconds (configurable)
PROGRESS_DURATION = 120

# Create data folder if it doesn't exist
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# ===== INITIALIZATION & STARTUP =====
def load_api_key():
    """Load Gemini API key from env.txt file"""
    try:
        with open('env.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise Exception("env.txt file not found. Please create it with your Gemini API key.")

def load_prompt():
    """Load the analysis prompt from prompt.txt file"""
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise Exception("prompt.txt file not found.")

# Initialize Gemini API
api_key = load_api_key()
client = genai.Client(api_key=api_key)

# Load the analysis prompt
analysis_prompt = load_prompt()

# ===== UTILITY FUNCTIONS =====
def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'txt', 'py', 'js', 'java', 'cpp', 'c', 'cs', 'php', 'rb', 'go', 'rs', 'swift', 'kt', 'ts', 'html', 'css', 'sql', 'sh', 'bat', 'ps1'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_file_to_txt(file_path, original_filename):
    """Convert uploaded file to .txt extension for Gemini compatibility"""
    base_name = os.path.splitext(original_filename)[0]
    txt_filename = f"{base_name}.txt"
    txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
    
    # Copy content to new .txt file
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
        content = src.read()
    
    with open(txt_path, 'w', encoding='utf-8') as dst:
        dst.write(content)
    
    return txt_path, txt_filename

def save_data_to_file(data, data_id):
    """Save data to a temporary file to avoid session size limits"""
    file_path = os.path.join(app.config['DATA_FOLDER'], f"{data_id}.pkl")
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
    return file_path

def load_data_from_file(data_id):
    """Load data from temporary file"""
    file_path = os.path.join(app.config['DATA_FOLDER'], f"{data_id}.pkl")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return None

def cleanup_data_file(data_id):
    """Clean up temporary data file"""
    file_path = os.path.join(app.config['DATA_FOLDER'], f"{data_id}.pkl")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass

def analyze_code_with_gemini(code_content):
    """Send code to Gemini for analysis"""
    try:
        full_prompt = f"{analysis_prompt}\n\n```\n{code_content}\n```"
        print(f"Sending request to Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=8192
            )
        )
        
        print(f"Received response from Gemini API")
        # Extract JSON from response
        response_text = response.text.strip() if response.text else ""
        print(f"Response text length: {len(response_text)}")
        
        # Check if response is empty
        if not response_text:
            print("Empty response from Gemini API")
            raise Exception("Received empty response from Gemini API")
        
        # Try to find JSON in the response
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text (first 500 chars): {response_text[:500]}")
            
            # If JSON parsing fails, try to extract JSON from the text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_text = response_text[start_idx:end_idx]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError as e2:
                    print(f"Second JSON parsing attempt failed: {str(e2)}")
                    print(f"Extracted JSON text: {json_text[:500]}")
                    raise Exception(f"Could not parse JSON response from Gemini: {str(e)}")
            else:
                raise Exception(f"Could not find valid JSON in response: {str(e)}")
                
    except Exception as e:
        return {
            "error": True,
            "message": f"Analysis failed: {str(e)}",
            "analysis_summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "major_issues": 0,
                "minor_issues": 0,
                "suggestions": 0,
                "overall_score": "N/A",
                "analysis_timestamp": datetime.now().isoformat()
            }
        }

# ===== API ROUTES & CONTROLLERS =====
@app.route('/')
def index():
    """Main page with code input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle code analysis request"""
    code_content = ""
    
    # Debug: Print request data
    print(f"Request form keys: {list(request.form.keys())}")
    print(f"Request files keys: {list(request.files.keys())}")
    
    # Check if code was pasted or file was uploaded
    if 'code_text' in request.form and request.form['code_text'].strip():
        code_content = request.form['code_text']
        print(f"Received pasted code, length: {len(code_content)}")
    elif 'code_file' in request.files:
        file = request.files['code_file']
        print(f"Received file: {file.filename if file else 'None'}")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Convert to .txt if needed
            if not filename.endswith('.txt'):
                file_path, filename = convert_file_to_txt(file_path, filename)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            
            # Clean up temporary file
            try:
                os.remove(file_path)
            except:
                pass
        else:
            return jsonify({'error': 'Invalid file type or no file selected'}), 400
    else:
        print("No code_text or code_file found in request")
        return jsonify({'error': 'No code provided'}), 400
    
    if not code_content.strip():
        print("Code content is empty after processing")
        return jsonify({'error': 'Empty code content'}), 400
    
    # Generate unique ID for this analysis session
    analysis_id = str(uuid.uuid4())
    
    # Store code in file instead of session to avoid size limits
    save_data_to_file(code_content, f"code_{analysis_id}")
    
    # Store only the analysis ID in session
    session['analysis_id'] = analysis_id
    print(f"Analysis started with ID: {analysis_id}")
    return jsonify({'success': True})

@app.route('/progress')
def progress():
    """Progress page with loading animation"""
    return render_template('progress.html', duration=PROGRESS_DURATION)

@app.route('/process')
def process():
    """Process the code analysis"""
    analysis_id = session.get('analysis_id')
    if not analysis_id:
        return redirect(url_for('index'))
    
    # Load code content from file
    code_content = load_data_from_file(f"code_{analysis_id}")
    if not code_content:
        return redirect(url_for('index'))
    
    # Analyze code with Gemini (removed artificial delay)
    result = analyze_code_with_gemini(code_content)
    
    # Store result in file instead of session
    save_data_to_file(result, f"result_{analysis_id}")
    
    # Clean up code file
    cleanup_data_file(f"code_{analysis_id}")
    
    return jsonify({'success': True, 'redirect': url_for('results')})

@app.route('/results')
def results():
    """Display analysis results"""
    analysis_id = session.get('analysis_id')
    if not analysis_id:
        return redirect(url_for('index'))
    
    # Load result from file
    result = load_data_from_file(f"result_{analysis_id}")
    if not result:
        return redirect(url_for('index'))
    
    return render_template('results.html', result=result)

@app.route('/api/result')
def api_result():
    """API endpoint to get analysis result as JSON"""
    analysis_id = session.get('analysis_id')
    if not analysis_id:
        return jsonify({'error': 'No analysis result found'}), 404
    
    # Load result from file
    result = load_data_from_file(f"result_{analysis_id}")
    if not result:
        return jsonify({'error': 'No analysis result found'}), 404
    
    return jsonify(result)

@app.route('/cleanup')
def cleanup():
    """Clean up analysis data and start fresh"""
    analysis_id = session.get('analysis_id')
    if analysis_id:
        cleanup_data_file(f"code_{analysis_id}")
        cleanup_data_file(f"result_{analysis_id}")
    
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
# Code Analyzer - Gemini AI Code Review Tool

A Flask web application that analyzes your code using Google's Gemini AI. Get comprehensive feedback on syntax, security, performance, and best practices with a modern dark/light mode interface.

## ✨ Key Features

- **Smart Analysis**: AI-powered code review covering syntax, security, performance, and best practices
- **Multiple Input**: Paste code directly or upload files (supports 20+ file types)
- **Modern UI**: Dark/light mode toggle with responsive design
- **Real-time Progress**: Visual progress tracking during analysis
- **Detailed Results**: Color-coded metrics and exportable JSON reports

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Gemini API key** to `env.txt`: (you need to create this file in the root of the repo)
   ```
   your-gemini-api-key-here
   ```

3. **Run the app**:
   ```bash
   python app.py
   ```

4. **Open** `http://127.0.0.1:5000` in your browser

## 📁 Project Structure

```
code-analyzer/
├── app.py              # Main Flask application
├── requirements.txt    # Dependencies
├── env.txt            # Your Gemini API key
├── prompt.txt         # AI analysis prompt
├── templates/         # HTML templates
└── tests/             # Test files for validation
```

## 🎯 How to Use

1. **Choose input method**: Paste code or upload a file
2. **Submit for analysis**: Click "Analyze Code"
3. **Watch progress**: Real-time analysis tracking
4. **Review results**: Comprehensive feedback with metrics
5. **Export**: Copy JSON results to clipboard

## 📊 Analysis Coverage

- **Syntax & Style**: Grammar, formatting, naming conventions
- **Code Quality**: Complexity, duplication, modularity
- **Security**: Vulnerability detection, unsafe patterns
- **Performance**: Algorithm efficiency, memory usage
- **Best Practices**: Modern coding standards

## 🔧 Configuration

- **File size limit**: 16MB (configurable in `app.py`)
- **Supported formats**: .py, .js, .java, .cpp, .c, .cs, .php, .rb, .go, .rs, .swift, .kt, .ts, .html, .css, .sql, .sh, .bat, .ps1, .txt
- **Progress duration**: Real-time tracking (configurable)

## 🛠️ Troubleshooting

**Common Issues:**
- **API Key Error**: Check `env.txt` contains your valid Gemini API key
- **File Upload Issues**: Ensure file is under 16MB and uses supported format
- **Analysis Timeout**: Large files may take longer to process

## 📝 Requirements

- Python 3.7+
- Google Gemini API key
- Internet connection

---

**Test Files**: Check the `tests/` folder for sample code files to validate the analyzer.

## 🐛 Bug Reports & Feedback

Please report any bugs, issues, or feature requests to help improve this tool. Your feedback is valuable for making the code analyzer better for everyone.

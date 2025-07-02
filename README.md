# 🎯 AI Resume Critiquer

An AI-powered resume analysis tool that provides personalized feedback and actionable insights to help job seekers optimize their resumes for specific roles and industries.

## 🌟 Features

- **AI-Powered Analysis**: Resume evaluation using OpenRouter or Ollama models
- **Interactive Chat**: Follow-up conversations with AI career coach
- **PDF Export**: Download professionally formatted analysis reports
- **Document Processing**: Supports PDF and text file parsing

## 🚀 Getting Started

### Prerequisites
- Python 3.13 or higher
- Git (for cloning the repository)

### Installation Methods

#### Option 1: Using UV (Recommended)
```bash
# Clone the repository
git clone https://github.com/syedmuneeruddin5/AI-Resume-Critiquer.git
cd AI-Resume-Critiquer

# Install dependencies with uv
uv sync
```

#### Option 2: Using pip
```bash
# Clone the repository
git clone https://github.com/syedmuneeruddin5/AI-Resume-Critiquer.git
cd AI-Resume-Critiquer

# Create virtual environment
pip install virtualenv
virtualenv -p python3.13 .venv

# Activate environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Additional Setup

### WeasyPrint Installation

**Windows:**
1. Download and install [MSYS2](https://www.msys2.org/#installation)
2. Open MSYS2 terminal and run:
   ```bash
   pacman -S mingw-w64-x86_64-pango
   ```

**macOS:**
```bash
brew install weasyprint
```

**Linux:**
Follow the official [WeasyPrint installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

### AI Provider Configuration

**For OpenRouter (Cloud AI):**
1. Create a free account at [OpenRouter](https://openrouter.ai//)
2. Generate an API key
3. Create a `.env` file in the project root:
   ```
   OPEN_ROUTER_API_KEY=your_api_key_here
   ```

**For Ollama (Local AI):**
1. Download and install [Ollama](https://ollama.com//)
2. Download your preferred model (e.g., `ollama pull gemma3`)
3. Start the Ollama server:
   ```bash
   ollama serve
   ```

## 🎮 Usage

### Launch the Application
```bash
# With uv:
uv run streamlit run main.py

# With pip:
streamlit run main.py
```

## 🛠 Technical Architecture

### Core Technologies
- **Frontend**: Streamlit for responsive web interface
- **Document Processing**: Docling for PDF parsing and text extraction
- **AI Integration**: Multi-provider support (OpenRouter API, Ollama local)
- **PDF Generation**: WeasyPrint with custom CSS styling
- **Markdown Processing**: markdown-it-py for rich text rendering

## 📄 License

This project is available under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Inspired by this [video](https://youtu.be/XZdY15sHUa8?si=FY-jgwX0S_8kLdDR) from Tech with Tim, this implementation extends the original concept with enhancements including:
- Multi-provider AI support
- Interactive chat functionality  
- PDF generation
- Industry-specific analysis
# Resume Parser

A Python-based resume parser using OpenRouter API to extract structured information from resumes.

## Features

- Extracts key information including:
  - Personal details (name, email, phone)
  - Work experience
  - Education
  - Skills
  - Projects
  - Certifications
- JSON output format
- Error handling and validation
- Fallback extraction methods

## Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ResumeParser.git
cd ResumeParser
```

2. Create virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

```python
from resume_parser import ResumeParser

parser = ResumeParser()
result = parser.parse_resume(resume_text)
print(result)
```

## Requirements

- Python 3.8+
- See requirements.txt for full list

## License

MIT License

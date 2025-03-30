# AI-Powered Resume Parser 📄✨

An intelligent resume parser that automatically extracts structured information from resumes (PDF, DOCX, DOC) using AI. Perfect for recruiters, HR teams, and job seekers!

## Features 🚀

* Extracts **name, email, phone, skills, experience, education** and more
* Supports **PDF, DOCX, and DOC** formats
* Clean **Streamlit web interface**
* Powered by **OpenAI GPT-4/3.5** for accurate parsing
* Handles complex resume layouts with **Mammoth & PyPDF2**

## Project Structure 🗂️

```
resume-parser/
├── resume_parser/
│   ├── __init__.py
│   ├── file_reader.py      # Handles file parsing
│   ├── chatgpt_parser.py   # AI text extraction
│   ├── utils.py            # Text cleaning
│   └── config.py           # API configuration
│ 
├── app.py                  # Streamlit UI
├── requirements.txt        # Dependencies
├── .env                    # Environment template
└── README.md
```

## Installation ⚙️

1. Clone the repository:
```bash
git clone https://github.com/DipankarDandapat/ResumeParser.git
cd resume-parser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

## Usage 🖥️

Run the Streamlit app:
```bash
streamlit run app.py
```

Then upload your resume file (PDF/DOCX/DOC) through the web interface.

## How It Works 🔍

1. Upload a resume file
2. The system extracts raw text using:
   * **Mammoth** for DOCX
   * **PyPDF2** for PDF
   * **Textract** for DOC
3. OpenAI GPT processes the text and returns structured JSON
4. Results are displayed in a clean UI

## Example Output 📋

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1 (123) 456-7890",
  "skills": ["Python", "Machine Learning", "SQL"],
  "experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Developer",
      "duration": "2020-Present"
    }
  ],
  "education": [
    {
      "institution": "State University",
      "degree": "B.S. Computer Science",
      "year": "2020"
    }
  ]
}
```

## Customization 🛠️

To modify what fields are extracted, edit the prompt in `chatgpt_parser.py`:

```python
prompt = f"""
Extract resume details in JSON format:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "skills": ["Python", "SQL"],
    "experience": [{{"company": "ABC Corp", "position": "SWE"}}]
}}
Resume Text: {text}
"""
```




import argparse

import json

from resume_parser.file_reader import FileReader
from resume_parser.chatgpt_parser import ResumeParser
from resume_parser.utils import TextCleaner


def main():
    parser = argparse.ArgumentParser(description="Resume Parser using ChatGPT")
    parser.add_argument("file_path", help="Path to the resume file")
    args = parser.parse_args()

    # Read and clean resume text
    raw_text = FileReader.read_file(args.file_path)
    if not raw_text:
        print("Failed to read file")
        return

    cleaned_text = TextCleaner.clean_text(raw_text)

    # Parse with ChatGPT
    parser = ResumeParser()
    result = parser.parse_resume(cleaned_text)

    # Print results
    print("Parsed Resume Data:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

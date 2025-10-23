import re

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = re.sub(r'\x0c', '', text)  # Remove form feed characters
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        return text.strip()

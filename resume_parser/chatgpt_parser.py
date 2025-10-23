import json
import re
import requests
import difflib
from typing import Dict, Any, Optional
from .config import Config

class ResumeParser:
    def __init__(self):
        self.api_key = Config.get_api_key()
        self.model = Config.MODEL_NAME
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": Config.SITE_URL,
            "X-Title": Config.SITE_NAME,
            "Content-Type": "application/json"
        }

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Main method to parse resume text"""
        try:
            # Validate input
            if not text or len(text.strip()) < 50:
                return {
                    "error": "Resume text too short",
                    "min_length": 50,
                    "received": len(text.strip()) if text else 0
                }
            # Get AI response
            response = self._get_ai_response(text)
            if "error" in response:
                return response

            # Parse and validate
            parsed_data = self._parse_and_validate(response, text)
            if "error" in parsed_data:
                return parsed_data

            return parsed_data

        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "type": type(e).__name__,
                "suggestion": "Try again or contact support"
            }

    def _get_ai_response(self, text: str) -> Dict[str, Any]:
        """Get response from OpenRouter API"""
        try:
            response = requests.post(
                url=f"{Config.API_BASE}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [{
                        "role": "user",
                        "content": self._create_prompt(text)
                    }],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "response_format": {"type": "json_object"}
                }
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Debug log
                print("Raw API Response:", content)  # For debugging
                return {"content": content}
            else:
                return {
                    "error": f"OpenRouter API error: Status {response.status_code}",
                    "details": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "code": "request_error"
            }

    def _parse_and_validate(self, response: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Parse and validate the AI response"""
        try:
            content = self._clean_json_response(response["content"])
            result = json.loads(content)

            # Validate minimum required fields
            if not result.get("name") and not result.get("email"):
                # Fallback to direct extraction
                result["name"] = self._extract_name_from_text(original_text) or "Not Found"
                result["email"] = self._extract_email_from_text(original_text) or "Not Found"

                if result["name"] == "Not Found" and result["email"] == "Not Found":
                    return {
                        "error": "Critical fields missing",
                        "missing_fields": ["name", "email"],
                        "raw_text_sample": original_text[:200] + "..." if original_text else None
                    }

            # Validate and clean skills
            result = self._validate_skills(result, original_text)

            # Clean empty values
            for key in list(result.keys()):
                if result[key] in [None, "", "Not Found", []]:
                    del result[key]

            return result

        except json.JSONDecodeError as e:
            return {
                "error": f"Invalid JSON response: {str(e)}",
                "content_sample": response["content"][:200] + "..." if "content" in response else None
            }


    def _create_prompt(self, text: str) -> str:
        """Create the prompt for OpenAI"""

        return f"""
            Extract resume information into this EXACT JSON structure. Follow these rules:

            1. Use null for missing fields
            2. Keep values concise
            3. MUST return valid JSON
            4. Prioritize finding name and email
            5. Extract ONLY relevant technical and professional information — NO assumptions or filler text.

            IMPORTANT: Only include actual information found in the resume, DO NOT use example values.

            Required structure:
            {{
                "name": "Full Name (if found, otherwise null)",
                "email": "Email address (if found, otherwise null)",
                "phone": "Phone number (if found, otherwise null)",
                "linkedin": "LinkedIn profile URL (if found, otherwise null)",
                "github": "GitHub profile URL (if found, otherwise null)",
                "headline_summary": "<1 short paragraph professional summary>",
                "role": "<Current or most recent job title>",
                "key_responsibilities": [
                    "<Concise bullet point summary>",
                    "<Focus on tools, platforms, and impact>"
                ],
                "certifications": [
                    {{
                        "name": "Certification name (if found)",
                        "issuer": "Issuing organization (if available, otherwise null)",
                        "date": "Date obtained (if available, otherwise null)"
                    }}
                ],
                "skills": {{
                    "primary": [
                        "Core technical skill 1",
                        "Core technical skill 2"
                    ],
                    "secondary": [
                        "Additional technical skill 1",
                        "Additional technical skill 2"
                    ]
                }}
            }}

            INSTRUCTIONS:
            1. Extract ONLY information that is explicitly present in the resume text.
            2. Leave fields null if not found.
            3. DO NOT invent values or rephrase company/project details.
            4. Keep sentences short, objective, and presentation-ready.

            Skill Extraction Guidelines:
            - Include **only technical, programming, data, or domain-related skills**.
            - Exclude generic soft skills (e.g., leadership, communication, teamwork, adaptability).
            - Focus on technologies, tools, frameworks, databases, programming languages, cloud services, and methodologies.
            - Use **context** to rank skills:
            * **Primary Skills** → 
                    - Mentioned multiple times
                    - Used in recent roles
                    - Core to current specialization (e.g., Snowflake, Spark, SQL, Airflow)
            * **Secondary Skills** → 
                    - Mentioned only once or briefly
                    - Older technologies or secondary tools
                    - Supporting technologies (e.g., Git, Jira, Jenkins)
            - If a skill looks like a generic noun but refers to a tech tool (e.g., “Hive,” “Control-M”), include it.
            - Maintain consistent capitalization and spelling.

            5. Return ONLY valid JSON (no markdown or explanations).

            Resume Content:
        {text}
        """
    def _clean_json_response(self, text: str) -> str:
        """Clean the JSON response from OpenAI"""
        # Remove code block markers
        text = re.sub(r'```(?:json)?|```', '', text)
    
        # Remove any non-JSON text before the first {
        text = text[text.find('{'):] if '{' in text else text
    
        # Remove any non-JSON text after the last }
        text = text[:text.rfind('}')+1] if '}' in text else text
    
        # Fix common JSON formatting issues
        text = re.sub(r',\s*([}\]])', r'\1', text)  # Remove trailing commas
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)  # Remove control characters
        text = re.sub(r'(?<!\\)"(\w+)":', r'"\1":', text)  # Fix unescaped quotes in keys
    
        # Validate JSON structure
        try:
            # Test if it's valid JSON
            json.loads(text)
            return text.strip()
        except json.JSONDecodeError:
            # If invalid, try to extract just the JSON object
            match = re.search(r'({[\s\S]*})', text)
            if match:
                try:
                    json_str = match.group(1)
                    json.loads(json_str)  # Validate the extracted JSON
                    return json_str.strip()
                except json.JSONDecodeError:
                    raise
            raise   

    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Fallback email extraction"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def _extract_name_from_text(self, text: str) -> Optional[str]:
        """Fallback name extraction"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:5]:  # Check first 5 non-empty lines
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', line):  # Basic name pattern
                return line
        return None

    # Add a curated skill whitelist (extend as needed)
    SKILL_SET = {
        # Languages
        "python", "java", "c++", "c#", "javascript", "typescript", "scala", "go", "rust",
        # Web / Frontend / Backend
        "react", "angular", "vue", "node.js", "express", "django", "flask", "spring",
        # Data / ML
        "sql", "mysql", "postgresql", "mongodb", "spark", "pyspark", "hive", "airflow",
        "tensorflow", "pytorch", "scikit-learn", "keras",
        # Cloud & Infra
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        # BI / Big Data
        "snowflake", "redshift", "hadoop", "kafka",
        # DevOps / Tools
        "git", "github", "gitlab", "jira", "confluence", "rest api", "graphql",
        # Other common tech/tools
        "opencv", "nlp", "numpy", "pandas", "matplotlib", "seaborn", "fastapi",
        "apache", "rabbitmq", "spark streaming", "spark sql"
    }
    SKILL_SET = {s.lower() for s in SKILL_SET}

    def _validate_skills(self, result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Validate and enhance skills extraction using a whitelist + fuzzy matching"""
        raw_skills = result.get("skills", [])
        candidates = []

        if isinstance(raw_skills, dict):
            primary = raw_skills.get("primary", []) or []
            secondary = raw_skills.get("secondary", []) or []
            if isinstance(primary, str):
                candidates += [primary]
            else:
                candidates += list(primary)
            if isinstance(secondary, str):
                candidates += [secondary]
            else:
                candidates += list(secondary)
        elif isinstance(raw_skills, list):
            candidates += raw_skills
        elif isinstance(raw_skills, str):
            candidates.append(raw_skills)

        text_skills = self._match_skills_in_text(original_text)
        candidates += text_skills

        accepted = []
        seen = set()
        for cand in candidates:
            if not isinstance(cand, str):
                continue
            c = cand.strip().lower()
            c = re.sub(r'[^\w\s\.\-#+]', '', c)
            if not c or len(c) < 2:
                continue

            if c in self.SKILL_SET:
                matched = c
            else:
                close = difflib.get_close_matches(c, list(self.SKILL_SET), n=1, cutoff=0.82)
                matched = close[0] if close else None

                if not matched and " " in c:
                    parts = [p for p in c.split() if len(p) > 1]
                    for p in parts:
                        if p in self.SKILL_SET:
                            matched = p
                            break

            if matched and matched not in seen:
                accepted.append(matched)
                seen.add(matched)

        if len(accepted) < 3:
            for s in text_skills:
                sl = s.strip().lower()
                if sl in self.SKILL_SET and sl not in seen:
                    accepted.append(sl)
                    seen.add(sl)
                if len(accepted) >= 6:
                    break

        # Rank by frequency in original_text to determine primary vs secondary
        lower_text = (original_text or "").lower()
        freq = {}
        for skill in accepted:
            # count occurrences (simple approach)
            freq[skill] = lower_text.count(skill)

        # sort by count desc then alphabetically
        sorted_skills = sorted(accepted, key=lambda s: (-freq.get(s, 0), s))

        # choose top N as primary (tunable)
        primary_count = min(5, max(1, len(sorted_skills)//2))
        primary_skills = [s.title() for s in sorted_skills[:primary_count]]
        secondary_skills = [s.title() for s in sorted_skills[primary_count:]]

        # Fallback: if still empty, keep conservative cleaned list
        if not primary_skills and not secondary_skills:
            cleaned = []
            for cand in candidates:
                if isinstance(cand, str):
                    c = cand.strip()
                    if 2 < len(c) < 40 and c.lower() not in {"example", "sample", "test"}:
                        cleaned.append(c.title())
                if len(cleaned) >= 10:
                    break
            primary_skills = cleaned[:5]
            secondary_skills = cleaned[5:10]

        result["skills"] = {"primary": primary_skills, "secondary": secondary_skills}
        return result

    def _match_skills_in_text(self, text: str) -> list:
        """Return list of whitelist skills found in the text (case-insensitive)"""
        found = set()
        if not text:
            return []
        lower_text = text.lower()

        # match exact whitelist tokens (word boundaries) and some multi-word phrases
        for skill in self.SKILL_SET:
            # escape dots and plus signs for regex
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, lower_text):
                found.add(skill)

        # also run a loose split-based check for phrases like "spark sql" or "node.js"
        tokens = re.split(r'[\s,;/()\[\]]+', lower_text)
        for i in range(len(tokens)):
            # check n-grams up to length 3
            for n in (3, 2):
                if i + n <= len(tokens):
                    phrase = " ".join(tokens[i:i+n]).strip()
                    if phrase in self.SKILL_SET:
                        found.add(phrase)

        return sorted(found)
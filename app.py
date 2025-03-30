import streamlit as st
import tempfile
import os
from resume_parser.file_reader import FileReader
from resume_parser.chatgpt_parser import ResumeParser
from resume_parser.utils import TextCleaner


def display_parsed_data(data: dict):
    """Display parsed resume data in Streamlit"""
    st.header("📄 Parsed Resume Information")

    # Personal Information
    with st.expander("👤 Personal Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Name:** {data.get('name', 'Not available')}")
            st.markdown(f"**Email:** {data.get('email', 'Not available')}")
            st.markdown(f"**Phone:** {data.get('phone', 'Not available')}")
        with col2:
            st.markdown(f"**LinkedIn:** {data.get('linkedin', 'Not available')}")
            if 'address' in data:
                st.markdown(f"**Address:** {data['address']}")

    # Experience
    if data.get('experience'):
        with st.expander("💼 Work Experience"):
            for exp in data['experience']:
                st.subheader(f"{exp.get('position', 'Unknown Position')}")
                st.markdown(f"**Company:** {exp.get('company', 'Unknown company')}")
                st.markdown(f"**Duration:** {exp.get('duration', 'Not specified')}")
                if exp.get('responsibilities'):
                    st.write("**Responsibilities:**")
                    for resp in exp['responsibilities']:
                        st.markdown(f"- {resp}")
                st.divider()

    # Education
    if data.get('education'):
        with st.expander("🎓 Education"):
            for edu in data['education']:
                st.markdown(f"**{edu.get('degree', 'Degree')}**")
                st.markdown(f"{edu.get('institution', 'Unknown institution')}")
                st.markdown(f"*{edu.get('field', '')}* ({edu.get('year', '')})")
                st.divider()

    # Skills & Certifications
    col1, col2 = st.columns(2)
    with col1:
        if data.get('skills'):
            with st.expander("🛠 Skills"):
                for skill in data['skills']:
                    st.success(f"• {skill}")

    with col2:
        if data.get('certifications'):
            with st.expander("📜 Certifications"):
                for cert in data['certifications']:
                    st.info(f"• {cert}")

    # Projects
    if data.get('projects'):
        with st.expander("🚀 Projects"):
            for project in data['projects']:
                st.markdown(f"**{project.get('name', 'Unnamed project')}**")
                st.markdown(f"{project.get('description', 'No description')}")
                st.divider()


def show_error(error_data: dict):
    """Display detailed error information"""
    st.error("❌ Resume Parsing Failed")

    st.write(f"**Error:** {error_data.get('error', 'Unknown error')}")

    if 'details' in error_data:
        st.write(f"**Details:** {error_data['details']}")

    if 'suggestion' in error_data:
        st.info(f"💡 Suggestion: {error_data['suggestion']}")

    # Show debug info if available
    debug_info = {
        'type': error_data.get('type'),
        'code': error_data.get('code'),
        'min_length': error_data.get('min_length'),
        'received': error_data.get('received')
    }
    debug_info = {k: v for k, v in debug_info.items() if v is not None}

    if debug_info:
        with st.expander("Technical Details"):
            st.json(debug_info)

    if 'content_sample' in error_data:
        with st.expander("View AI Response Sample"):
            st.text(error_data['content_sample'])

    if 'raw_text_sample' in error_data:
        with st.expander("View Resume Text Sample"):
            st.text(error_data['raw_text_sample'])

    st.markdown("""
    **Common Solutions:**
    1. Try a simpler resume format (PDF works best)
    2. Ensure the resume contains clear contact information
    3. Check the file isn't image-based (scanned resumes won't work)
    4. Try removing sensitive information if redacted
    """)


def main():
    st.set_page_config(
        page_title="AI Resume Parser",
        page_icon="📄",
        layout="wide"
    )

    st.title("AI-Powered Resume Parser")
    st.markdown("Upload a resume to extract structured information automatically")

    # Initialize parser (with error handling)
    try:
        parser = ResumeParser()
    except Exception as e:
        st.error(f"Failed to initialize parser: {str(e)}")
        st.stop()

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        try:
            with st.spinner("🔍 Reading resume..."):
                # Read file
                raw_text = FileReader.read_file(tmp_path)
                if not raw_text:
                    st.error("Failed to read file content")
                    return
                print(raw_text)
                # Clean text
                cleaned_text = TextCleaner.clean_text(raw_text)
                # Validate text length
                if len(cleaned_text) < 100:
                    show_error({
                        "error": "Resume text too short",
                        "details": "The extracted text appears incomplete",
                        "min_length": 100,
                        "received": len(cleaned_text),
                        "raw_text_sample": cleaned_text
                    })
                    return

                # Parse with AI
                with st.spinner("🤖 Analyzing content..."):
                    result = parser.parse_resume(cleaned_text)
                    print("dddddddddddddd")
                    print(result)

                # Handle results
                if "error" in result:
                    show_error(result)
                else:
                    st.balloons()
                    display_parsed_data(result)
                    st.success("✅ Resume parsed successfully!")

                    # Show raw JSON
                    with st.expander("View Raw JSON Output"):
                        st.json(result)

        except Exception as e:
            show_error({
                "error": "Unexpected processing error",
                "details": str(e),
                "type": type(e).__name__,
                "suggestion": "Try again or contact support"
            })

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    main()
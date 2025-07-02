import streamlit as st
import pytesseract
import pdf2image
from PyPDF2 import PdfReader
import re
from PIL import Image
import tempfile

# Optional: set this if tesseract is not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="Exam Score Analyzer", layout="centered")
st.title("📊 Multi-Exam Score Analyzer (UGC NET / CUET UG)")

st.markdown("""
Upload your **Response Sheet PDF** and **Answer Key PDF**  
✅ Supports UGC NET & CUET UG  
✅ Works with text & image-based answer keys  
""")

response_pdf = st.file_uploader("Upload Response Sheet PDF", type="pdf")
answer_pdf = st.file_uploader("Upload Answer Key PDF (text or scanned)", type="pdf")

# === Utilities ===

def extract_text_from_pdf(pdf_file):
    """Extract raw text from selectable text PDF."""
    try:
        reader = PdfReader(pdf_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except:
        return ""

def extract_text_from_image_pdf(pdf_file):
    """OCR fallback for image-based PDFs."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    images = pdf2image.convert_from_path(tmp_path, dpi=300)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text

def parse_response_sheet(text):
    """
    Parses response sheet and returns {QuestionID: ChosenOption}.
    Handles variable-length Question IDs.
    """
    pattern = r"Question ID\s*:\s*(\d+).*?Chosen Option\s*:\s*(\d)"
    return {qid: opt for qid, opt in re.findall(pattern, text, re.DOTALL)}

def parse_answer_key(text):
    """
    Parses answer key (CUET/UGC). Supports multiple correct options like '1,4'.
    Handles variable-length Question IDs.
    """
    pattern = r"(\d+)\s+([1234](?:,[1234])?)"
    answer_dict = {}
    for qid, key in re.findall(pattern, text):
        options = [opt.strip() for opt in key.split(',')]
        answer_dict[qid] = options
    return answer_dict

def calculate_score(response, answer_key):
    correct = incorrect = dropped = 0
    total = len(answer_key)

    for qid, correct_opts in answer_key.items():
        chosen = response.get(qid)
        if correct_opts == ["DROPPED"]:
            dropped += 1
        elif chosen is None:
            continue
        elif chosen in correct_opts:
            correct += 1
        else:
            incorrect += 1

    unattempted = total - (correct + incorrect + dropped)
    score = correct * 2
    return {
        "Total Questions": total,
        "Attempted": correct + incorrect,
        "Correct": correct,
        "Incorrect": incorrect,
        "Unattempted": unattempted,
        "Dropped": dropped,
        "Final Score": score
    }

# === Main Logic ===

if response_pdf and answer_pdf:
    with st.spinner("Processing response sheet..."):
        response_text = extract_text_from_pdf(response_pdf)
        response_data = parse_response_sheet(response_text)

    with st.spinner("Processing answer key..."):
        answer_text = extract_text_from_pdf(answer_pdf)
        if not answer_text.strip():
            answer_text = extract_text_from_image_pdf(answer_pdf)
        answer_data = parse_answer_key(answer_text)

    with st.spinner("Calculating score..."):
        result = calculate_score(response_data, answer_data)

    st.success("✅ Score calculated successfully!")
    for k, v in result.items():
        st.write(f"**{k}**: {v}")

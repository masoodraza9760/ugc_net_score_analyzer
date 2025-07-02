import streamlit as st
import PyPDF2
import re

st.title("Exam Score Analyzer (CUET / UGC NET / Any Exam)")

# --- PDF Text Extractor ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

# --- General Response Parser ---
def parse_response_sheet(text, qid_label="Question ID", opt_label="Chosen Option"):
    pattern = fr"{qid_label}\s*[:\-]?\s*(\d+).*?{opt_label}\s*[:\-]?\s*([1-9])"
    return {qid: opt for qid, opt in re.findall(pattern, text, re.DOTALL)}

# --- General Answer Key Parser ---
def parse_answer_key(text, key_label="Key", allow_dropped=True):
    pattern1 = r"(\d+)[^\d\n]+([1234D])" if allow_dropped else r"(\d+)[^\d\n]+([1234])"
    pattern2 = r"Question ID\s*[:\-]?\s*(\d+).*?" + key_label + r"\s*[:\-]?\s*([1234D])"
    
    matches = re.findall(pattern1, text)
    matches += re.findall(pattern2, text, re.DOTALL)

    answer_dict = {}
    for qid, opt in matches:
        if not allow_dropped and opt == 'D':
            continue
        if opt in ['1', '2', '3', '4']:
            answer_dict[qid] = opt
    return answer_dict

# --- Score Calculator ---
def calculate_score(response_dict, answer_dict, marks_per_correct=2, marks_per_wrong=0):
    correct = incorrect = dropped = unattempted = 0

    for qid, correct_opt in answer_dict.items():
        chosen_opt = response_dict.get(qid)

        if correct_opt == 'D':
            dropped += 1
        elif chosen_opt is None:
            unattempted += 1
        elif chosen_opt == correct_opt:
            correct += 1
        else:
            incorrect += 1

    score = correct * marks_per_correct + incorrect * marks_per_wrong

    return {
        "Total Questions": len(answer_dict),
        "Attempted": correct + incorrect,
        "Correct": correct,
        "Incorrect": incorrect,
        "Unattempted": unattempted,
        "Dropped": dropped,
        "Final Score": score
    }

# --- Upload UI ---
response_pdf = st.file_uploader("Upload Response Sheet PDF", type="pdf")
answer_pdf = st.file_uploader("Upload Answer Key PDF", type="pdf")

# --- Run Logic ---
if response_pdf and answer_pdf:
    response_text = extract_text_from_pdf(response_pdf)
    answer_text = extract_text_from_pdf(answer_pdf)

    # Flexible parsing
    response_data = parse_response_sheet(response_text, qid_label="Question ID", opt_label="Chosen Option")
    answer_key_data = parse_answer_key(answer_text, key_label="Key", allow_dropped=True)

    result = calculate_score(response_data, answer_key_data)

    st.success("Score Calculation Complete!")
    for key, value in result.items():
        st.write(f"**{key}**: {value}")

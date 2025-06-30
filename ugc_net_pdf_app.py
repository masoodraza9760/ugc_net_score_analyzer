import streamlit as st
import PyPDF2
import re

st.title("UGC NET Score Analyzer (PDF Upload)")

# --- Functions ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    return "\n".join(page.extract_text() for page in reader.pages)

def parse_response_sheet(text):
    pattern = r"Question ID\s*:\s*(\d+).*?Chosen Option\s*:\s*(\d)"
    return {qid: opt for qid, opt in re.findall(pattern, text, re.DOTALL)}

def parse_answer_key(text):
    pattern = r"(\d{10})\s+([1234D])"
    return {qid: opt for qid, opt in re.findall(pattern, text)}

def calculate_score(response_dict, answer_dict):
    correct = incorrect = dropped = 0
    total_questions = len(answer_dict)

    for qid, correct_option in answer_dict.items():
        chosen = response_dict.get(qid)
        if correct_option.upper() == 'D':
            dropped += 1
        elif chosen is None:
            continue
        elif chosen == correct_option:
            correct += 1
        else:
            incorrect += 1

    unattempted = total_questions - (correct + incorrect + dropped)
    score = correct * 2

    return {
        "Total Questions": total_questions,
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

    response_data = parse_response_sheet(response_text)
    answer_key_data = parse_answer_key(answer_text)

    result = calculate_score(response_data, answer_key_data)

    st.success("Score Calculation Complete!")
    for key, value in result.items():
        st.write(f"**{key}**: {value}")

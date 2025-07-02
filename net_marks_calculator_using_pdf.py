import re
import PyPDF2

def extract_text_from_pdf(path):
    """Extracts text from all pages of a PDF file"""
    with open(path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join(page.extract_text() or '' for page in reader.pages)

def parse_response_sheet(text, qid_label="Question ID", opt_label="Chosen Option"):
    """
    Parses response sheet into {question_id: chosen_option}.
    """
    pattern = fr"{qid_label}\s*[:\-]?\s*(\d+).*?{opt_label}\s*[:\-]?\s*([1-9])"
    return {qid: opt for qid, opt in re.findall(pattern, text, re.DOTALL)}

def parse_answer_key(text, key_label="Key", allow_dropped=True):
    """
    Parses answer key into {question_id: correct_option}.
    Supports:
      - Formats like: 226895702123 4
      - Or: Question ID: 226895702123 Key: 4
    """
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

def calculate_marks(response_dict, answer_key_dict, marks_per_correct=2, marks_per_wrong=0):
    correct = incorrect = dropped = unattempted = 0

    for qid, correct_opt in answer_key_dict.items():
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
        "Total Questions": len(answer_key_dict),
        "Attempted": correct + incorrect,
        "Correct": correct,
        "Incorrect": incorrect,
        "Unattempted": unattempted,
        "Dropped": dropped,
        "Final Score": score
    }

def print_result_summary(result_dict, title="Exam Score Summary"):
    print(f"\n{title}")
    print("-" * len(title))
    for k, v in result_dict.items():
        print(f"{k}: {v}")

# ========== USAGE EXAMPLE ==========
# Replace with actual file names
response_pdf = "resp.pdf"
answer_pdf = "answ.pdf"

# Extract text
response_text = extract_text_from_pdf(response_pdf)
answer_key_text = extract_text_from_pdf(answer_pdf)

# Parse
response_data = parse_response_sheet(response_text, qid_label="Question ID", opt_label="Chosen Option")
answer_key_data = parse_answer_key(answer_key_text, key_label="Key", allow_dropped=True)

# Compute and print
result = calculate_marks(response_data, answer_key_data, marks_per_correct=2, marks_per_wrong=0)
print_result_summary(result, title="CUET / UGC NET Scorecard")

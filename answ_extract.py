import re
import csv
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_answer_key(text):
    """
    Extracts (Question ID, Correct Option) pairs, skips dropped questions (optional)
    """
    pattern = r"(\d{10})\s+([1234D])"
    matches = re.findall(pattern, text)
    return matches  # Includes 'D' for dropped; filter if needed

def save_to_csv(data, filename='answer_key.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Question ID', 'Correct Option'])
        writer.writerows(data)
    print(f"CSV saved as {filename}")

# === USAGE ===
answer_pdf = "answ.PDF"

text = extract_text_from_pdf(answer_pdf)
answer_data = extract_answer_key(text)
save_to_csv(answer_data)

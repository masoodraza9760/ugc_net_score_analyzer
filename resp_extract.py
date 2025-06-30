import re
import csv
import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_qid_and_choice(text):
    """
    Extracts (Question ID, Chosen Option) pairs from response sheet text
    """
    pattern = r"Question ID\s*:\s*(\d+).*?Chosen Option\s*:\s*(\d)"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def save_to_csv(data, filename='response_data.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Question ID', 'Chosen Option'])
        writer.writerows(data)
    print(f"CSV saved as {filename}")

# === USAGE ===
response_pdf = "resp.pdf"

text = extract_text_from_pdf(response_pdf)
response_data = extract_qid_and_choice(text)
save_to_csv(response_data)

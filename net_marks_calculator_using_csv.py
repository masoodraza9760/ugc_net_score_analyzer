import csv

def load_csv_as_dict(filepath):
    """
    Loads a CSV into a dictionary with format {Question ID: Option}
    """
    data = {}
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row['Question ID'].strip()] = row[list(row.keys())[1]].strip()
    return data

def calculate_marks(response_data, answer_key_data):
    correct = incorrect = dropped = 0
    total_questions = len(answer_key_data)
    attempted = len(response_data)

    for qid, correct_option in answer_key_data.items():
        chosen_option = response_data.get(qid)

        if correct_option.upper() == 'D':
            dropped += 1
        elif chosen_option is None:
            pass  # Could count as unattempted if needed
        elif chosen_option == correct_option:
            correct += 1
        else:
            incorrect += 1

    unattempted = total_questions - (correct + incorrect + dropped)
    score = correct * 2

    return {
        "Total Questions in Answer Key": total_questions,
        "Attempted Questions": attempted,
        "Correct Answers": correct,
        "Incorrect Answers": incorrect,
        "Unattempted": unattempted,
        "Dropped Questions": dropped,
        "Final Score": score
    }

# === USAGE ===
response_csv = 'response_data.csv'
answer_key_csv = 'answer_key.csv'

response_dict = load_csv_as_dict(response_csv)
answer_key_dict = load_csv_as_dict(answer_key_csv)

result = calculate_marks(response_dict, answer_key_dict)

# Output
print("\nUGC NET Marks Report")
print("-" * 30)
for k, v in result.items():
    print(f"{k}: {v}")

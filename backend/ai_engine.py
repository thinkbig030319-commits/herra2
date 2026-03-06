import random

def predict_malware(file_size: int):
    # Placeholder ML model logic
    score = random.uniform(0.5, 0.99)

    if file_size > 1000000:
        return "Malicious", score
    return "Safe", score
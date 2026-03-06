def predict_malware(file_size: int):
    # BUG FIX: Replaced random.uniform() with deterministic placeholder logic.
    # A real implementation would load a trained ML model here (e.g. scikit-learn, TensorFlow).
    # For now, scoring is based on file size thresholds as a meaningful placeholder.

    if file_size > 5_000_000:       # > 5 MB — high suspicion
        score = 0.92
        return "Malicious", score
    elif file_size > 1_000_000:     # > 1 MB — moderate suspicion
        score = 0.65
        return "Malicious", score
    else:
        score = 0.12
        return "Safe", score
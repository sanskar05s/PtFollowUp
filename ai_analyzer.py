def analyze_symptoms(message):

    message = message.lower()

    high_risk_keywords = [
        "chest pain",
        "breathing difficulty",
        "heavy bleeding",
        "unconscious",
        "high fever",
        "severe pain"
    ]

    for keyword in high_risk_keywords:
        if keyword in message:
            return {
                "risk_level": "High Risk",
                "recovery_score": 2
            }

    mild_keywords = [
        "headache",
        "mild pain",
        "nausea",
        "dizziness",
        "tired",
        "fever"
    ]

    for keyword in mild_keywords:
        if keyword in message:
            return {
                "risk_level": "Mild Concern",
                "recovery_score": 6
            }

    return {
        "risk_level": "Normal",
        "recovery_score": 9
    }
def check_suspicious(row):
    reasons = []
    risk_score = 0

    amount = row["amount"]
    location = str(row["location"]).lower()
    time = str(row["time"])
    transaction_type = str(row["transaction_type"])

    hour = int(time.split(":")[0])

    if amount > 50000:
        risk_score += 40
        reasons.append("High amount transaction")

    if hour >= 0 and hour <= 5:
        risk_score += 25
        reasons.append("Transaction at unusual night time")

    if location == "unknown":
        risk_score += 25
        reasons.append("Unknown location")

    if transaction_type in ["Online", "Transfer"] and amount > 30000:
        risk_score += 20
        reasons.append("High-value online/transfer transaction")

    if risk_score >= 70:
        risk_level = "High Risk"
    elif risk_score >= 40:
        risk_level = "Medium Risk"
    else:
        risk_level = "Low Risk"

    if len(reasons) == 0:
        reasons.append("Normal transaction")

    return risk_score, risk_level, ", ".join(reasons)
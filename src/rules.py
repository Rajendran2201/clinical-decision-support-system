def apply_clinical_rules(data):
    """
    Advanced multimodal rule engine combining vitals, symptoms, and imaging findings.
    Input `data` can be from database or manual entry.
    """
    alerts = []
    recommendations = []
    
    # 1. Image-Based Flags (from imaging.py results)
    image_finding = data.get('image_analysis', {}).get('finding', 'None')
    image_conf = data.get('image_analysis', {}).get('confidence', 0)
    
    # 2. Vitals
    temp = data.get('Temperature', 37.0)
    spO2 = data.get('SpO2', 98)
    sys_bp = data.get('SystolicBloodPressure', 120)
    heart_rate = data.get('Heartrate', 70)
    
    # 3. Symptoms (Boolean flags)
    has_cough = data.get('Cough', False)
    has_dyspnea = data.get('Dyspnea', False)
    has_fatigue = data.get('Fatigue', False)

    # --- Pneumonia Logic (Multi-factor) ---
    pneumonia_score = 0
    if image_finding == 'Infiltration/Opacity': pneumonia_score += 3
    if temp > 38.0: pneumonia_score += 2
    if has_cough: pneumonia_score += 1
    if spO2 < 94: pneumonia_score += 2

    if pneumonia_score >= 5:
        alerts.append("CRITICAL: High clinical suspicion of Pneumonia")
        recommendations.append("Initiate empiric antibiotics according to hospital protocol.")
        recommendations.append("Consider urgent Chest CT for further characterization.")
    elif pneumonia_score >= 3:
        alerts.append("MODERATE: Potential Respiratory Infection")
        recommendations.append("Recommend daily monitoring of temperature and SpO2.")
        recommendations.append("Follow-up X-ray suggested in 48-72 hours if symptoms persist.")

    # --- Cardiovascular Alert ---
    if sys_bp > 160 or heart_rate > 110:
        alerts.append("ALERT: Hypertensive/Tachycardic Crisis Profile")
        recommendations.append("Urgent cardiovascular assessment required.")
        recommendations.append("Rule out acute stress or cardiac event.")

    # --- Respiratory Distress ---
    if spO2 < 92:
        alerts.append("URGENT: Hypoxemic Respiratory Failure Risk")
        recommendations.append("Administer supplemental oxygen (target SpO2 >94%).")
        recommendations.append("Evaluate for potential hospitalization.")

    # Severity Mapping
    max_score = pneumonia_score + (1 if sys_bp > 140 else 0) + (1 if spO2 < 95 else 0)
    
    if max_score >= 6:
        severity = "High"
        summary = "Patient exhibits signs of severe acute illness. Immediate intervention required."
    elif max_score >= 3:
        severity = "Moderate"
        summary = "Patient exhibits stable but significant symptoms. Close monitoring and outpatient follow-up required."
    else:
        severity = "Low"
        summary = "Patient is clinically stable. No immediate acute concerns identified."

    if not alerts:
        alerts.append("No immediate clinical triggers. Continue routine monitoring.")
        recommendations.append("Maintain health maintenance and routine screenings.")
        
    return {
        "severity": severity,
        "summary": summary,
        "alerts": alerts,
        "recommendations": list(set(recommendations))
    }

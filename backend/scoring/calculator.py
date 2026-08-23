from typing import List, Dict, Any

SEVERITY_WEIGHTS = {
    "Critical": 30.0,
    "High": 18.0,
    "Medium": 10.0,
    "Low": 5.0
}

def calculate_manipulation_index(findings: List[Dict[str, Any]], flow_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Computes the composite Manipulation Index (0-100), letter grade,
    regulatory risk level, and statistical summary.
    """
    if flow_context is None:
        flow_context = {}
        
    base_score = 0.0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    category_counts = {}
    
    for f in findings:
        severity = f.get("severity", "Medium")
        category = f.get("category", "General")
        
        category_counts[category] = category_counts.get(category, 0) + 1
        
        if severity == "Critical":
            critical_count += 1
            base_score += SEVERITY_WEIGHTS["Critical"]
        elif severity == "High":
            high_count += 1
            base_score += SEVERITY_WEIGHTS["High"]
        elif severity == "Medium":
            medium_count += 1
            base_score += SEVERITY_WEIGHTS["Medium"]
        else:
            low_count += 1
            base_score += SEVERITY_WEIGHTS["Low"]

    # Friction / Multiplier bonus
    asymmetry_ratio = flow_context.get("asymmetry_ratio", 1.0)
    if asymmetry_ratio > 2.0:
        base_score *= 1.15
        
    # Cap score strictly between 0 and 100
    final_score = min(100.0, max(0.0, round(base_score, 1)))
    
    # Calculate Grade
    if final_score <= 15:
        grade = "A+"
        classification = "Clean / Ethical"
        ftc_risk = "Compliant"
    elif final_score <= 30:
        grade = "B"
        classification = "Dubious / Soft Nudge"
        ftc_risk = "Low"
    elif final_score <= 65:
        grade = "D"
        classification = "Predatory / Coercive"
        ftc_risk = "High"
    else:
        grade = "F"
        classification = "Egregious Offender"
        ftc_risk = "Critical Violation Liability"
        
    return {
        "manipulation_index": final_score,
        "grade": grade,
        "classification": classification,
        "ftc_risk_level": ftc_risk,
        "critical_count": critical_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "total_findings": len(findings),
        "category_distribution": category_counts
    }


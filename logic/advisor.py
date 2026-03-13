def calculate_recommendation(credits, intensity):
    # Base rule: 2 hours per credit
    multiplier = 2
    
    if intensity == "STEM":
        multiplier = 3
    elif intensity == "Finals Week":
        multiplier = 4
    elif intensity == "Light":
        multiplier = 1.5

    suggested_hours = credits * multiplier
    
    # Peer Comparison Text
    if suggested_hours <= 15:
        bracket = "Maintaining Pace"
    elif suggested_hours <= 30:
        bracket = "Competitive Edge"
    else:
        bracket = "Dean's List Intensity"
        
    return suggested_hours, bracket
def bucket_rouge(score):
    """
    Bucket the Rouge Score into High/Medium/Low/Unknown
    """
    try:
        val = float(score)
    except ValueError:
        return "Unknown"
    if val >= 0.75:
        return "High"
    elif val >= 0.50:
        return "Medium"
    else:
        return "Low"

def bucket_generic(value, unique_vals):
    """
    For numeric values with more than 2 unique values, bucket them as:
      High (>=0.75), Medium (>=0.50), Low (<0.50).
    If binary or non-numeric, return as string.
    """
    try:
        v = float(value)
    except:
        return str(value)
    if len(unique_vals) <= 2:
        return str(int(v))  # e.g. "0" or "1"
    else:
        if v >= 0.75:
            return "High"
        elif v >= 0.50:
            return "Medium"
        else:
            return "Low"
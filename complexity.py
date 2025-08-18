import pandas as pd
import numpy as np

# Load your file
df = pd.read_csv("data.csv")

# Mapping function
def map_complexity(text):
    text = str(text).lower()
    if "very high" in text:
        return "Very Complex"
    elif "high" in text:
        return "Complex"
    elif "complex" in text:
        return  "Complex"
    elif "moderate to complex" in text:
        return  "Complex" # midpoint rounded
    elif "moderate" in text:
        return "Moderate"
    elif "low" in text:
        return "Low"
    else:
        return np.nan

# Apply mapping
df["Level of Complexity"] = df["Application Complexity"].apply(map_complexity)


# Save new CSV
df.to_csv("grants_with_complexity.csv", index=False)
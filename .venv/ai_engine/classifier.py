
def classify_disaster(description):

    text = description.lower()

    if any(word in text for word in ["flood", "water rising", "heavy rain", "inundation"]):
        return "Flood"

    elif any(word in text for word in ["fire", "smoke", "burning", "flames"]):
        return "Fire"

    elif any(word in text for word in ["cyclone", "strong wind", "storm"]):
        return "Cyclone"

    elif any(word in text for word in ["earthquake", "tremor", "shaking"]):
        return "Earthquake"

    else:
        return "Unknown"


# Test the function
if __name__ == "__main__":
      report = input("Enter the emergency description: ")
      
      result = classify_disaster(report)

      print("Detected Disaster:", result)

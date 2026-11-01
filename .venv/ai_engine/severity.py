
def assess_severity(people_affected, people_trapped, situation):

    score = 0

    # People affected
    if people_affected >= 50:
        score += 30
    elif people_affected >= 20:
        score += 20
    elif people_affected >= 5:
        score += 10

    # People trapped
    if people_trapped:
        score += 40

    # Situation
    situation = situation.lower()

    if any(word in situation for word in [
        "trapped", "life threatening", "building collapse"
    ]):
        score += 30

    elif any(word in situation for word in [
        "water rising", "heavy smoke", "strong wind"
    ]):
        score += 20

    elif any(word in situation for word in [
        "minor", "small", "under control"
    ]):
        score += 5

    # Maximum score
    score = min(score, 100)

    # Severity result
    if score >= 75:
        severity = "Critical"

    elif score >= 50:
        severity = "High"

    elif score >= 25:
        severity = "Medium"

    else:
        severity = "Low"

    return score, severity


# Get user input
if __name__ == "__main__":

    people = int(input("Enter people affected: "))

    trapped_input = input("Are people trapped? (yes/no): ")
    trapped = trapped_input.lower() == "yes"

    situation = input("Describe the situation: ")

    score, severity = assess_severity(
        people, trapped, situation
    )

    print("Severity Score:", score)
    print("Severity Level:", severity)
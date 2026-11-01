def calculate_priority(people_affected, people_trapped, severity):

    priority_score = 0

    # People affected
    if people_affected >= 50:
        priority_score += 30

    elif people_affected >= 20:
        priority_score += 20

    elif people_affected >= 5:
        priority_score += 10

    # People trapped
    if people_trapped:
        priority_score += 40

    # Severity
    if severity == "Critical":
        priority_score += 30

    elif severity == "High":
        priority_score += 20

    elif severity == "Medium":
        priority_score += 10

    # Priority result
    if priority_score >= 70:
        priority = "Urgent"

    elif priority_score >= 40:
        priority = "High"

    elif priority_score >= 20:
        priority = "Medium"

    else:
        priority = "Low"

    return priority_score, priority
# Get user inputs
if __name__ == "__main__":

    people = int(input("Enter people affected: "))

    trapped_input = input("Are people trapped? (yes/no): ")
    trapped = trapped_input.lower() == "yes"

    severity = input("Enter severity (Low/Medium/High/Critical): ")

    score, priority = calculate_priority(
        people, trapped, severity
    )

    print("Priority Score:", score)
    print("Priority Level:", priority)
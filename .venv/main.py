from ai_engine.classifier import classify_disaster

from ai_engine.severity import assess_severity

from ai_engine.priority import calculate_priority

print("===== RESQ AI =====")

report = input("Describe the disaster: ")

disaster = classify_disaster(report)

print("Detected Disaster:", disaster)

people = int(input("Enter number of people affected: "))

trapped_input = input("Are people trapped? (yes/no): ")

trapped = trapped_input.lower() == "yes"

severity_score, severity_level = assess_severity(
    people, trapped, report
)
print("Severity Score:", severity_score)
print("Severity Level:", severity_level)

priority_score, priority_level = calculate_priority(
    people, trapped, severity_level
)

print("Priority Score:", priority_score)
print("Priority Level:", priority_level)
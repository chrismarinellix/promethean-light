"""Extract key Hayden salary information from search results"""

import re

# Read the search results file
with open('hayden_search_results.txt', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("="*100)
print("HAYDEN BRUNJES - SALARY AND COMPENSATION SUMMARY")
print("="*100)

# Extract key information
print("\n1. CURRENT SALARY INFORMATION:")
print("-" * 100)

# Find salary entries
salary_patterns = [
    r'Hayden Brunjes.*?SALARY\s+(\d+)\s+AUD',
    r'Hayden.*?\$95,?000',
    r'470434.*?Hayden Brunjes.*?95000',
]

for pattern in salary_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
    if matches:
        print(f"Pattern '{pattern}': {matches[:3]}")

# Key facts
print("\nKEY SALARY FACTS:")
print("- Employee ID: 470434")
print("- Current Position: Power Systems Engineer (POS_1046)")
print("- Current Salary: $95,000 AUD (as of July 1, 2025)")
print("- Valid From: 7/1/2025")
print("- Valid To: 12/31/9999")

print("\n2. PROPOSED SALARY INCREASE:")
print("-" * 100)

# Find increase discussions
if "Hayden	$95,000	$108,000	+$13,000" in content or "Hayden: NEXT 1-2 WEEKS" in content:
    print("PROPOSED INCREASE FOUND:")
    print("- Current: $95,000 AUD")
    print("- Proposed: $108,000 AUD")
    print("- Increase: +$13,000 AUD (+13.7%)")
    print("- Timeline: Next 1-2 weeks (can wait a bit)")
    print("- Status: REVIEW NEEDED ★")

print("\n3. MANAGER NOTES AND CONTEXT:")
print("-" * 100)

# Extract manager notes
manager_notes = [
    "i loike hayden and ajith, i get on really well with them, they are both under paid",
    "i was thinking just asking them on teams how much they want to get paid",
    "Do this for Ajith THIS WEEK. Hayden can wait a bit, but don't wait too long.",
    "Hayden: NEXT 1-2 WEEKS",
]

for note in manager_notes:
    if note.lower() in content.lower():
        print(f"- {note}")

print("\n4. TENURE AND EXPERIENCE:")
print("-" * 100)
print("- Tenure: Longer tenure (~2023-2024)")
print("- Start Date: Approximately 2023")
print("- Notes: 'hayden longer, khadija longer' (compared to recent hires)")

print("\n5. COMPARISONS WITH OTHER JUNIOR ENGINEERS:")
print("-" * 100)

# Extract junior engineer comparisons
junior_engineers = [
    ("Hayden Brunjes", "$95,000 AUD", "Power Systems Engineer"),
    ("Dominic Moncada", "$140,000 AUD", "Power Systems Engineer"),
    ("Khadija Kobra", "$130,000 AUD", "Power Systems Engineer"),
]

print("\nJunior/Mid-Level Power Systems Engineers:")
for name, salary, position in junior_engineers:
    print(f"- {name:25s} | {salary:15s} | {position}")

print("\nGAP ANALYSIS:")
print(f"- Hayden ($95k) vs Dominic ($140k): -$45,000 AUD (-32%)")
print(f"- Hayden ($95k) vs Khadija ($130k): -$35,000 AUD (-27%)")
print(f"- After proposed increase ($108k) vs Khadija ($130k): -$22,000 AUD (-17%)")

print("\n6. SCHEDULED DISCUSSION:")
print("-" * 100)
if "10:00 AM: Hayden (20 min) - Development progress, salary discussion" in content:
    print("- Meeting scheduled: 10:00 AM (20 min)")
    print("- Topic: Development progress, salary discussion")
    print("- Date: November 14, 2025")

print("\n7. MARKET POSITIONING:")
print("-" * 100)
print("- Current salary ($95k) is significantly below peers in same role")
print("- Proposed increase to $108k still below mid-level engineers ($130k-$140k)")
print("- Classified as UNDERPAID by management")
print("- Recommendation: Review and increase needed")

print("\n8. CAREER PROGRESSION NOTES:")
print("-" * 100)
print("- Current: Power Systems Engineer (junior level)")
print("- Comparison roles:")
print("  - Senior Power System Engineer: $160,000+ AUD")
print("  - Lead Power Systems Engineer: $170,000-$185,000 AUD")
print("- Progression path: Junior -> Mid-level -> Senior -> Lead")

print("\n" + "="*100)
print("END OF SUMMARY")
print("="*100)

# Save summary to file
with open('hayden_salary_summary.txt', 'w', encoding='utf-8') as f:
    f.write("HAYDEN BRUNJES - SALARY SUMMARY\n")
    f.write("="*100 + "\n\n")
    f.write("CURRENT SITUATION:\n")
    f.write("- Position: Power Systems Engineer\n")
    f.write("- Current Salary: $95,000 AUD\n")
    f.write("- Status: UNDERPAID - Review Needed\n\n")
    f.write("PROPOSED ACTION:\n")
    f.write("- Increase to: $108,000 AUD (+$13,000 / +13.7%)\n")
    f.write("- Timeline: Next 1-2 weeks\n")
    f.write("- Manager note: 'both under paid'\n\n")
    f.write("CONTEXT:\n")
    f.write("- Peer comparison: Still below Khadija ($130k) and Dominic ($140k)\n")
    f.write("- Tenure: ~2 years (longer tenure member)\n")
    f.write("- Relationship: Manager gets on 'really well' with Hayden\n")

print("\nSummary saved to: hayden_salary_summary.txt")

from mydata.summaries import get_australia_staff_summary, get_india_staff_summary
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

aus_data = get_australia_staff_summary()
india_data = get_india_staff_summary()

# Separate staff
aus_with_bonus = [s for s in aus_data['staff'] if s.get('retention_bonus')]
aus_need_review = [s for s in aus_data['staff'] if not s.get('retention_bonus')]
india_with_bonus = [s for s in india_data['staff'] if s.get('retention_bonus') != "None"]
india_need_review = [s for s in india_data['staff'] if s.get('retention_bonus') == "None"]

print("\n" + "="*120)
print(" TEAM SALARY REVIEW STATUS ".center(120, "="))
print("="*120)
print(f"\n  Total: 20 team members  |  With Recent Pay Rises: 8  |  Need Review: 12 (6 HIGH PRIORITY)")
print("="*120)

# TABLE 1: STAFF WITH RECENT PAY RISES
print("\n[1] STAFF WITH RECENT PAY RISES (Retention Bonuses - 8 staff)")
print("-"*120)
print(f"{'Reg':<5} {'ID':<10} {'Name':<25} {'Position/Level':<28} {'Base':<14} {'Total+Bonus':<14} {'Expires':<11} {'Status':<10}")
print("-"*120)

for s in aus_with_bonus:
    status = "RESIGNED" if "RESIGNED" in s['position'] else "Active"
    print(f"{'AUS':<5} {s['id']:<10} {s['name']:<25} {s['position'].replace(' [RESIGNED]', '')[:27]:<28} "
          f"{s['salary']:<14} {s.get('total', s['salary']):<14} {s.get('expires', '-'):<11} {status:<10}")

for s in india_with_bonus:
    print(f"{'IND':<5} {s['id']:<10} {s['name']:<25} {s['level']:<28} "
          f"{s['ctc_aud']:<14} {s['total_with_bonus_aud']:<14} {s.get('bonus_until', '-'):<11} {'Active':<10}")

# TABLE 2: HIGH PRIORITY REVIEWS
print("\n[2] HIGH PRIORITY - Staff Requiring IMMEDIATE Review (6 staff)")
print("-"*120)
print(f"{'Reg':<5} {'ID':<10} {'Name':<25} {'Position/Level':<28} {'Salary':<14} {'Key Issue':<35}")
print("-"*120)

high_aus = [s for s in aus_need_review if int(s['salary'].replace('$', '').replace(',', '')) >= 160000]
for s in high_aus:
    issue = "Senior leadership - no bonus. Retention risk" if int(s['salary'].replace('$', '').replace(',', '')) > 200000 else "Senior role - equity issue vs others"
    print(f"{'AUS':<5} {s['id']:<10} {s['name']:<25} {s['position'][:27]:<28} {s['salary']:<14} {issue:<35}")

high_india = [s for s in india_need_review if "Senior" in s['level']]
for s in high_india:
    issue = "Equity issue: similar roles have 10% bonus"
    print(f"{'IND':<5} {s['id']:<10} {s['name']:<25} {s['level'][:27]:<28} {s['ctc_aud']:<14} {issue:<35}")

# TABLE 3: MEDIUM PRIORITY
print("\n[3] MEDIUM PRIORITY - Performance Review Needed (4 staff)")
print("-"*120)
print(f"{'Reg':<5} {'ID':<10} {'Name':<25} {'Position/Level':<28} {'Salary':<14} {'Recommendation':<35}")
print("-"*120)

med_aus = [s for s in aus_need_review if 100000 <= int(s['salary'].replace('$', '').replace(',', '')) < 160000]
for s in med_aus:
    print(f"{'AUS':<5} {s['id']:<10} {s['name']:<25} {s['position'][:27]:<28} {s['salary']:<14} {'Performance & market review':<35}")

med_india = [s for s in india_need_review if "Mid" in s['level'] and "Senior" not in s['level']]
for s in med_india:
    print(f"{'IND':<5} {s['id']:<10} {s['name']:<25} {s['level'][:27]:<28} {s['ctc_aud']:<14} {'Review vs India market rates':<35}")

# TABLE 4: STANDARD REVIEWS
print("\n[4] STANDARD REVIEW (Annual Cycle) - 2 staff")
print("-"*120)
print(f"{'Reg':<5} {'ID':<10} {'Name':<25} {'Position/Level':<28} {'Salary':<14} {'Recommendation':<35}")
print("-"*120)

std_aus = [s for s in aus_need_review if int(s['salary'].replace('$', '').replace(',', '')) < 100000]
for s in std_aus:
    print(f"{'AUS':<5} {s['id']:<10} {s['name']:<25} {s['position'][:27]:<28} {s['salary']:<14} {'Annual review cycle':<35}")

# ACTIONS
print("\n" + "="*120)
print(" CRITICAL ACTIONS ".center(120, "="))
print("="*120)

print("\n[IMMEDIATE - Next 30 Days]")
print("  • Schedule performance reviews for 12 staff without retention bonuses")
print("  • Market salary comparisons for 6 HIGH PRIORITY staff")
print("  • Fix equity issues: India mid-senior (3) and AUS senior (Komal) vs peers with bonuses")

print("\n[SHORT TERM - Feb 2026 (3 months)]")
print("  • Plan retention for Feb 2026 expiry: Naveen ($23K) + Eduardo ($19.3K) = $42.3K at risk")

print("\n[MEDIUM TERM - Aug 2026 (9 months)]")
print("  • Plan retention for Aug 2026 expiry: 5 staff, ~$75K total at risk")

print("\n" + "="*120)
print(" FINANCIAL SUMMARY ".center(120, "="))
print("="*120)
print(f"\n  Current Retention Bonus Investment: $117,221/year (AUS: $98.8K | India: $18.4K)")
print(f"  At Risk Feb 2026: $42,300/year (2 staff)")
print(f"  At Risk Aug 2026: $74,921/year (5 staff)")
print("\n" + "="*120 + "\n")

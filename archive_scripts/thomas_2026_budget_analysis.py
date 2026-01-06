"""
2026 Budget Bridge Analysis Tool
Helps structure response to Thomas's budget requirements
"""

from datetime import datetime
from typing import List, Dict
import json

class BudgetBridgeAnalyzer:
    """Tool to analyze pipeline data and create Thomas's budget bridge"""

    def __init__(self):
        self.gbp_aud_rate = 0.498  # Approximate GBP to AUD conversion

    def analyze_pipeline_dates(self, opportunities: List[Dict]) -> Dict:
        """Analyze sign dates in pipeline"""
        by_period = {
            'Q4_2025': [],
            'Q1_2026': [],
            'Q2_2026': [],
            'Q3_2026': [],
            'Q4_2026': [],
            '2027_plus': []
        }

        for opp in opportunities:
            sign_date = datetime.strptime(opp['est_sign_date'], '%d/%m/%Y')

            if sign_date.year < 2026:
                if sign_date.month >= 10:
                    by_period['Q4_2025'].append(opp)
            elif sign_date.year == 2026:
                if sign_date.month <= 3:
                    by_period['Q1_2026'].append(opp)
                elif sign_date.month <= 6:
                    by_period['Q2_2026'].append(opp)
                elif sign_date.month <= 9:
                    by_period['Q3_2026'].append(opp)
                else:
                    by_period['Q4_2026'].append(opp)
            else:
                by_period['2027_plus'].append(opp)

        return by_period

    def create_budget_template(self):
        """Create template for Thomas's requirements"""

        template = """
================================================================================
2026 BUDGET BRIDGE - CHRIS MARINELLI / AUSTRALIA OPERATIONS
================================================================================

Date: {date}
Prepared by: Chris Marinelli

================================================================================
SECTION 1: ORDERBOOK (As at 1 January 2026)
================================================================================

Current Orderbook:
------------------
[List all signed contracts that will deliver revenue in 2026]

Project                    | Client              | Contract Value | 2026 Revenue | Status
---------------------------|---------------------|----------------|--------------|--------
Example: Corop Solar Farm  | LEESON PROJECTS     | £XXX,XXX       | £XXX,XXX     | Active


Expected Wins (Nov-Dec 2025):
------------------------------
[Opportunities you expect to close before Jan 1, 2026]

Opp No | Project                 | Client         | Value    | Prob% | Expected | Sign Date
-------|-------------------------|----------------|----------|-------|----------|----------
6470   | Corop Solar Farm Var    | LEESON         | £41,356  | 20%   | £8,271   | 30/11/2025
6864   | Swan Hill SF BESS       | ELECTRANET     | £9,965   | 50%   | £4,983   | 29/10/2025


Total Projected Orderbook (1 Jan 2026): £XXX,XXX
Total 2026 Revenue Conversion: £XXX,XXX

Orderbook Analysis:
-------------------
- Current orderbook vs 2026 conversion: XX%
- Revenue scheduled after 2026: £XXX,XXX
- Opportunities to bring forward: [List projects that could accelerate]


================================================================================
SECTION 2: VARIATIONS
================================================================================

Projected Variations (2026):
-----------------------------
Based on run rate analysis from current projects:

Project                    | Base Contract | Est. Variations | Confidence | Notes
---------------------------|---------------|-----------------|------------|-------
Example: Birdwood Project  | £XXX,XXX      | £XX,XXX         | High       | Scope changes expected


Total Variation Revenue 2026: £XXX,XXX
Confidence Level: [High/Medium/Low]

Recommendations:
- Consider making variations a formal target for operations
- Monthly tracking of variation pipeline


================================================================================
SECTION 3: SALES & PIPELINE
================================================================================

Q1 2026 Pipeline:
-----------------
Critical Q4 2025 wins needed for Q1 2026 conversion:

Opp No | Project                 | Client         | Value      | Prob% | Sign Date   | Revenue Date
-------|-------------------------|----------------|------------|-------|-------------|-------------
6470   | Corop Solar Farm        | LEESON         | £41,356    | 20%   | 30/11/2025  | Q1 2026
6864   | Swan Hill BESS          | ELECTRANET     | £9,965     | 50%   | 29/10/2025  | Q1 2026
6827   | Malaysian Generator     | TNB            | £249,131   | 40%   | 31/01/2026  | Q1 2026


Q2-Q4 2026 Pipeline:
--------------------
[Key opportunities by quarter]

Quarter | No. Opps | Total Value | Weighted Value | Key Projects
--------|----------|-------------|----------------|-------------
Q2 2026 | X        | £XXX,XXX    | £XXX,XXX       | List top 3
Q3 2026 | X        | £XXX,XXX    | £XXX,XXX       | List top 3
Q4 2026 | X        | £XXX,XXX    | £XXX,XXX       | List top 3


================================================================================
SECTION 4: CRITICAL WINS FOR 2026
================================================================================

Must-Win Opportunities:
-----------------------
[Rank by importance to achieving FY budget]

Priority | Opp No | Project        | Client     | Value    | Sign Date | Why Critical
---------|--------|----------------|------------|----------|-----------|-------------
1        | XXXX   | Project Name   | Client     | £XXX,XXX | Q1 2026   | Reason
2        | XXXX   | Project Name   | Client     | £XXX,XXX | Q2 2026   | Reason
3        | XXXX   | Project Name   | Client     | £XXX,XXX | Q3 2026   | Reason


================================================================================
SECTION 5: PIPELINE DATA QUALITY ISSUES
================================================================================

Issues Identified:
------------------
1. DATE CONCENTRATION: {pct_2027}% of pipeline shows 01/01/2027 sign dates
   - This appears to be default/placeholder dates
   - Action: Review each opportunity and assign realistic sign dates

2. LOW PROBABILITY: Weighted value only {weighted_pct}% of total
   - Average probability: {avg_prob}%
   - Action: Re-assess probability based on client engagement

3. Q1 2026 GAP: Insufficient opportunities for Q1 conversion
   - Only £XXX,XXX weighted for Q1
   - Action: Identify acceleratable projects


Pipeline Cleanup Actions:
-------------------------
□ Review all 01/01/2027 dates - assign realistic dates
□ Update probability based on latest client contact
□ Identify opportunities that can be brought forward
□ Add missing Q4 2025 / Q1 2026 opportunities
□ Validate client contact information


================================================================================
SECTION 6: BRIDGE TO FY2026 TARGET
================================================================================

Component                          | Value      | Confidence | Notes
-----------------------------------|------------|------------|-------
Opening Orderbook (1 Jan 2026)     | £XXX,XXX   | High       | Signed contracts
Variations (existing projects)     | £XX,XXX    | Medium     | Based on run rate
Q1 2026 Wins                       | £XX,XXX    | Medium     | See Section 3
Q2 2026 Wins                       | £XX,XXX    | Low        | Pipeline dependent
Q3 2026 Wins                       | £XX,XXX    | Low        | Pipeline dependent
Q4 2026 Wins                       | £XX,XXX    | Low        | Pipeline dependent
                                   |            |            |
TOTAL 2026 REVENUE TARGET          | £XXX,XXX   |            |

Gap Analysis:
-------------
Company Target: £26M
Your Contribution Target: £XXX,XXX (X% of company target)
Current Projection: £XXX,XXX
GAP: £XXX,XXX

Actions to close gap:
□ [Action 1]
□ [Action 2]
□ [Action 3]


================================================================================
NEXT STEPS (2 WEEK DELIVERABLE)
================================================================================

Week 1 (by {week1_date}):
-------------------------
□ Clean up pipeline dates - remove all placeholder 01/01/2027 dates
□ Update probabilities based on latest client engagement
□ Identify top 10 critical wins for 2026
□ Calculate realistic orderbook projection for 1 Jan 2026

Week 2 (by {week2_date}):
-------------------------
□ Quantify variation potential from existing projects
□ Create month-by-month revenue bridge for 2026
□ Identify opportunities to accelerate from 2027 to 2026
□ Validate with team and submit to Thomas


================================================================================
KEY QUESTIONS TO ANSWER
================================================================================

1. What is your projected orderbook at 1st January 2026?
   → Answer: £XXX,XXX

2. Which orders will you win between today and Jan 1st?
   → Answer: [List with dates and values]

3. Total orderbook vs 2026 conversion?
   → Answer: XX% converts in 2026, XX% in 2027+
   → Action: [Projects that can be brought forward]

4. Can you firm up variation estimates vs run rate?
   → Answer: £XX,XXX based on [method]

5. What are you planning to win in Nov/Dec for Q1 conversion?
   → Answer: [List opportunities]

6. List critical wins for 2026 and when you need to win them?
   → Answer: [See Section 4]

7. Is pipeline data accurate?
   → Answer: [Status and cleanup plan]

================================================================================
""".format(
            date=datetime.now().strftime('%d %B %Y'),
            pct_2027="{pct_2027}",  # Placeholder for calculation
            weighted_pct="{weighted_pct}",
            avg_prob="{avg_prob}",
            week1_date=(datetime.now()).strftime('%d %B %Y'),
            week2_date=(datetime.now()).strftime('%d %B %Y')
        )

        return template

    def calculate_summary_stats(self, opportunities: List[Dict]) -> Dict:
        """Calculate summary statistics for pipeline"""
        total_value = sum(opp['value_gbp'] for opp in opportunities)
        weighted_value = sum(opp['value_gbp'] * (opp['probability'] / 100) for opp in opportunities)

        # Count 2027 dates
        jan_2027_count = sum(1 for opp in opportunities if opp['est_sign_date'] == '01/01/2027')

        avg_probability = sum(opp['probability'] for opp in opportunities) / len(opportunities) if opportunities else 0

        return {
            'total_opps': len(opportunities),
            'total_value': total_value,
            'weighted_value': weighted_value,
            'weighted_pct': (weighted_value / total_value * 100) if total_value > 0 else 0,
            'pct_2027': (jan_2027_count / len(opportunities) * 100) if opportunities else 0,
            'avg_probability': avg_probability,
            'jan_2027_count': jan_2027_count
        }


def main():
    """Generate template"""
    analyzer = BudgetBridgeAnalyzer()
    template = analyzer.create_budget_template()

    # Save to file
    output_file = 'thomas_2026_budget_response_template.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"[OK] Budget bridge template created: {output_file}")
    print()
    print("CRITICAL ISSUES TO ADDRESS:")
    print("===========================")
    print()
    print("1. PIPELINE DATES ISSUE")
    print("   - Most opportunities show 01/01/2027 sign dates")
    print("   - This means GBP 3.16M is NOT contributing to 2026 budget")
    print("   - Action: Review CRM and assign realistic 2026 dates")
    print()
    print("2. Q1 2026 CONVERSION GAP")
    print("   - Only GBP 300K weighted for Q1 2026")
    print("   - Thomas specifically asked: 'What are you winning in Nov/Dec for Q1?'")
    print("   - Action: Identify opportunities to close in Nov/Dec 2025")
    print()
    print("3. LOW PROBABILITY WEIGHTING")
    print("   - Weighted value only 17% of total pipeline")
    print("   - Action: Re-assess probability based on actual client engagement")
    print()
    print("IMMEDIATE ACTIONS (THIS WEEK):")
    print("===============================")
    print()
    print("[ ] Export full CRM pipeline data (all dates, not just 2027)")
    print("[ ] Review each opportunity - assign realistic sign dates")
    print("[ ] List current signed contracts (orderbook as of today)")
    print("[ ] Calculate expected variations from existing projects")
    print("[ ] Identify which opportunities can be brought forward to 2026")
    print()
    print(f"Template saved to: {output_file}")


if __name__ == '__main__':
    main()

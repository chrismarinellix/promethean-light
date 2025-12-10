"""Pre-computed summaries for common queries - Ultra fast, 0 tokens"""

from typing import Dict, List, Optional


def get_india_salary_bands() -> Dict:
    """Standard salary bands for India Power Systems Engineers"""
    return {
        "P.S Engineer (Junior)": {"min_inr": "INR 10 Lakhs", "max_inr": "INR 25 Lakhs", "min_aud": "$17,500", "max_aud": "$43,860"},
        "Senior P.S Engineer": {"min_inr": "INR 25 Lakhs", "max_inr": "INR 40 Lakhs", "min_aud": "$43,860", "max_aud": "$70,175"},
        "Lead P.S Engineer": {"min_inr": "INR 40 Lakhs", "max_inr": "INR 50 Lakhs", "min_aud": "$70,175", "max_aud": "$87,719"},
        "Principal P.S Engineer": {"min_inr": "INR 50 Lakhs+", "max_inr": "-", "min_aud": "$87,719+", "max_aud": "-"},
    }


def get_india_staff_summary() -> Dict:
    """Pre-computed India staff summary"""
    bands = get_india_salary_bands()
    return {
        "summary": "7 India staff members, INR 2M-8M CTC range",
        "salary_bands": bands,
        "staff": [
            {
                "id": "470396",
                "name": "Faraz Khan",
                "level": "Senior",
                "ctc_inr": "INR 80,00,002",
                "ctc_aud": "$140,351",
                "band_range": "INR 25L-40L",
                "vs_band": "ABOVE (Senior paid at Principal+ level)",
                "retention_bonus": "10% (INR 8L)",
                "bonus_until": "Aug 2026",
                "total_with_bonus_inr": "INR 88,00,002",
                "total_with_bonus_aud": "$154,386"
            },
            {
                "id": "470365",
                "name": "Mohammed Kandanari Nathar",
                "level": "Senior",
                "ctc_inr": "INR 59,99,996",
                "ctc_aud": "$105,263",
                "band_range": "INR 25L-40L",
                "vs_band": "ABOVE (at Lead level)",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "INR 59,99,996",
                "total_with_bonus_aud": "$105,263"
            },
            {
                "id": "470320",
                "name": "Owais Raja",
                "level": "Mid-Senior",
                "ctc_inr": "INR 25,00,006",
                "ctc_aud": "$43,860",
                "band_range": "INR 25L-40L",
                "vs_band": "AT MIN (bottom of Senior band)",
                "retention_bonus": "10% (INR 2.5L)",
                "bonus_until": "Aug 2026",
                "total_with_bonus_inr": "INR 27,50,006",
                "total_with_bonus_aud": "$48,246",
                "tenure": "~2.5 years (6-7 months training + ~2 years engineer)",
                "career_status": "Seeking promotion to Senior role",
                "education": "PhD in Power Systems (relevant field)",
                "pending_actions": "Skills review with Tony not yet completed",
                "flight_risk": "May return to academia - needs more industry experience first",
                "notes": "Strong academic background (PhD). Started as junior trainee, now seeking senior role. Potential long-term interest in returning to academic career."
            },
            {
                "id": "470465",
                "name": "Chirag Rohit",
                "level": "Mid-Senior",
                "ctc_inr": "INR 25,00,002",
                "ctc_aud": "$43,860",
                "band_range": "INR 25L-40L",
                "vs_band": "AT MIN (bottom of Senior band)",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "INR 25,00,002",
                "total_with_bonus_aud": "$43,860"
            },
            {
                "id": "470482",
                "name": "Chandan Kumar Singh",
                "level": "Mid-Senior",
                "ctc_inr": "INR 25,00,002",
                "ctc_aud": "$43,860",
                "band_range": "INR 25L-40L",
                "vs_band": "AT MIN (bottom of Senior band)",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "INR 25,00,002",
                "total_with_bonus_aud": "$43,860"
            },
            {
                "id": "470311",
                "name": "Sirisha Ammanamanchi",
                "level": "Mid-level",
                "ctc_inr": "INR 22,50,009",
                "ctc_aud": "$39,474",
                "band_range": "INR 10L-25L",
                "vs_band": "WITHIN (upper Junior band)",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "INR 22,50,009",
                "total_with_bonus_aud": "$39,474"
            },
            {
                "id": "470431",
                "name": "Abhinit Gaurav",
                "level": "Mid-level",
                "ctc_inr": "INR 19,99,991",
                "ctc_aud": "$35,088",
                "band_range": "INR 10L-25L",
                "vs_band": "WITHIN (mid Junior band)",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "INR 19,99,991",
                "total_with_bonus_aud": "$35,088"
            }
        ],
        "total_count": 7,
        "with_retention_bonus": 2,
        "retention_bonus_staff": ["Faraz Khan", "Owais Raja"],
        "retention_bonus_expires": "Aug 2026"
    }


def get_australia_staff_summary() -> Dict:
    """Pre-computed Australia staff summary"""
    return {
        "summary": "13 Australia staff members, $49K-$260K AUD range",
        "staff": [
            {"id": "470408", "name": "Chris Marinelli", "position": "Operations Director", "salary": "$260,000"},
            {"id": "435865", "name": "Anthony Morton", "position": "Global Tech Head", "salary": "$250,000"},
            {"id": "435867", "name": "Robby Palackal", "position": "Team Lead [RESIGNED]", "salary": "$230,000", "retention_bonus": "10%", "total": "$253,000", "expires": "Feb 2026"},
            {"id": "470162", "name": "Naveenkumar Rajagopal", "position": "Principal Engineer", "salary": "$230,000", "retention_bonus": "10%", "total": "$253,000", "expires": "Feb 2026"},
            {"id": "450639", "name": "Eduardo Jr Laygo", "position": "Lead Engineer", "salary": "$193,000", "retention_bonus": "10%", "total": "$212,300", "expires": "Feb 2026"},
            {"id": "459865", "name": "Ajith Tennakoon", "position": "Lead Engineer", "salary": "$220,000", "retention_bonus": "10%", "total": "$242,000", "expires": "Aug 2026"},
            {"id": "470305", "name": "Md Rahman", "position": "Senior Engineer", "salary": "$175,000", "retention_bonus": "10%", "total": "$192,500", "expires": "Aug 2026"},
            {"id": "470479", "name": "Zabir Uddin Hussainy Syed", "position": "Lead Engineer", "salary": "$170,000", "retention_bonus": "10%", "total": "$187,000", "expires": "Aug 2026"},
            {"id": "470443", "name": "Komal Gaikwad", "position": "Senior Engineer", "salary": "$160,000"},
            {"id": "470433", "name": "Dominic Moncada", "position": "Power Systems Engineer", "salary": "$140,000"},
            {"id": "470428", "name": "Khadija Kobra", "position": "Power Systems Engineer", "salary": "$130,000"},
            {"id": "470434", "name": "Hayden Brunjes", "position": "Power Systems Engineer", "salary": "$95,000"},
            {"id": "470116", "name": "Parthena Savvidis", "position": "Administrator", "salary": "$49,000"}
        ],
        "total_count": 13,
        "with_retention_bonus": 6,
        "retention_bonus_expires_feb_2026": 3,
        "retention_bonus_expires_aug_2026": 3,
        "notes": "Ajith raised to $220K + 10% bonus. Naveen raised to $230K. Robby resigned."
    }


def get_retention_bonus_summary() -> Dict:
    """Pre-computed retention bonus summary"""
    return {
        "total_staff_with_bonuses": 9,
        "expires_feb_2026": [
            {"name": "Robby Palackal [RESIGNED]", "bonus": "10%", "amount_aud": "$23,000"},
            {"name": "Naveen Rajagopal", "bonus": "10%", "amount_aud": "$23,000"},
            {"name": "Eduardo Laygo", "bonus": "10%", "amount_aud": "$19,300"}
        ],
        "expires_aug_2026": [
            {"name": "Ajith Tennakoon", "bonus": "10%", "amount_aud": "$22,000"},
            {"name": "Md Rahman", "bonus": "10%", "amount_aud": "$17,500"},
            {"name": "Zabir Uddin", "bonus": "10%", "amount_aud": "$17,000"},
            {"name": "Amani (Malaysia)", "bonus": "10%", "amount_myr": "26K MYR"},
            {"name": "Faraz Khan (India)", "bonus": "10%", "amount_inr": "800K INR"},
            {"name": "Owais Raja (India)", "bonus": "10%", "amount_inr": "250K INR"}
        ],
        "total_annual_cost_aud": "$148,000"
    }


def get_malaysia_staff_summary() -> Dict:
    """Pre-computed Malaysia staff summary"""
    return {
        "summary": "1 Malaysia staff member",
        "staff": [
            {
                "id": "470XXX",
                "name": "Amani",
                "level": "Engineer",
                "salary_myr": "MYR 156,000",
                "salary_aud": "$52,000",
                "retention_bonus": "10% (26K MYR)",
                "bonus_until": "Aug 2026"
            }
        ],
        "total_count": 1,
        "with_retention_bonus": 1
    }


def get_all_staff_summary() -> Dict:
    """Complete team pay summary across all regions"""
    aus = get_australia_staff_summary()
    india = get_india_staff_summary()
    malaysia = get_malaysia_staff_summary()

    return {
        "australia": aus,
        "india": india,
        "malaysia": malaysia,
        "totals": {
            "total_headcount": aus["total_count"] + india["total_count"] + malaysia["total_count"],
            "australia_headcount": aus["total_count"],
            "india_headcount": india["total_count"],
            "malaysia_headcount": malaysia["total_count"],
            "total_with_retention_bonus": aus["with_retention_bonus"] + india["with_retention_bonus"] + malaysia["with_retention_bonus"]
        }
    }


def get_project_sentinel_summary() -> Dict:
    """Pre-computed Project Sentinel summary"""
    return {
        "summary": "Project Sentinel - Continuous Improvement Initiative with MacBook Air Prize Draw",
        "prize_draw_date": "December 19-22, 2025",
        "scoring_deadline": "December 13, 2025",
        "lead": "Chris Marinelli (Managing Director)",
        "prizes": ["MacBook Air", "Windows Laptop", "Cash"],
        "submissions": [
            {
                "number": 1,
                "proposer": "Australia Team",
                "topic": "Knowledge Sharing and Training Initiative",
                "status": "Active - work underway"
            },
            {
                "number": 2,
                "proposer": "Malaysia Team",
                "topic": "Knowledge Sharing and Training Initiative",
                "status": "Active - work underway"
            },
            {
                "number": 3,
                "proposer": "TBD",
                "topic": "Details pending",
                "status": "FUNDED - Implementation Approved (Nov 18, 2025)"
            },
            {
                "number": 4,
                "proposer": "ISN / Rachael Yul",
                "topic": "NAS Storage Solution (QNAP 20TB)",
                "focus": "Improved data management and accessibility",
                "status": "Under Review"
            },
            {
                "number": 5,
                "proposer": "Zabir",
                "topic": "Data Management Improvements",
                "focus": "Reducing time copying data between machines",
                "status": "Under Review"
            },
            {
                "number": 6,
                "proposer": "Dominic Joey Jr Moncada (Australia)",
                "topic": "Standardized Simulation Assessment Guideline",
                "focus": "Reducing simulation review time",
                "status": "Under Review"
            }
        ],
        "scoring_criteria": [
            {"criterion": "Business Impact", "weight": "25%"},
            {"criterion": "Innovation & Creativity", "weight": "20%"},
            {"criterion": "Feasibility", "weight": "20%"},
            {"criterion": "Scalability", "weight": "15%"},
            {"criterion": "Time Savings", "weight": "10%"},
            {"criterion": "Quality Improvement", "weight": "10%"}
        ],
        "total_submissions": 6,
        "funded_count": 1,
        "active_count": 2,
        "under_review_count": 3
    }


# Pre-computed summaries registry
SUMMARIES = {
    "india_staff": get_india_staff_summary,
    "australia_staff": get_australia_staff_summary,
    "malaysia_staff": get_malaysia_staff_summary,
    "retention_bonuses": get_retention_bonus_summary,
    "all_staff": get_all_staff_summary,
    "team_pay": get_all_staff_summary,
    "project_sentinel": get_project_sentinel_summary,
}


def get_summary(summary_name: str) -> Optional[Dict]:
    """Get pre-computed summary by name"""
    if summary_name in SUMMARIES:
        return SUMMARIES[summary_name]()
    return None

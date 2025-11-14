"""Pre-computed summaries for common queries - Ultra fast, 0 tokens"""

from typing import Dict, List


def get_india_staff_summary() -> Dict:
    """Pre-computed India staff summary"""
    return {
        "summary": "7 India staff members, ₹2M-₹8M CTC range",
        "staff": [
            {
                "id": "470396",
                "name": "Faraz Khan",
                "level": "Senior",
                "ctc_inr": "₹8,000,002",
                "ctc_aud": "$140,351",
                "retention_bonus": "10% (₹800K)",
                "bonus_until": "Aug 2026",
                "total_with_bonus_inr": "₹8,800,002",
                "total_with_bonus_aud": "$154,386"
            },
            {
                "id": "470365",
                "name": "Mohammed Kandanari Nathar",
                "level": "Senior",
                "ctc_inr": "₹5,999,996",
                "ctc_aud": "$105,263",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "₹5,999,996",
                "total_with_bonus_aud": "$105,263"
            },
            {
                "id": "470320",
                "name": "Owais Raja",
                "level": "Mid-Senior",
                "ctc_inr": "₹2,500,006",
                "ctc_aud": "$43,860",
                "retention_bonus": "10% (₹250K)",
                "bonus_until": "Aug 2026",
                "total_with_bonus_inr": "₹2,750,006",
                "total_with_bonus_aud": "$48,246"
            },
            {
                "id": "470465",
                "name": "Chirag Rohit",
                "level": "Mid-Senior",
                "ctc_inr": "₹2,500,002",
                "ctc_aud": "$43,860",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "₹2,500,002",
                "total_with_bonus_aud": "$43,860"
            },
            {
                "id": "470482",
                "name": "Chandan Kumar Singh",
                "level": "Mid-Senior",
                "ctc_inr": "₹2,500,002",
                "ctc_aud": "$43,860",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "₹2,500,002",
                "total_with_bonus_aud": "$43,860"
            },
            {
                "id": "470311",
                "name": "Sirisha Ammanamanchi",
                "level": "Mid-level",
                "ctc_inr": "₹2,250,009",
                "ctc_aud": "$39,474",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "₹2,250,009",
                "total_with_bonus_aud": "$39,474"
            },
            {
                "id": "470431",
                "name": "Abhinit Gaurav",
                "level": "Mid-level",
                "ctc_inr": "₹1,999,991",
                "ctc_aud": "$35,088",
                "retention_bonus": "None",
                "bonus_until": "-",
                "total_with_bonus_inr": "₹1,999,991",
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
            {"id": "435867", "name": "Robby Palackal", "position": "Team Lead", "salary": "$230,000", "retention_bonus": "10%", "total": "$253,000", "expires": "Feb 2026"},
            {"id": "470162", "name": "Naveenkumar Rajagopal", "position": "Principal Engineer", "salary": "$220,000", "retention_bonus": "10%", "total": "$242,000", "expires": "Feb 2026"},
            {"id": "450639", "name": "Eduardo Jr Laygo", "position": "Lead Engineer", "salary": "$193,000", "retention_bonus": "10%", "total": "$212,300", "expires": "Feb 2026"},
            {"id": "459865", "name": "Ajith Tennakoon", "position": "Lead Engineer", "salary": "$185,000", "retention_bonus": "None"},
            {"id": "470305", "name": "Md Rahman", "position": "Senior Engineer", "salary": "$175,000", "retention_bonus": "10%", "total": "$192,500", "expires": "Aug 2026"},
            {"id": "470479", "name": "Zabir Uddin Hussainy Syed", "position": "Lead Engineer", "salary": "$170,000", "retention_bonus": "10%", "total": "$187,000", "expires": "Aug 2026"},
            {"id": "470443", "name": "Komal Gaikwad", "position": "Senior Engineer", "salary": "$160,000"},
            {"id": "470433", "name": "Dominic Moncada", "position": "Power Systems Engineer", "salary": "$140,000"},
            {"id": "470428", "name": "Khadija Kobra", "position": "Power Systems Engineer", "salary": "$130,000"},
            {"id": "470434", "name": "Hayden Brunjes", "position": "Power Systems Engineer", "salary": "$95,000"},
            {"id": "470116", "name": "Parthena Savvidis", "position": "Administrator", "salary": "$49,000"}
        ],
        "total_count": 13,
        "with_retention_bonus": 5,
        "retention_bonus_expires_feb_2026": 3,
        "retention_bonus_expires_aug_2026": 2
    }


def get_retention_bonus_summary() -> Dict:
    """Pre-computed retention bonus summary"""
    return {
        "total_staff_with_bonuses": 8,
        "expires_feb_2026": [
            {"name": "Robby Palackal", "bonus": "10%", "amount_aud": "$23,000"},
            {"name": "Naveen Rajagopal", "bonus": "10%", "amount_aud": "$22,000"},
            {"name": "Eduardo Laygo", "bonus": "10%", "amount_aud": "$19,300"}
        ],
        "expires_aug_2026": [
            {"name": "Md Rahman", "bonus": "10%", "amount_aud": "$17,500"},
            {"name": "Zabir Uddin", "bonus": "10%", "amount_aud": "$17,000"},
            {"name": "Amani (Malaysia)", "bonus": "10%", "amount_myr": "26K MYR"},
            {"name": "Faraz Khan (India)", "bonus": "10%", "amount_inr": "₹800K"},
            {"name": "Owais Raja (India)", "bonus": "10%", "amount_inr": "₹250K"}
        ],
        "total_annual_cost_aud": "$126,000"
    }


# Pre-computed summaries registry
SUMMARIES = {
    "india_staff": get_india_staff_summary,
    "australia_staff": get_australia_staff_summary,
    "retention_bonuses": get_retention_bonus_summary,
}


def get_summary(summary_name: str) -> Optional[Dict]:
    """Get pre-computed summary by name"""
    if summary_name in SUMMARIES:
        return SUMMARIES[summary_name]()
    return None

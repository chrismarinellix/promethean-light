"""
Ingest all text files from the Promethean Light folder and pipeline data, then delete the originals.
Uses the CLI module functions directly.
"""

import os
import sys
from pathlib import Path

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path setup
from mydata.cli import get_pipeline

# Pipeline data to ingest
PIPELINE_DATA = """
Grid and Power Systems Advisory Pipeline - November 2025

Opportunity Summary:
Total Pipeline Value: AUD $5,033,068
Total Probability-Weighted Value (GBP): £1,435,364

Active Opportunities:

1. Opp #4855 - Flynn Solar Farm Connection Studies
   - Customer: BNRG RENEWABLES LIMITED (Peter Leeson)
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $150,000 (GBP £74,739)
   - Probability: 0%
   - Est Sign Date: 01/01/2027
   - Date Entered: 04/03/2024
   - Status: Unlikely to proceed - not expecting further work with Peter Leeson

2. Opp #5042 (680AU) - Castle Doyle Wind Farm Connection Studies
   - Customer: Sirius Energy Australia Pty Ltd
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $570,000 (GBP £284,009)
   - Probability: 10%
   - Prob-Weighted GBP: £28,401
   - Est Sign Date: 01/01/2027
   - Date Entered: 13/04/2024

3. Opp #5043 (680AU) - Bethungra Wind Farm Connection Studies
   - Customer: Sirius Energy Australia Pty Ltd
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $570,000 (GBP £284,009)
   - Probability: 10%
   - Prob-Weighted GBP: £28,401
   - Est Sign Date: 01/01/2027
   - Date Entered: 13/04/2024

4. Opp #5147 (680AU) - Tabulam Solar Farm & BESS Connection Study Support
   - Customer: ELGIN ENERGY PTY LTD
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $576,100 (GBP £287,048)
   - Probability: 10%
   - Prob-Weighted GBP: £28,705
   - Est Sign Date: 01/01/2027
   - Date Entered: 07/05/2024

5. Opp #5676 (680AU) - Uranquinty AVR Replacement 5.3.9 Studies
   - Customer: Origin Energy Power Limited
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $400,000 (GBP £199,304)
   - Probability: 10%
   - Prob-Weighted GBP: £19,930
   - Est Sign Date: 01/01/2027
   - Date Entered: 12/10/2024

6. Opp #5677 (680AU) - Shoalhaven Control Scheme Replacement 5.3.9 Studies
   - Customer: Origin Energy Power Limited
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $400,000 (GBP £199,304)
   - Probability: 10%
   - Prob-Weighted GBP: £19,930
   - Est Sign Date: 01/01/2027
   - Date Entered: 12/10/2024

7. Opp #5415 (680AU) - Inverell BESS RO Studies
   - Customer: SOUTH ENERGY PTY LTD
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $625,100 (GBP £311,463)
   - Probability: 10%
   - Prob-Weighted GBP: £31,146
   - Est Sign Date: 01/01/2027
   - Date Entered: 16/06/2025

8. Opp #744 (680AU) - Emu Park BESS R1 Connection Studies
   - Customer: Metlen Energy and Metals
   - Main Rep: Chris Marinelli
   - Estimated Value: AUD $599,200 (GBP £298,558)
   - Probability: 10%
   - Prob-Weighted GBP: £29,856
   - Est Sign Date: 01/02/2027
   - Date Entered: 15/09/2025

All opportunities are for Grid and Power Systems Advisory services.
All opportunities use currency: AUD
"""

# Text files to ingest (excluding system/build files)
TEXT_FILES_TO_INGEST = [
    "APAC_Salary_Budget.txt",
    "pipeline_summary_output.txt",
    "HR_Salary_Guide_APAC.txt",
    "project_sentinel_list.txt",
    "PROJECT_SENTINEL_SUMMARY.txt",
    "sentinel_scoring_email.txt",
    "boulder_creek_filter_design_note.txt",
    "momtaz_promotion_diagram.txt",
    "salary_tables_output.txt",
    "license_resource_allocation_note.txt",
    "email_to_lisa_salary_changes.txt",
    "parthena_salary_research.txt",
    "client_contact_report.txt",
    "mt_challenger_summary.txt",
    "email_summary_detailed.txt",
    "email_summary_by_theme.txt",
    "team_salary_review_detailed.txt",
    "corrected_origin_projects.txt",
    "thomas_2026_budget_response_template.txt",
    "hayden_search_results.txt",
    "hayden_summary_output.txt",
    "hayden_info.txt",
    "HAYDEN_BRUNJES_COMPLETE_ANALYSIS.txt",
]

def main():
    base_path = Path(__file__).parent

    print("=" * 60)
    print("Promethean Light - Text File Ingestion & Cleanup")
    print("=" * 60)

    # Initialize pipeline
    print("\nInitializing ingestion pipeline...")
    pipeline = get_pipeline()
    print("Pipeline ready.")

    ingested_files = []
    failed_files = []

    # Ingest text files
    print("\n[1/2] Ingesting text files...")
    for filename in TEXT_FILES_TO_INGEST:
        file_path = base_path / filename
        if file_path.exists():
            try:
                result = pipeline.ingest_file(file_path)
                if result:
                    print(f"  [OK] Ingested: {filename}")
                    ingested_files.append(file_path)
                else:
                    print(f"  [SKIP] Already exists or empty: {filename}")
                    ingested_files.append(file_path)  # Still mark for deletion
            except Exception as e:
                print(f"  [ERROR] {filename}: {e}")
                failed_files.append(filename)
        else:
            print(f"  [NOT FOUND] {filename}")

    # Ingest pipeline data
    print("\n[2/2] Ingesting pipeline data...")
    try:
        result = pipeline.ingest_text(PIPELINE_DATA, source="pipeline://grid_power_advisory_nov2025")
        if result:
            print("  [OK] Pipeline data ingested")
        else:
            print("  [SKIP] Pipeline data may already exist")
    except Exception as e:
        print(f"  [ERROR] Pipeline: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Ingested: {len(ingested_files)} files")
    print(f"Failed: {len(failed_files)} files")

    # Delete ingested files
    if ingested_files:
        print(f"\nDeleting {len(ingested_files)} ingested files...")
        for file_path in ingested_files:
            try:
                file_path.unlink()
                print(f"  [DELETED] {file_path.name}")
            except Exception as e:
                print(f"  [ERROR] Could not delete {file_path.name}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    main()

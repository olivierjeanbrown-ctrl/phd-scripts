Adherence Report Generator (Python)
-----------------------------------
A reproducible Python pipeline for generating adherence metrics for the Mindfulness-Based Intervention for Pediatric mTBI project.
This script processes REDCap exports and partner-app usage logs to compute session adherence, weekly engagement, feasibility classifications, and MRI visit completions.

Overview
--------
This project contains a single Python script that:

1. Loads raw CSV files exported from:
   - REDCap (Day 1 + Week 4 visits)
   - Partner app session logs
   - Outcome tracking (IDs to include)

2. Cleans and harmonizes datasets:
   - Robust datetime parsing
   - Duration capping (max 3600s)
   - Type conversion for IDs, session numbers, and categories

3. Computes adherence metrics:
   - Total number of sessions
   - Total session duration
   - Number of unique days used
   - Counts by session type (Journey vs Standalone)

4. Computes weekly engagement:
   - sessionduration_wk1
   - sessionduration_wk2
   - sessionduration_wk3
   - sessionduration_wk4

5. Adds feasibility and MRI completion flags:
   - Binary adherence label
   - Day 1 MRI completion
   - Week 4 MRI (MRI2) completion

6. Outputs a clean CSV ready for downstream statistical analysis.

Directory Structure
-------------------
project/
  raw/                     - Input CSV files go here
    MBIProjectPhase2.csv
    Outcome_complete.csv
    PartnerReport.csv
  output/                  - Script creates this if missing
    Adherence_Report.csv
  adherence_report.py      - Main pipeline script
  README.txt               - This file

Dependencies
------------
The script uses:
- pandas
- numpy
- datetime (built-in)

To install dependencies:
pip install pandas numpy

How to Run
----------
From the project root, run:
python adherence_report.py

On first run, the script will:
- Create output/ if it does not exist
- Validate the presence of required raw files
- Generate Adherence_Report.csv

Required Input Files
-------------------
Place these inside raw/:

File: MBIProjectPhase2.csv
Description: Full REDCap export including Day 1 + Week 4 event records

File: Outcome_complete.csv
Description: List of participant IDs to include

File: PartnerReport.csv
Description: Partner app session logs

Output
------
File: output/Adherence_Report.csv

Contains one row per participant with:

REDCap Variables:
- record_id
- randomization (MBI / Control)
- mri_day1
- mri2_complete
- w4_ques
- w4_debrief

Partner App Summary:
- n_sessions
- total_session_time
- total_session_length
- unique_days
- n_mindfulness
- n_standalone

Weekly Adherence:
- sessionduration_wk1
- sessionduration_wk2
- sessionduration_wk3
- sessionduration_wk4

Feasibility Outcome:
- feasibility_outcome_adherence_label (0/1)

Configuration
-------------
In adherence_report.py, update the DIRECTORY variable to point to your local folder containing raw files.

Data Assumptions
----------------
- session_start_date is the timestamp used to determine weekly engagement.
- Week 1 begins at each participant’s REDCap Day 1 date.
- Durations above 3600 seconds are capped.
- Missing dates are treated as '9999/01/01'.
- All IDs in Outcome_complete.csv must appear in REDCap.

Troubleshooting
---------------
File not found:
- Ensure all required CSVs are in raw/

Date parsing failed:
- The script handles multiple formats. Rare corrupted rows are set to '9999/01/01'.

Missing weekly durations:
- Check that session_start_date and day_1_date exist and are valid.

Citation / Usage
----------------
You are free to reuse or modify this pipeline for research, replication, or quality control.
Please cite the repository or the accompanying manuscript where appropriate.

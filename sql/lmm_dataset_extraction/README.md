# LMM Dataset Extraction

# SAMPLE DATA NOT PROVIDED DUE TO CONFIDENTIALITY. MOCK DATA NOT GENERATED FOR THIS OPEN SOURCE SCRIPT!

## Overview
This query extracts a subset of participants from `MBI4mTBIoutput` for an interaction linear mixed-effects model (LMM). 
This query also implements all data from the PartnerReport for navigating app-usage data.

It filters for:

- Completion of both MRI sessions  
- Protocol adherence (≥ 9600 seconds in-app)  
- Complete resilience scores (`cdrisc_72` and `cdrisc_4w`)  

Results are sorted by `randomization` (MBI first, Sham second).

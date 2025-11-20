# Data Cleaning Tool

This repository contains an R script that prepares the dataset for downstream analysis, including:

## Workflow

1. **Load raw dataset** from `raw/data_placeholder.csv`
2. **Imputation**  
   - EM-based imputation using `mice`  
   - Replaces missing quantitative values
3. **Feature computation**  
   - Change scores (e.g., resilience, PedsQL, HBI)
4. **Stratification & Winsorization**  
   - Groups: MBI vs. Control  
   - Custom Winsorization at ±2.48 SD
5. **Output**  
   - Cleaned dataset saved to `output/data_placeholder_cleaned.csv`


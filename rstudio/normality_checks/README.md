normality_checks.R
---------------------
Purpose:
  This R script performs data cleaning and normality checks on a raw dataset. It generates histograms
  with density plots, Q-Q plots, runs Shapiro-Wilk tests, applies Box-Cox transformations if variables
  are not normally distributed, and saves the updated dataset with transformed variables.

Usage:
  1. Replace "raw/data_placeholder.csv" with the path to your actual CSV file.
  2. Ensure required packages are installed: ggplot2, car, MASS, rio.
     You can install missing packages using install.packages("package_name").
  3. Run the script in R or RStudio.
  4. Transformed variables are appended to the dataset with the suffix "_transformed".
  5. The updated dataset is saved as "output/data_cleaned.csv".

Dependencies:
  - R (version 4.0 or higher recommended)
  - ggplot2
  - car
  - MASS
  - rio

Features:
  - Automatically detects numeric variables in the dataset (excluding 'randomization').
  - Generates histograms with density lines for each variable.
  - Generates Q-Q plots for each variable.
  - Performs Shapiro-Wilk tests for normality.
  - Applies Box-Cox transformations to variables that are not normally distributed.
  - Re-checks normality on transformed variables.
  - Saves the updated dataset with transformed variables.

Notes:
  - 'randomization' is treated as a factor and is not transformed.
  - Do not commit confidential data to GitHub.
  - Make sure the "output" folder exists or create it before running the script.

Example:
  # Load script
  source("clean_data_normality.R")
  # The script will automatically process the dataset and save the cleaned file.

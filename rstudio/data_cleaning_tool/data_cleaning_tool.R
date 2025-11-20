# clean_data_tool.R
# ---------------------
# Purpose: Clean raw data, perform EM imputation, compute change scores, 
#          stratify by group, Winsorize variables, and save cleaned dataset.
# Language: R
# Dependencies: readr, dplyr, mice, psych, reshape2, ggplot2, MVN, DescTools, rio
# Notes: Replace "raw/data_placeholder.csv" with actual local data; 
#        do not commit confidential data.



#### Libraries ####
# Load necessary libraries
library(readr)
library(dplyr)
library(mice)
library(psych)
library(reshape2)
library(ggplot2)
library(MVN)
library(DescTools)
#### Load the data ####
# Load the dataset
data <- rio::import("raw/data_placeholder.csv", na.strings = c("", "NA"))   # set empty strings and "NA" as missing
data <- data %>%
  mutate(randomization = factor(randomization))  # categorical

#### Variable check ####
# Select the quantitative variables of interest
quant_vars <- c("cdrisc_72", "cdrisc_4w", "camm_baseline", "camm_4w", "hbi_baseline", "hbi_4w", "PedsQL_baseline_total", "PedsQL_4w_total", "PedsQL_4w_Physical", 
                "PedsQL_4w_Social", "PedsQL_4w_Emotional", "PedsQL_4w_School", "SEQ_72_total", "SEQ_4w_total",
                "gad_score_ed", "gad_score_wk48", "cesd_score", "cesd_score_4w")
#### Imputation ####
# Impute missing data using expectation maximization
imputed_data <- mice(data[quant_vars], method = "norm.predict", m = 1, maxit = 50, seed = 123)
completed_data <- complete(imputed_data)
# Replace missing values in the original data with imputed values
data[quant_vars] <- completed_data
#### Compute new variables with imputed data ####
# Add new quantitative variables
data <- data %>%
  mutate(cdrisc_change = cdrisc_4w - cdrisc_72,
         PedsQL_change = PedsQL_4w_total - PedsQL_baseline_total,
         PedsQL_Physical_change = PedsQL_4w_Physical - PedsQL_baseline_Physical,
         PedsQL_Social_change = PedsQL_4w_Social - PedsQL_baseline_Social,
         PedsQL_Emotional_change = PedsQL_4w_Emotional - PedsQL_baseline_Emotional,
         PedsQL_School_change = PedsQL_4w_School - PedsQL_baseline_School,
         hbi_change = hbi_4w - hbi_baseline)
#### Stratify and Winsorize ####
# Stratify data into two groups based on 'randomization'
group_MBI <- data %>% filter(randomization == 0)
group_control <- data %>% filter(randomization == 1)

# Custom Winsorization function for values 2.48 standard deviations below the mean
custom_winsorize <- function(x, threshold = 2.48) {
  mean_x <- mean(x, na.rm = TRUE)
  sd_x <- sd(x, na.rm = TRUE)
  lower_bound <- mean_x - threshold * sd_x
  upper_bound <- mean_x + threshold * sd_x
  x[x < lower_bound] <- lower_bound
  x[x > upper_bound] <- upper_bound
  return(x)
}

# Apply custom Winsorization function to each variable in both groups
for (var in quant_vars) {
  group_MBI[[var]] <- custom_winsorize(group_MBI[[var]])
  group_control[[var]] <- custom_winsorize(group_control[[var]])
}

# Incorporate Winsorized data back into the original data frame
for (var in quant_vars) {
  data[data$randomization == 0, var] <- group_MBI[[var]]
  data[data$randomization == 1, var] <- group_control[[var]]
}

#### Save new dataset, cleaned ####
# Save the updated dataset
write.csv(data, "output/data_placeholder_cleaned.csv", row.names = FALSE)

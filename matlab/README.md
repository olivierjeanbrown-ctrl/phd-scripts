
# Data Generator GUI (MATLAB)

A MATLAB GUI application that allows users to generate, visualize, and export mock experimental data.  
This project was developed as the **final assignment** for a graduate-level MATLAB programming course.

---

## Processes

- Specify **number of groups**
- Enter **sample sizes, means, and standard deviations** per group
- Generates normally distributed data for each group
- Automatically constructs:
  - Group labels  
  - Participant IDs  
  - Dependent variable values  
- Exports results to an **Excel (.xls)** file
- Includes filename validation and overwrite protection

---

##  Output Format

The generated dataset is saved as:

| IV (Group) | Participant | DV (Value) |
|------------|-------------|------------|
| 1          | 1           | ...        |
| 1          | 2           | ...        |
| ...        | ...         | ...        |

---

## How to Run

1. Open MATLAB  
2. Add the script folder to your path  
3. Run:

```matlab
datagenerator

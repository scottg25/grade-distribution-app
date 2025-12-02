# Grade Distribution App

**Interactive Streamlit App for Visualizing and Adjusting Students' Final Grades**

---

## **Description**

The Grade Distribution App is an interactive tool designed for professors to visualize, analyze, and adjust final course grades. First, upload the grades csv available in the "Grades" section in Canvas, and the app will automatically calculate letter grades based on either fixed point cutoffs or custom percentage distributions. The app also identifies students near grade cutoffs and allows you to bump their scores interactively.

---

## **Key Features**

- Assign letter grades using:
  - **Point cutoffs** (e.g., A ≥ 90, B ≥ 80)
  - **Percentage-based distributions** (e.g., top 30% = A)
- Visualize grade distributions with a dynamic **bar chart** showing counts and percentages.
- Identify **students within 2 points of a grade cutoff**.
- **Bump up student scores** interactively with buttons next to each student's name.
- **Export updated letter grades** to CSV sorted alphabetically.
- Warnings for:
  - Percentages summing to more than 100%
  - Misordered point cutoffs (e.g., B cutoff higher than A)

---

## **Getting Started**

### **Requirements**

- Python 3.9+  
- Packages listed in `requirements.txt`:

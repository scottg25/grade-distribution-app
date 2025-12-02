import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import io

# --- Functions ---

def convert_name(name):
    last, first = name.split(",", 1)
    return f"{first.strip()} {last.strip()}"

def get_grade(score, cutoffs):
    if isinstance(cutoffs, dict):
        if score >= cutoffs["A"]:
            return "A"
        elif score >= cutoffs["B"]:
            return "B"
        elif score >= cutoffs["C"]:
            return "C"
        elif score >= cutoffs["D"]:
            return "D"
        else:
            return "F"
    else:
        A, B, C, D = cutoffs
        if score >= A:
            return "A"
        elif score >= B:
            return "B"
        elif score >= C:
            return "C"
        elif score >= D:
            return "D"
        else:
            return "F"

def calculate_cutoffs(scores, percentages):
    scores_sorted = sorted(scores, reverse=True)
    n = len(scores_sorted)
    cutoffs = {}
    cumulative = 0
    grade_order = ["A", "B", "C", "D"]
    for grade in grade_order:
        count = int(np.ceil(percentages[grade] * n / 100))
        index = min(cumulative + count - 1, n-1)
        cutoffs[grade] = scores_sorted[index]
        cumulative += count
    cutoffs["F"] = 0
    return cutoffs

def plot_grade_distribution(student_grades, cutoffs):
    grade_counts = Counter(student_grades.values())
    grade_order = ["A", "B", "C", "D", "F"]
    counts_sorted = [grade_counts.get(g, 0) for g in grade_order]

    total_students = sum(counts_sorted)
    percentages = [(count / total_students) * 100 for count in counts_sorted]

    # Create x-axis labels with cutoffs
    x_labels = []
    for g in grade_order:
        if g in ["A", "B", "C", "D"]:
            if isinstance(cutoffs, dict):
                threshold = cutoffs[g]
            else:
                threshold = cutoffs[["A","B","C","D"].index(g)]
            x_labels.append(f"{g} ({threshold})")
        else:
            x_labels.append(f"{g} (0)")

    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(x_labels, counts_sorted, color='skyblue', edgecolor='black')

    # Add counts + percentages on top of bars
    for bar, pct, count in zip(bars, percentages, counts_sorted):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                f"{count} ({pct:.1f}%)", ha='center', va='bottom', fontsize=10)

    ax.set_xlabel("Grades (Cutoff Points)")
    ax.set_ylabel("Number of Students")
    ax.set_title("Grade Distribution")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

def export_grades_csv(student_grades):
    df_export = pd.DataFrame({
        "Student": list(student_grades.keys()),
        "Letter Grade": list(student_grades.values())
    }).sort_values(by="Student")
    csv_buffer = io.StringIO()
    df_export.to_csv(csv_buffer, index=False)
    st.download_button(
        "Download CSV of student grades",
        data=csv_buffer.getvalue(),
        file_name="student_letter_grades.csv",
        mime="text/csv"
    )

def display_near_cutoff_students(student_scores, cutoffs, use_percentage):
    st.subheader("Students within 2 points of the cutoff") 
    near_students = {}
    if use_percentage:
        grades = ["A","B","C","D"]
        for g in grades:
            threshold = cutoffs[g]
            students = [s for s, score in student_scores.items() if threshold-2 <= score < threshold]
            if students:
                near_students[g] = (threshold, students)
    else:
        for i, g in enumerate(["A","B","C","D"]):
            threshold = cutoffs[i]
            students = [s for s, score in student_scores.items() if threshold-2 <= score < threshold]
            if students:
                near_students[g] = (threshold, students)

    for grade, (threshold, students) in near_students.items():
        st.write(f"#### {grade} cutoff ({threshold})")
        for student in students:
            cols = st.columns([3,1])
            cols[0].write(student)

            # Use a callback to bump the student and immediately update the chart
            def bump_student(s=student):
                st.session_state.adjusted_scores[s] += 2

            cols[1].button("Bump", key=f"bump_{student}", on_click=bump_student)

# --- Streamlit App ---

st.title("Grade Distribution App")

uploaded_file = st.file_uploader("Upload your grade CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, skiprows=[1,2])
    df = df[df["Student"] != "Student, Test"]
    df["Student"] = df["Student"].apply(convert_name)
    df["Final Score"] = df["Final Score"].round()
    original_scores = dict(zip(df["Student"], df["Final Score"]))

    if "adjusted_scores" not in st.session_state:
        st.session_state.adjusted_scores = original_scores.copy()

    student_scores = st.session_state.adjusted_scores

    # Grading method
    method = st.radio("Choose grading method", ["Point Cutoffs", "Percentages"])
    use_percentage = method == "Percentages"

    if use_percentage:
        A = st.number_input("Percentage for A", 0, 100, 30)
        B = st.number_input("Percentage for B", 0, 100, 40)
        C = st.number_input("Percentage for C", 0, 100, 20)
        D = st.number_input("Percentage for D", 0, 100, 10)
        
        total_percentage = A + B + C + D
        if total_percentage > 100:
            st.warning(f"The sum of percentages is {total_percentage}%, which exceeds 100%! Please adjust values.")
        
        percentages = {"A": A, "B": B, "C": C, "D": D}
        percentages["F"] = max(0, 100 - total_percentage)
        
        cutoffs = calculate_cutoffs(list(student_scores.values()), percentages)
    else:
        A = st.number_input("A cutoff", 0, 100, 90)
        B = st.number_input("B cutoff", 0, 100, 80)
        C = st.number_input("C cutoff", 0, 100, 70)
        D = st.number_input("D cutoff", 0, 100, 60)

        # Validation: ensure descending order
        if not (A > B > C > D):
            st.warning("Check your cutoffs: They should be in descending order (A > B > C > D).")
            
        cutoffs = [A, B, C, D]

    # Recalculate grades dynamically
    student_grades = {s: get_grade(score, cutoffs) for s, score in student_scores.items()}

    # Plot grade distribution **above** the bump buttons
    plot_grade_distribution(student_grades, cutoffs)

    # Show students near cutoff with bump buttons
    display_near_cutoff_students(student_scores, cutoffs, use_percentage)

    # Export CSV
    export_grades_csv(student_grades)
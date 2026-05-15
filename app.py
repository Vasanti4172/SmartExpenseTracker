import streamlit as st
from database import (
    create_table,
    add_expense,
    get_all_expenses,
    delete_expense,
    update_expense,
    get_total_expense,
    get_expense_count,
    get_category_summary
)
import matplotlib.pyplot as plt
import pandas as pd
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")

# ---------------- INIT ----------------
create_table()

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ---------------- PDF FUNCTION (TOP LEVEL - IMPORTANT) ----------------
def generate_pdf():
    expenses = get_all_expenses()
    total = get_total_expense()
    categories = get_category_summary()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    file_path = temp_file.name

    c = canvas.Canvas(file_path, pagesize=A4)

    y = 800

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y, "SMART EXPENSE REPORT")

    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Total Expense: ₹{total}")
    y -= 20

    c.drawString(50, y, f"Total Transactions: {len(expenses)}")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "CATEGORY SUMMARY:")
    y -= 20

    c.setFont("Helvetica", 11)
    for cat in categories:
        c.drawString(60, y, f"{cat[0]}: ₹{cat[1]}")
        y -= 15

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "EXPENSE DETAILS:")
    y -= 20

    c.setFont("Helvetica", 10)
    for e in expenses:
        c.drawString(60, y, f"{e[1]} - ₹{e[2]} - {e[3]} - {e[4]}")
        y -= 12

        if y < 50:
            c.showPage()
            y = 800

    c.save()

    return file_path


# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add Expense", "View Expenses", "Download PDF"]
)

# ---------------- HEADER ----------------
st.markdown("""
    <div style='text-align:center; padding:10px'>
        <h1 style='color:#1f77b4;'>💰 Smart Expense Tracker</h1>
        <h4 style='color:gray;'>Your personal finance dashboard</h4>
    </div>
    <hr style='border:1px solid #ddd'>
""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":

    st.title("📊 Dashboard")

    total = get_total_expense()
    count = get_expense_count()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Expense", f"₹{total}")
    col2.metric("Transactions", count)
    col3.metric("Avg Expense", f"₹{total/count if count else 0:.2f}")

    st.markdown("---")

    st.subheader("📌 Category Breakdown")

    category_data = get_category_summary()

    if category_data:
        for cat in category_data:
            st.write(f"**{cat[0]}:** ₹{cat[1]}")
    else:
        st.info("No data available")

    st.markdown("---")

    st.subheader("📈 Spending Chart")

    if category_data:
        categories = [x[0] for x in category_data]
        amounts = [x[1] for x in category_data]

        chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Bar Chart"])

        fig, ax = plt.subplots()

        if chart_type == "Pie Chart":
            ax.pie(amounts, labels=categories, autopct="%1.1f%%")
            ax.set_title("Expense Distribution")

        elif chart_type == "Bar Chart":
            ax.bar(categories, amounts)
            ax.set_title("Expense Distribution")

        st.pyplot(fig)

    else:
        st.info("No data to display chart")

# =========================================================
# ADD EXPENSE
# =========================================================
elif page == "Add Expense":

    st.title("➕ Add Expense")

    with st.form("expense_form"):

        title = st.text_input("Expense Title")
        amount = st.number_input("Amount", min_value=0.0)
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Rent", "Other"])
        date = st.date_input("Date")

        submitted = st.form_submit_button("Add Expense")

        if submitted:
            if title and amount:
                add_expense(title, amount, category, str(date))
                st.success("Expense added successfully ✔")
                st.balloons()
                st.rerun()
            else:
                st.error("Please fill all fields")

# =========================================================
# VIEW EXPENSES
# =========================================================
elif page == "View Expenses":

    st.title("📋 View Expenses")

    expenses = get_all_expenses()

    if expenses:

        df = pd.DataFrame(
            expenses,
            columns=["ID", "Title", "Amount", "Category", "Date"]
        )

        st.dataframe(df, use_container_width=True)

        st.markdown("---")

        for expense in expenses:

            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                st.write(f"{expense[1]} - ₹{expense[2]} - {expense[3]} - {expense[4]}")

            with col2:
                if st.button("🗑️ Delete", key=f"del_{expense[0]}"):
                    delete_expense(expense[0])
                    st.rerun()

            with col3:
                if st.button("✏️ Edit", key=f"edit_{expense[0]}"):
                    st.session_state.edit_id = expense[0]
                    st.session_state.edit_data = expense
                    st.rerun()

    else:
        st.info("No expenses found")

    if st.session_state.edit_id is not None:

        st.subheader("✏️ Edit Expense")

        data = st.session_state.edit_data

        with st.form("edit_form"):

            new_title = st.text_input("Title", value=data[1])
            new_amount = st.number_input("Amount", value=float(data[2]))
            new_category = st.selectbox(
                "Category",
                ["Food", "Travel", "Shopping", "Rent", "Other"],
                index=["Food", "Travel", "Shopping", "Rent", "Other"].index(data[3])
            )
            new_date = st.date_input("Date")

            if st.form_submit_button("Update Expense"):

                update_expense(
                    st.session_state.edit_id,
                    new_title,
                    new_amount,
                    new_category,
                    str(new_date)
                )

                st.success("Updated successfully ✔")
                st.session_state.edit_id = None
                st.rerun()

# =========================================================
# PDF DOWNLOAD PAGE
# =========================================================
elif page == "Download PDF":

    st.title("📄 Download Expense Report")

    if st.button("Generate PDF"):

        pdf_path = generate_pdf()

        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇ Download Report",
                f,
                file_name="expense_report.pdf",
                mime="application/pdf"
            )

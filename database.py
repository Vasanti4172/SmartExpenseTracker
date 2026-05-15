import sqlite3

# ---------------- CONNECTION ----------------
def get_connection():
    conn = sqlite3.connect("expense.db")
    return conn


# ---------------- CREATE TABLE ----------------
def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- INSERT EXPENSE ----------------
def add_expense(title, amount, category, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses (title, amount, category, date)
    VALUES (?, ?, ?, ?)
    """, (title, amount, category, date))

    conn.commit()
    conn.close()
def get_all_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    conn.close()
    return rows
def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    conn.commit()
    conn.close()
def update_expense(expense_id, title, amount, category, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE expenses
    SET title = ?, amount = ?, category = ?, date = ?
    WHERE id = ?
    """, (title, amount, category, date, expense_id))

    conn.commit()
    conn.close()

def get_total_expense():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    conn.close()
    return total if total else 0

def get_expense_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]

    conn.close()
    return count

def get_category_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()
    conn.close()
    return data
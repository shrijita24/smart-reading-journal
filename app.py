import streamlit as st
import sqlite3

# -------------------
# Database Functions
# -------------------
def init_db():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT,
            author TEXT,
            note TEXT,
            tags TEXT
        )
    """)
    conn.commit()
    conn.close()
    
def seed_sample_notes():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()

    # Check if table already has data
    c.execute("SELECT COUNT(*) FROM notes")
    count = c.fetchone()[0]

    if count == 0:
        sample_notes = [
            (
                "Atomic Habits",
                "James Clear",
                "Habits are the compound interest of self-improvement. Small changes matter over time.",
                "habits, self-improvement"
            ),
            (
                "Atomic Habits",
                "James Clear",
                "You do not rise to the level of your goals. You fall to the level of your systems.",
                "systems, productivity"
            ),
            (
                "Atomic Habits",
                "James Clear",
                "Every action you take is a vote for the type of person you wish to become.",
                "identity, behavior"
            )
        ]

        c.executemany(
            "INSERT INTO notes (book, author, note, tags) VALUES (?, ?, ?, ?)",
            sample_notes
        )

        conn.commit()

    conn.close()
    


def add_note(book, author, note, tags):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("INSERT INTO notes (book, author, note, tags) VALUES (?, ?, ?, ?)", 
              (book, author, note, tags))
    conn.commit()
    conn.close()

def get_notes():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    rows = c.fetchall()
    conn.close()
    return rows

def search_by_book(book):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE book LIKE ?", ('%' + book + '%',))
    rows = c.fetchall()
    conn.close()
    return rows

# -------------------
# Streamlit App
# -------------------
st.title("📖 Smart Reading Journal (Phase 1)")
st.sidebar.title("Menu")

menu = ["Add Note", "View All Notes", "Search by Book"]
choice = st.sidebar.radio("Navigate", menu)

init_db()  # Initialize database
seed_sample_notes()


if choice == "Add Note":
    st.subheader("✍️ Add a new note")
    book = st.text_input("Book Title")
    author = st.text_input("Author")
    note = st.text_area("Note / Quote")
    tags = st.text_input("Tags (comma-separated)")

    if st.button("Save Note"):
        if book and note:
            add_note(book, author, note, tags)
            st.success("✅ Note saved successfully!")
        else:
            st.error("⚠️ Please enter at least Book Title and Note.")

elif choice == "View All Notes":
    st.subheader("📑 All Notes")
    notes = get_notes()
    st.info("✨ Sample notes are shown for demonstration. You can add your own insights.")
    for row in notes:
        st.markdown(f"**Book:** {row[1]} | **Author:** {row[2]} | **Tags:** {row[4]}")
        st.write(row[3])
        st.markdown("---")

elif choice == "Search by Book":
    st.subheader("🔍 Search Notes by Book")
    search_book = st.text_input("Enter book title")
    if st.button("Search"):
        results = search_by_book(search_book)
        if results:
            for row in results:
                st.markdown(f"**Book:** {row[1]} | **Author:** {row[2]} | **Tags:** {row[4]}")
                st.write(row[3])
                st.markdown("---")
        else:
            st.info("No notes found for this book.")

import streamlit as st
import sqlite3
import os
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LumenNotes",
    page_icon="📚",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .note-card {
        background: white;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #6c63ff;
    }
    .note-card-starred {
        background: #fffbf0;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 4px solid #f4a261;
    }
    .tag-pill {
        display: inline-block;
        background: #e9ecef;
        color: #495057;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 2px 3px;
        font-size: 12px;
        font-weight: 500;
    }
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .stat-number {
        font-size: 36px;
        font-weight: 800;
        color: #6c63ff;
    }
    .stat-label {
        font-size: 13px;
        color: #6c757d;
        margin-top: 4px;
    }
    .ai-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #343a40;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT,
            author TEXT,
            note TEXT,
            tags TEXT,
            starred INTEGER DEFAULT 0
        )
    """)
    # Add starred column if upgrading from old schema
    try:
        c.execute("ALTER TABLE notes ADD COLUMN starred INTEGER DEFAULT 0")
    except:
        pass
    conn.commit()
    conn.close()

def seed_sample_notes():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM notes")
    if c.fetchone()[0] == 0:
        samples = [
            ("Atomic Habits", "James Clear",
             "Habits are the compound interest of self-improvement. Small changes matter over time.",
             "habits, self-improvement", 1),
            ("Atomic Habits", "James Clear",
             "You do not rise to the level of your goals. You fall to the level of your systems.",
             "systems, productivity", 0),
            ("Thinking, Fast and Slow", "Daniel Kahneman",
             "Nothing in life is as important as you think it is, while you are thinking about it.",
             "psychology, decision-making", 1),
            ("Deep Work", "Cal Newport",
             "Clarity about what matters provides clarity about what does not.",
             "focus, productivity", 0),
        ]
        c.executemany(
            "INSERT INTO notes (book, author, note, tags, starred) VALUES (?, ?, ?, ?, ?)",
            samples
        )
        conn.commit()
    conn.close()

def add_note(book, author, note, tags):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("INSERT INTO notes (book, author, note, tags, starred) VALUES (?, ?, ?, ?, 0)",
              (book, author, note, tags))
    conn.commit()
    conn.close()

def get_all_notes():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes ORDER BY starred DESC, id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def search_notes(query, search_type="book"):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    if search_type == "book":
        c.execute("SELECT * FROM notes WHERE book LIKE ? ORDER BY starred DESC", ('%' + query + '%',))
    elif search_type == "tag":
        c.execute("SELECT * FROM notes WHERE tags LIKE ? ORDER BY starred DESC", ('%' + query + '%',))
    elif search_type == "keyword":
        c.execute("SELECT * FROM notes WHERE note LIKE ? ORDER BY starred DESC", ('%' + query + '%',))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_note(note_id):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

def toggle_star(note_id, current):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("UPDATE notes SET starred = ? WHERE id = ?", (0 if current else 1, note_id))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM notes")
    total_notes = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT book) FROM notes")
    total_books = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM notes WHERE starred = 1")
    starred = c.fetchone()[0]
    c.execute("SELECT tags FROM notes")
    all_tags = [row[0] for row in c.fetchall() if row[0]]
    conn.close()
    tag_list = []
    for t in all_tags:
        tag_list.extend([x.strip() for x in t.split(",")])
    top_tags = Counter(tag_list).most_common(5)
    return total_notes, total_books, starred, top_tags

# ── Render note card ──────────────────────────────────────────────────────────
def render_note(row, show_actions=True):
    note_id, book, author, note_text, tags, starred = row
    card_class = "note-card-starred" if starred else "note-card"
    star_icon = "⭐" if starred else "☆"
    tag_pills = ""
    if tags:
        tag_pills = "".join([f"<span class='tag-pill'>#{t.strip()}</span>"
                             for t in tags.split(",") if t.strip()])

    st.markdown(f"""
    <div class='{card_class}'>
        <div style='font-size:13px;color:#6c757d;margin-bottom:6px;'>
            📖 <strong>{book}</strong>
            {f"· <em>{author}</em>" if author else ""}
        </div>
        <div style='font-size:15px;color:#212529;line-height:1.6;margin-bottom:10px;'>
            "{note_text}"
        </div>
        <div>{tag_pills}</div>
    </div>
    """, unsafe_allow_html=True)

    if show_actions:
        col1, col2, col3 = st.columns([1, 1, 6])
        with col1:
            if st.button(f"{star_icon} Star", key=f"star_{note_id}"):
                toggle_star(note_id, starred)
                st.rerun()
        with col2:
            if st.button("🗑️ Delete", key=f"del_{note_id}"):
                delete_note(note_id)
                st.rerun()

# ── AI Insights ───────────────────────────────────────────────────────────────
def get_ai_insight(question, notes_context):
    try:
        from openai import OpenAI
        api_key = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
        if not api_key:
            return None
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a thoughtful reading companion. Based on the user's book notes, provide insightful, concise responses. Be specific and reference the actual notes where possible."},
                {"role": "user", "content": f"Here are my reading notes:\n\n{notes_context}\n\nQuestion: {question}"}
            ],
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return None

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
seed_sample_notes()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 LumenNotes")
    st.markdown("<p style='color:#6c757d;font-size:13px;'>Your AI-powered reading journal</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navigate", ["🏠 Dashboard", "✍️ Add Note", "📑 All Notes", "🔍 Search & Filter", "🤖 AI Insights"])
    st.markdown("---")
    total_notes, total_books, starred_count, _ = get_stats()
    st.markdown(f"**{total_notes}** notes · **{total_books}** books · **{starred_count}** starred")
    st.markdown("---")
    st.markdown("<div style='font-size:12px;color:#adb5bd;text-align:center;'>Built by Shrijita Bhattacharyya<br>Python · SQLite · OpenAI · Streamlit</div>", unsafe_allow_html=True)

# ── Pages ─────────────────────────────────────────────────────────────────────

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if menu == "🏠 Dashboard":
    st.markdown("# 📚 LumenNotes")
    st.markdown("<p style='color:#6c757d;font-size:16px;'>Your personal AI-powered reading journal — capture, organise, and rediscover your best ideas.</p>", unsafe_allow_html=True)
    st.markdown("---")

    total_notes, total_books, starred_count, top_tags = get_stats()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number'>{total_notes}</div>
            <div class='stat-label'>Total Notes</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number'>{total_books}</div>
            <div class='stat-label'>Books Logged</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='stat-card'>
            <div class='stat-number'>{starred_count}</div>
            <div class='stat-label'>Starred Insights</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(" ")

    col_tags, col_starred = st.columns([1, 1], gap="large")

    with col_tags:
        st.markdown("<div class='section-header'>🏷️ Top Tags</div>", unsafe_allow_html=True)
        if top_tags:
            for tag, count in top_tags:
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                            background:white;border-radius:10px;padding:10px 16px;
                            margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,0.06);'>
                    <span style='color:#495057;font-size:14px;'>#{tag}</span>
                    <span style='background:#6c63ff;color:white;border-radius:20px;
                                 padding:2px 10px;font-size:12px;font-weight:600;'>{count}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No tags yet — add some notes!")

    with col_starred:
        st.markdown("<div class='section-header'>⭐ Starred Notes</div>", unsafe_allow_html=True)
        all_notes = get_all_notes()
        starred_notes = [n for n in all_notes if n[5] == 1]
        if starred_notes:
            for row in starred_notes[:3]:
                render_note(row, show_actions=False)
        else:
            st.info("Star your favourite insights to see them here!")

# ── ADD NOTE ──────────────────────────────────────────────────────────────────
elif menu == "✍️ Add Note":
    st.markdown("# ✍️ Add a New Note")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        book = st.text_input("📖 Book Title *", placeholder="e.g. Atomic Habits")
        author = st.text_input("👤 Author", placeholder="e.g. James Clear")
    with col2:
        tags = st.text_input("🏷️ Tags (comma-separated)", placeholder="e.g. habits, productivity, mindset")

    note = st.text_area("💡 Note / Quote *", placeholder="Type your insight, quote, or key takeaway here...", height=180)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("💾 Save Note", use_container_width=True, type="primary"):
            if book.strip() and note.strip():
                add_note(book.strip(), author.strip(), note.strip(), tags.strip())
                st.success("✅ Note saved successfully!")
                st.balloons()
            else:
                st.error("⚠️ Book title and note are required.")

# ── ALL NOTES ─────────────────────────────────────────────────────────────────
elif menu == "📑 All Notes":
    st.markdown("# 📑 All Notes")
    st.markdown("---")

    all_notes = get_all_notes()
    if not all_notes:
        st.info("No notes yet — add your first one!")
    else:
        st.markdown(f"<p style='color:#6c757d;'>{len(all_notes)} notes total</p>", unsafe_allow_html=True)
        for row in all_notes:
            render_note(row)

# ── SEARCH & FILTER ───────────────────────────────────────────────────────────
elif menu == "🔍 Search & Filter":
    st.markdown("# 🔍 Search & Filter")
    st.markdown("---")

    search_type = st.radio("Search by", ["Book title", "Tag", "Keyword in note"], horizontal=True)
    query = st.text_input("Enter search term", placeholder="e.g. habits / productivity / decisions...")

    if query.strip():
        type_map = {"Book title": "book", "Tag": "tag", "Keyword in note": "keyword"}
        results = search_notes(query.strip(), type_map[search_type])
        st.markdown(f"<p style='color:#6c757d;'>{len(results)} result(s) found</p>", unsafe_allow_html=True)
        if results:
            for row in results:
                render_note(row)
        else:
            st.info("No notes found. Try a different search term.")

# ── AI INSIGHTS ───────────────────────────────────────────────────────────────
elif menu == "🤖 AI Insights":
    st.markdown("# 🤖 AI Insights")
    st.markdown("---")

    api_key = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

    if not api_key:
        st.markdown("""
        <div class='ai-box'>
            <div style='font-size:20px;font-weight:700;margin-bottom:8px;'>🔑 Set up your OpenAI API Key</div>
            <div style='font-size:14px;opacity:0.9;'>To enable AI-powered insights across your reading notes, add your OpenAI API key to Streamlit Cloud secrets.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### How to set it up:")
        st.markdown("""
1. Go to your app on **Streamlit Cloud**
2. Click **⋮ (three dots)** → **Settings** → **Secrets**
3. Add this:
```
OPENAI_API_KEY = "sk-your-key-here"
```
4. Click **Save** — the app will restart automatically
        """)
        st.info("Once set up, you'll be able to ask questions like: *'What are the common themes across my books?'* or *'Summarise my notes on productivity.'*")
    else:
        all_notes = get_all_notes()
        if not all_notes:
            st.info("Add some notes first — then come back to ask AI about them!")
        else:
            notes_context = "\n\n".join([
                f"Book: {r[1]} by {r[2]}\nNote: {r[3]}\nTags: {r[4]}"
                for r in all_notes
            ])

            st.markdown("Ask anything about your reading notes:")

            suggested = [
                "What are the common themes across my books?",
                "Which book has the most actionable insights?",
                "Summarise my notes on productivity.",
                "What should I read next based on my notes?"
            ]
            selected = st.selectbox("💡 Try a suggested question or type your own below:", [""] + suggested)
            question = st.text_input("Or type your own question:", value=selected if selected else "")

            if st.button("✨ Ask AI", type="primary") and question.strip():
                with st.spinner("Thinking..."):
                    answer = get_ai_insight(question, notes_context)
                    if answer:
                        st.markdown(f"""
                        <div class='ai-box'>
                            <div style='font-size:13px;opacity:0.8;margin-bottom:8px;'>🤖 AI Response</div>
                            <div style='font-size:15px;line-height:1.7;'>{answer}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Something went wrong. Check your API key in Streamlit secrets.")

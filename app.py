import streamlit as st
import sqlite3
import os
from collections import Counter, defaultdict

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
    .book-header {
        background: white;
        border-radius: 14px 14px 0 0;
        padding: 16px 22px 12px 22px;
        border-left: 5px solid #6c63ff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-top: 20px;
    }
    .book-title {
        font-size: 18px;
        font-weight: 700;
        color: #343a40;
    }
    .book-author {
        font-size: 13px;
        color: #6c757d;
        margin-top: 2px;
    }
    .note-item {
        background: #fafafa;
        border-left: 3px solid #dee2e6;
        padding: 14px 18px;
        margin: 0 0 2px 0;
        font-size: 14px;
        color: #212529;
        line-height: 1.6;
    }
    .note-item-starred {
        background: #fffbf0;
        border-left: 3px solid #f4a261;
        padding: 14px 18px;
        margin: 0 0 2px 0;
        font-size: 14px;
        color: #212529;
        line-height: 1.6;
    }
    .book-footer {
        background: white;
        border-radius: 0 0 14px 14px;
        padding: 8px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 6px;
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
            ("Atomic Habits", "James Clear",
             "Every action you take is a vote for the type of person you wish to become.",
             "identity, behavior", 0),
            ("Thinking, Fast and Slow", "Daniel Kahneman",
             "Nothing in life is as important as you think it is, while you are thinking about it.",
             "psychology, decision-making", 1),
            ("Thinking, Fast and Slow", "Daniel Kahneman",
             "A reliable way to make people believe in falsehoods is frequent repetition.",
             "psychology, bias", 0),
            ("Deep Work", "Cal Newport",
             "Clarity about what matters provides clarity about what does not.",
             "focus, productivity", 0),
            ("Deep Work", "Cal Newport",
             "To produce at your peak level you need to work for extended periods with full concentration.",
             "focus, deep work", 1),
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
    c.execute("SELECT * FROM notes ORDER BY book, starred DESC, id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def search_notes(query, search_type="book"):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    if search_type == "book":
        c.execute("SELECT * FROM notes WHERE book LIKE ? ORDER BY book, starred DESC", ('%' + query + '%',))
    elif search_type == "tag":
        c.execute("SELECT * FROM notes WHERE tags LIKE ? ORDER BY book, starred DESC", ('%' + query + '%',))
    elif search_type == "keyword":
        c.execute("SELECT * FROM notes WHERE note LIKE ? ORDER BY book, starred DESC", ('%' + query + '%',))
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
        tag_list.extend([x.strip() for x in t.split(",") if x.strip()])
    top_tags = Counter(tag_list).most_common(5)
    return total_notes, total_books, starred, top_tags

# ── Group notes by book and render ───────────────────────────────────────────
def group_by_book(rows):
    grouped = defaultdict(lambda: {"author": "", "notes": []})
    for row in rows:
        note_id, book, author, note_text, tags, starred = row
        grouped[book]["author"] = author
        grouped[book]["notes"].append((note_id, note_text, tags, starred))
    return grouped

def render_book_group(book, author, notes, show_actions=True):
    note_count = len(notes)
    st.markdown(f"""
    <div class='book-header'>
        <div class='book-title'>📖 {book}
            <span style='font-size:12px;font-weight:400;color:#adb5bd;margin-left:8px;'>
                {note_count} note{"s" if note_count != 1 else ""}
            </span>
        </div>
        {"<div class='book-author'>by " + author + "</div>" if author else ""}
    </div>
    """, unsafe_allow_html=True)

    for note_id, note_text, tags, starred in notes:
        star_icon = "⭐" if starred else "☆"
        card_class = "note-item-starred" if starred else "note-item"
        tag_pills = "".join([f"<span class='tag-pill'>#{t.strip()}</span>"
                             for t in tags.split(",") if t.strip()]) if tags else ""
        st.markdown(f"""
        <div class='{card_class}'>
            <div>"{note_text}"</div>
            <div style='margin-top:8px;'>{tag_pills}</div>
        </div>
        """, unsafe_allow_html=True)

        if show_actions:
            col1, col2, col_space = st.columns([0.7, 0.7, 6])
            with col1:
                if st.button(f"{star_icon}", key=f"star_{note_id}", help="Star this note"):
                    toggle_star(note_id, starred)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{note_id}", help="Delete this note"):
                    delete_note(note_id)
                    st.rerun()

    st.markdown("<div class='book-footer'></div>", unsafe_allow_html=True)

# ── AI Insights ───────────────────────────────────────────────────────────────
def get_ai_insight(question, notes_context):
    try:
        from openai import OpenAI
        api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))
        if not api_key:
            return None
        # Groq exposes an OpenAI-compatible endpoint, so the same OpenAI SDK
        # works here — just pointed at Groq's base URL with a Groq key.
        # Free tier, no billing required: https://console.groq.com
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a thoughtful reading companion. Based on the user's book notes, provide insightful, concise responses. Be specific and reference actual notes where possible."},
                {"role": "user", "content": f"Here are my reading notes:\n\n{notes_context}\n\nQuestion: {question}"}
            ],
            max_tokens=400
        )
        return response.choices[0].message.content
    except:
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
    st.markdown("<div style='font-size:12px;color:#adb5bd;text-align:center;'>Built by Shrijita Bhattacharyya<br>Python · SQLite · Groq · Streamlit</div>", unsafe_allow_html=True)

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if menu == "🏠 Dashboard":
    st.markdown("# 📚 LumenNotes")
    st.markdown("<p style='color:#6c757d;font-size:16px;'>Your personal AI-powered reading journal — capture, organise, and rediscover your best ideas.</p>", unsafe_allow_html=True)
    st.markdown("---")

    total_notes, total_books, starred_count, top_tags = get_stats()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{total_notes}</div><div class='stat-label'>Total Notes</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{total_books}</div><div class='stat-label'>Books Logged</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='stat-card'><div class='stat-number'>{starred_count}</div><div class='stat-label'>Starred Insights</div></div>", unsafe_allow_html=True)

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
            grouped = group_by_book(starred_notes)
            for book, data in grouped.items():
                render_book_group(book, data["author"], data["notes"], show_actions=False)
        else:
            st.info("Star your favourite insights to see them here!")

# ── ADD NOTE ──────────────────────────────────────────────────────────────────
elif menu == "✍️ Add Note":
    st.markdown("# ✍️ Add a New Note")
    st.markdown("---")

    # Suggest existing book titles
    all_notes = get_all_notes()
    existing_books = sorted(list(set([n[1] for n in all_notes])))

    col1, col2 = st.columns(2)
    with col1:
        if existing_books:
            book_choice = st.selectbox("📖 Book Title *",
                                       ["+ Add new book..."] + existing_books)
            if book_choice == "+ Add new book...":
                book = st.text_input("Enter new book title", placeholder="e.g. The Psychology of Money")
            else:
                book = book_choice
                # Auto-fill author
                author_match = next((n[2] for n in all_notes if n[1] == book_choice), "")
                st.text_input("👤 Author (auto-filled)", value=author_match, disabled=True, key="auto_author")
                author = author_match
        else:
            book = st.text_input("📖 Book Title *", placeholder="e.g. Atomic Habits")

    with col2:
        if not existing_books or book_choice == "+ Add new book...":
            author = st.text_input("👤 Author", placeholder="e.g. James Clear")
        tags = st.text_input("🏷️ Tags (comma-separated)", placeholder="e.g. habits, productivity")

    note = st.text_area("💡 Note / Quote *",
                        placeholder="Type your insight, quote, or key takeaway here...",
                        height=180)

    if st.button("💾 Save Note", use_container_width=True, type="primary"):
        if book.strip() and note.strip():
            add_note(book.strip(), author.strip() if 'author' in locals() else "", note.strip(), tags.strip())
            st.success("✅ Note saved!")
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
        total_notes, total_books, _, _ = get_stats()
        st.markdown(f"<p style='color:#6c757d;'>{total_notes} notes across {total_books} books</p>",
                    unsafe_allow_html=True)
        grouped = group_by_book(all_notes)
        for book, data in grouped.items():
            render_book_group(book, data["author"], data["notes"], show_actions=True)

# ── SEARCH & FILTER ───────────────────────────────────────────────────────────
elif menu == "🔍 Search & Filter":
    st.markdown("# 🔍 Search & Filter")
    st.markdown("---")

    search_type = st.radio("Search by", ["Book title", "Tag", "Keyword in note"], horizontal=True)
    query = st.text_input("Enter search term", placeholder="e.g. habits / productivity / decisions...")

    if query.strip():
        type_map = {"Book title": "book", "Tag": "tag", "Keyword in note": "keyword"}
        results = search_notes(query.strip(), type_map[search_type])
        st.markdown(f"<p style='color:#6c757d;'>{len(results)} result(s) found</p>",
                    unsafe_allow_html=True)
        if results:
            grouped = group_by_book(results)
            for book, data in grouped.items():
                render_book_group(book, data["author"], data["notes"], show_actions=True)
        else:
            st.info("No notes found. Try a different search term.")

# ── AI INSIGHTS ───────────────────────────────────────────────────────────────
elif menu == "🤖 AI Insights":
    st.markdown("# 🤖 AI Insights")
    st.markdown("---")

    api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

    if not api_key:
        st.markdown("""
        <div class='ai-box'>
            <div style='font-size:20px;font-weight:700;margin-bottom:8px;'>🔑 Set up your Groq API Key</div>
            <div style='font-size:14px;opacity:0.9;'>Add your key to Streamlit Cloud secrets to unlock AI-powered insights across your reading notes — free, no credit card required.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("#### How to set it up:")
        st.markdown("""
1. Get a free key at **[console.groq.com](https://console.groq.com)** — no credit card required
2. Go to your app on **Streamlit Cloud**
3. Click **⋮ (three dots)** → **Settings** → **Secrets**
4. Add:
```
GROQ_API_KEY = "gsk_your-key-here"
```
5. Click **Save** — app restarts automatically ✅
        """)
        st.info("Once set up, ask things like: *'What are the common themes across my books?'* or *'Summarise my notes on productivity.'*")
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
            selected = st.selectbox("💡 Try a suggested question:", [""] + suggested)
            question = st.text_input("Or type your own:", value=selected if selected else "")

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

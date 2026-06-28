# LumenNotes 📚
**An AI-powered reading journal for non-fiction thinkers.**

LumenNotes helps you capture, organise, and retrieve insights from the books you read — built end-to-end with Python, SQLite, and Streamlit, with an AI layer powered by the OpenAI GPT-4 API.

> 🚀 **Currently upgrading to a full RAG architecture** — Groq + LangChain + FAISS for semantic search and context-aware retrieval across your entire reading history.

🔗 [**Try it live →**](https://lumennotes.streamlit.app/)
---

## ✨ Features

- 📝 Add and organise book notes with tags
- 🔍 Search notes by book title
- 🗄️ Persistent local storage via a normalised SQLite schema
- 🤖 GPT-4 API integration for AI-powered reading insights
- ☁️ Deployed on Streamlit Cloud — zero local setup required · [Live App →](https://lumennotes.streamlit.app/)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite |
| AI Layer | OpenAI GPT-4 API |
| Deployment | Streamlit Cloud |

---

## 🗂️ Project Structure

```
lumennotes/
├── app.py              # Main Streamlit application
├── check_db.py         # Database inspection and schema utilities
├── requirements.txt    # Dependencies
├── .gitignore
└── README.md
```

---

## 🚀 Run Locally

```bash
git clone https://github.com/shrijita24/lumennotes
cd lumennotes
pip install -r requirements.txt
streamlit run app.py
```

Add your OpenAI API key to a `.env` file:
```
OPENAI_API_KEY=your_key_here
```

---

## 🔭 Roadmap — RAG Upgrade (In Progress)

The next version of LumenNotes moves from keyword search to **semantic retrieval** using a full RAG pipeline:

| Component | Technology |
|---|---|
| LLM Backend | Groq (llama3) |
| Orchestration | LangChain |
| Vector Store | FAISS |
| Embeddings | HuggingFace / OpenAI |

**What this unlocks:**
- Ask questions across your entire reading history ("What have I read about decision-making?")
- Semantic similarity search — find related notes even without exact keyword matches
- Context-aware AI responses grounded in your own notes, not hallucinated

---

## 👩‍💻 Author

**Shrijita Bhattacharyya**
B.Tech CS, IEM Kolkata | LLM Post-Training Intern (Ethara AI) | AI/ML Engineer

[LinkedIn](https://www.linkedin.com/in/shrijita-bhattacharyya/) · [GitHub](https://github.com/shrijita24) · [Portfolio](https://shrijitabhattacharyya-portfolio.netlify.app/)

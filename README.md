# CineBot - Intelligent Movie Recommendation Chatbot

CineBot is an intelligent, interactive movie recommendation chatbot that maps natural language requests (mood, genre, ratings, tone) to high-quality movie recommendations. Recommendations are fetched using an LLM, cross-referenced and enriched against a static IMDb/movies CSV catalog, and continuously adapted based on thumbs-up/down session feedback.

---

## Architecture Diagram

```text
               +----------------------------------------+
               |           React Frontend UI            |
               |  (Generates session_id, displays cards)|
               +-------------------+--------------------+
                                   |
                      POST /chat   |   POST /feedback
                    (message, sId) |   (title, liked, sId)
                                   v
               +-------------------+--------------------+
               |         FastAPI Backend Router         |
               |          (app/main.py, port 8000)      |
               +-------------------+--------------------+
                                   |
                                   |  In-Memory Memory & Feedback Store
                                   v
               +-------------------+--------------------+
               |         LangChain Pipeline Layer       |
               |                                        |
               |  1. Preference Extraction Chain        |
               |     (Extracts mood, genre, threshold)  |
               |                                        |
               |  2. Recommendation Generation Chain    |
               |     (Queries Groq API with context +   |
               |      session feedback liked/disliked)  |
               +-------------------+--------------------+
                                   |
                                   |  Proposes Titles & Justifications
                                   v
               +-------------------+--------------------+
               |        Recommendation Service          |
               |                                        |
               |  1. Fuzzy-matches titles via RapidFuzz |
               |     (against app/data/movies.csv)      |
               |  2. Enriches with metadata (rating,    |
               |     genre, year, plot overview)        |
               +-------------------+--------------------+
                                   |
                    Matched Cards  |  (JSON response)
                                   v
                       [Conversational Reply]
                       [Enriched Movie Cards]
```

---

## Sourcing & Dataset Attribution
CineBot uses a static dataset containing **999 movies** sourced from the public **IMDb Top 1000** Kaggle dataset.
- **Source Columns**: `Series_Title`, `Genre`, `Released_Year`, `IMDB_Rating`, `Overview`.
- **Location**: `backend/app/data/movies.csv` (saved in cleaned format with columns `title, genre, rating, year, overview`).

---

## Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **LLM Orchestration**: LangChain LCEL & `ConversationBufferMemory`
- **LLM Inference**: Groq API (`llama-3.3-70b-versatile`)
- **Database**: Single-loaded static Pandas CSV DataFrame (Memory Singleton)
- **Frontend**: React (Vite) + Plain CSS (Premium Dark Mode Styling)
- **Identity**: Session-scoped using in-memory random UUID `session_id`.

---

## Setup & Running Instructions

### Prerequisites
- Python 3.11+
- Node.js (v18+)
- Groq API Key (get one from [console.groq.com](https://console.groq.com/))

### 1. Backend Setup
1. Navigate to the `backend/` directory.
2. Create a `.env` file from the example template:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```
4. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
   The backend will start running at `http://127.0.0.1:8000`.

### 2. Frontend Setup
1. Navigate to the `frontend/` directory.
2. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
3. Install frontend npm dependencies:
   ```bash
   npm install
   ```
4. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   The frontend will start running at `http://localhost:5173`. Open this URL in your web browser.

---

## Standalone Verification Scripts & Unit Tests

CineBot includes two test scripts to verify modules independently of the API endpoints:

1. **Verify CSV Dataset and Data Loader**:
   ```bash
   python backend/tests/test_data_loader.py
   ```
   *Tests CSV loading, basic searches, and case/year-insensitive fuzzy title matching.*

2. **Verify LangChain + Groq Pipeline**:
   ```bash
   python backend/tests/test_pipeline.py
   ```
   *Runs preference extraction, Groq recommendation generation, and conversational phrasing templates.*

3. **Run Recommendation Service Unit Tests**:
   ```bash
   python backend/tests/test_recommender.py
   ```
   *Asserts metadata enrichment, non-catalog movie filtering, and disliked movies exclusion.*

---

## Sample Conversational Flows

### Chat 1: Initial Recommendation Request
- **User**: "I want a funny movie for a lazy Sunday evening"
- **CineBot**: "I've got just the thing to tickle your funny bone - some hilarious comedies with top-notch ratings that are sure to put a smile on your face! Here are my top picks for you:"
- **Movie Cards Displayed**:
  - *The Hangover* (2009, Rating: 7.7) - "A hilarious comedy film with a high rating, matching your preference for funny movies."
  - *Up* (2009, Rating: 8.2) - "A coming-of-age comedy classic with a high rating, known for its funny and relatable storyline."

### Chat 2: User Thumbs Down (Feedback Logging)
- **User Action**: Clicks Thumbs Down on *The Hangover* card.
- **Under-the-hood**: POSTs feedback to `/feedback` mapping `The Hangover` to the disliked list for the session.

### Chat 3: Requesting More Recommendations
- **User**: "recommend another comedy movie with rating above 8"
- **CineBot**: "Here are some other highly-rated comedies for you! Since you disliked *The Hangover*, I've leaned into more lighthearted, animated, and smart family comedies instead."
- **Movie Cards Displayed**:
  - *Up* (2009, Rating: 8.2)
  - *Monty Python and the Holy Grail* (1975, Rating: 8.2)
  - *(Note: The Hangover is completely excluded from recommendations)*

---

## Architecture Limitations & Future Enhancements
- **In-Memory Storage**: Memory buffers and feedback history are stored in-memory in dictionary variables. In production, this should be backed by **Redis** or a relational database so session context persists across server restarts.
- **Session Identity Reset**: Identity is tied to a client-side generated UUID stored in React state. Refreshing the browser page resets the `session_id`, starting a fresh conversation. Adding a user authentication layer (e.g., Auth0 or JWT) and persistent accounts would maintain memory long-term.

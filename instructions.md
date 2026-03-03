# 📘 Product Requirements Document (PRD)

## Product Name
AI Tutor – Personal AI & ML Learning Assistant

---

## 1. Overview

AI Tutor is a web-based chatbot application built using Streamlit and OpenRouter API.  
It acts as a structured AI professor that teaches Artificial Intelligence concepts interactively.

The product is designed for:
- Engineering students
- Beginners learning AI
- Self-learners
- Interview preparation

---

## 2. Problem Statement

Students struggle with:
- Understanding AI concepts clearly
- Finding structured explanations
- Getting interactive quizzes
- Having a personalized AI mentor

Existing chatbots give generic answers without structured teaching.

---

## 3. Solution

Build a Streamlit-based AI Tutor that:

- Explains AI topics clearly
- Adapts to user level (Beginner / Intermediate / Advanced)
- Gives structured answers:
  1. Simple Explanation
  2. Real-world Example
  3. Mathematical Explanation
  4. Quiz Questions
  5. Suggested Next Topic
- Maintains conversation memory
- Tracks learning progress

---

## 4. Goals

### Primary Goals
- Provide structured AI learning
- Enable interactive tutoring
- Maintain chat memory
- Use free OpenRouter models

### Secondary Goals
- Portfolio-worthy project
- Deployable on Streamlit Cloud
- Extendable to RAG system later

---

## 5. Target Users

- First-year engineering students
- AI beginners
- Interview aspirants
- College students preparing for placements

---

## 6. Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### API
- OpenRouter Chat Completions API

### Model
- mistralai/mistral-7b-instruct (Free Tier)

### Hosting
- GitHub Codespaces
- Streamlit Cloud

---

## 7. Functional Requirements

### 7.1 Chat Interface
- Text input field
- Send button
- Display formatted AI response

### 7.2 Learning Level Selector
Dropdown:
- Beginner
- Intermediate
- Advanced

System prompt adapts explanation depth.

### 7.3 Structured Response Format
Every response must include:

1. Simple Explanation
2. Real-world Example
3. Mathematical Explanation
4. 2 Quiz Questions
5. Suggested Next Topic

### 7.4 Conversation Memory
- Store messages in `st.session_state`
- Maintain context throughout session

### 7.5 Error Handling
- Handle API failures
- Handle invalid responses
- Show user-friendly error messages

### 7.6 Secure API Key
- Store API key using environment variable
- Do NOT hardcode API key

---

## 8. Non-Functional Requirements

- Fast response (< 10 seconds typical)
- Clean minimal UI
- Lightweight deployment
- Mobile responsive (basic Streamlit support)
- No database required (session-based memory only)

---

## 9. System Architecture

User
  ↓
Streamlit UI
  ↓
OpenRouter API
  ↓
LLM (Mistral 7B)

---

## 10. User Flow

1. User opens app
2. Selects learning level
3. Enters AI topic (e.g., "Neural Networks")
4. AI generates structured teaching response
5. User answers quiz
6. AI continues conversation
7. Session memory retained

---

## 11. Future Enhancements (Phase 2)

- PDF Upload (RAG)
- Learning Progress Tracker
- Topic Roadmap Generator
- Quiz Evaluation Scoring
- Authentication System
- Save Chat History
- Multi-model selection
- Deployment as SaaS

---

## 12. Deployment Plan

### Local (Codespaces)
- Set environment variable:
  OPENROUTER_API_KEY
- Install requirements
- Run Streamlit

### Production
- Deploy via Streamlit Cloud
- Add secret key in dashboard
- Connect GitHub repository

---

## 13. Success Metrics

- Users can understand AI concepts clearly
- Structured teaching format maintained
- Zero hardcoded secrets
- Deployable public link
- Works with free OpenRouter model

---

## 14. Risks & Constraints

- Free API rate limits
- Cold start latency
- No persistent database
- Model response variability

Mitigation:
- Handle API errors
- Keep prompts structured
- Add retry logic if needed

---

## 15. Versioning

v1.0
- Basic AI tutor
- Level selector
- Structured answers
- Memory support

v2.0 (Future)
- RAG
- Progress tracking
- Multi-user system
- SaaS deployment

---

# End of PRDp

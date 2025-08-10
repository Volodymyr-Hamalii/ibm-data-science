# CLAUDE.md

## 🧠 Project Purpose

This project is an AI-powered hotel recommendation assistant built with **FastAPI**, **Elasticsearch**, and a **Retrieval-Augmented Generation (RAG)** pipeline. It allows users to search for hotels using natural language queries. The system returns relevant hotel recommendations based on semantic search over hotel descriptions and features.

The goal is to gain practical experience with:

- FastAPI for microservice architecture
- RAG pipelines using vector embeddings and LLMs
- Elasticsearch for vector similarity search
- LangChain for orchestration
- OpenAI and Claude for language understanding/generation

---

## 🗂️ Project Structure

hotel-assistant/
├── app/
│ ├── api/ # FastAPI endpoints
│ │ └── endpoints/
│ │ └── hotels.py
│ ├── core/ # Configs and shared clients
│ │ ├── config.py # Loads .env settings
│ │ └── es_client.py # Elasticsearch client with auth
│ ├── models/ # Pydantic models
│ │ └── hotel.py
│ ├── services/ # Business logic
│ │ └── rag_service.py # RAG flow: embed → search → return
│ └── main.py # FastAPI app entry point
├── .env # Environment variables
├── CLAUDE.md # Instructions for Claude Code
├── Dockerfile # App containerization
├── requirements.txt # Python dependencies

---

## ⚙️ Technologies & Libraries

| Layer             | Tools                                            |
| ----------------- | ------------------------------------------------ |
| API Framework     | FastAPI                                          |
| Vector Store      | Elasticsearch (dense_vector + cosine similarity) |
| Embeddings        | OpenAI (`text-embedding-3-small`) or HuggingFace |
| RAG Orchestration | LangChain                                        |
| LLM Interface     | Claude (for generation), OpenAI (for embedding)  |
| Auth              | Basic Auth for Elasticsearch                     |
| Config            | `pydantic_settings` with `.env` loading          |

---

## 🔍 How the AI Assistant Works

1. User sends a natural language query (e.g. “Hotel near beach with free parking”).
2. Query is embedded via `OpenAIEmbeddings` (LangChain).
3. The embedding is used to perform vector similarity search in Elasticsearch.
4. Top matching hotel documents are returned.
5. (Optional) Claude can re-rank or summarize the results.
6. FastAPI returns the structured list of hotels to the user.

---

## 📌 Claude Use Cases

Claude can assist with:

- Writing or updating FastAPI routes and Pydantic models
- Generating custom prompt templates or summaries
- Improving or testing the RAG pipeline
- Debugging Elasticsearch queriesРш
- Suggesting improvements to LangChain usage
- Writing infrastructure (e.g., Docker, IaC templates)
- Extending the assistant to support multi-turn conversations or personalization

---

## 🧪 Example Queries for Claude

- "Create a new endpoint that returns hotels grouped by country"
- "Write a test case for `recommend_hotels` function"
- "Explain how to extend this to use Claude as the generator instead of OpenAI"
- "Refactor the `rag_service.py` to allow dynamic model switching"
- "Write a prompt template to generate a friendly hotel summary from metadata"

---

## ✅ Environment Variables (.env)

```env
ES_URL=http://localhost:9200
ES_INDEX=hotels
OPENAI_API_KEY=openai_key
```

# SHL Recommender System

This project is a content-based recommendation system that suggests suitable SHL assessments based on a job description. It utilizes sentence embeddings to represent job descriptions and assessment summaries, and then performs similarity matching using cosine similarity.

## 🚀 Features

- Semantic retrieval using `BAAI/bge-large-en-v1.5` model.
- FastAPI backend for recommendation serving.
- Frontend built to accept job descriptions and display assessment recommendations.
- Summarization of long descriptions for concise matching.

## 🛠️ Tech Stack

- **FastAPI**: Backend framework for serving the API.
- **Sentence-Transformers**: For embedding generation.
- **OpenAI Gemini Pro (via PaLM or similar)**: Used to extract structured data from job descriptions.
- **Pandas**: For data wrangling.
- **Render/Vercel**: Deployment of backend and frontend respectively.

## 🧠 Model

- Embedding Model: `BAAI/bge-large-en-v1.5`
- Similarity Metric: Cosine Similarity

## 🧪 Evaluation

We used **Mean Average Precision at K (MAP@K)** to evaluate recommendation quality. This metric captures how well the top-K recommendations match ground truth labels. We validated results by measuring overlap between recommended assessments and expected job functions.


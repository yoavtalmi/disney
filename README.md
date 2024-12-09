# Disney FAQ Answering System

This repository demonstrates a scalable, real-world implementation of a **Retrieval-Augmented Generation (RAG)** system designed for answering frequently asked questions (FAQs) from the Disney Experience website. This system combines web scraping, semantic search (via FAISS), and generative AI to provide answers based on a context-aware model.

---

## Table of Contents

1. [Motivation and Objectives](#motivation-and-objectives)
2. [Folder Structure](#folder-structure)
3. [Setup and Installation](#setup-and-installation)
4. [Usage](#usage)
5. [Thought Process and Trade-offs](#thought-process-and-trade-offs)
6. [Future Improvements](#future-improvements)
7. [License](#license)

---

## Motivation and Objectives

This repository was created as part of a **hiring process for Disney** to showcase technical proficiency in building scalable, production-ready systems. The goal is to demonstrate:
- The ability to scrape, structure, and utilize Disney's FAQ data for an AI-powered query-answering system.
- A deep understanding of **retrieval-based question answering** and the trade-offs in implementation.
- A robust deployment pipeline using **Docker** for portability and ease of use.

By integrating FAISS for similarity search and OpenAI's GPT-3.5-turbo for context-aware responses, this system achieves a balance between scalability and precision, even for large datasets.

---

## Folder Structure

```plaintext
disney/
├── src/
│   ├── __init__.py
│   ├── disney_constants.py          # Dataclass for all constants in the repo.
│   ├── scrape_faq.py                # Script for scraping FAQ data and saving to SQLite.
│   ├── vectorizing.py               # Script for creating a FAISS table and mappings.
│   ├── generating_answers.py        # QueryFAQ class with answer generation.
├── data/
│   ├── disney_faq.db                # SQLite DB with FAQs and mappings.
│   ├── faq_index.faiss              # FAISS table of embedded FAQ questions.
├── .env                             # Environment file for OpenAI credentials.
├── Dockerfile                       # Dockerfile for containerizing the system.
├── server.py                        # Flask API server for handling queries.
├── requirements.txt                 # Python dependencies.
```

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- Docker

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yoavtalmi/disney-faq.git
   cd disney-faq
   ```


2. Build the Docker image:
   ```bash
   docker build -t disney-faq .
   ```

3. Run the container:
   - To use pre-saved data (Recommended):
     ```bash
     docker run -d -p 8000:8000 --env RUN_SETUP=false disney-faq
     ```
   - To recreate the database and FAISS table. Note: This will take 20 minutes more to start up due to scraping and vectorizing data
     ```bash
     docker run -d -p 8000:8000 --env RUN_SETUP=true disney-faq
     ```

---

## Usage

Send a POST request to the server:

### Example Query
```bash
curl -X POST "http://127.0.0.1:8000/query" \
-H "Content-Type: application/json" \
-d '{"question": "What is the smoking policy at Disney Resort hotels?"}'
```

### Example Response
```json
{
  "question": "What is the smoking policy at Disney Resort hotels?",
  "answer": "Disney Resort hotels allow smoking only in designated areas."
}
```

---

## Thought Process and Trade-offs

### Key Design Decisions
1. **Scraping Disney Experience FAQ**:
   - Scraping the Disney website for FAQ data ensures the system is up-to-date with the latest information.
   - SQLite is used for storing the scraped data due to its simplicity and compatibility with FAISS.
   - While the Disney Experience FAQ was chosen for this project, the system can be adapted to any website with question and answer pairs.

2. **FAISS for Semantic Search**:
    - FAISS is chosen for its speed and efficiency in handling large-scale similarity searches.
    - The system uses FAISS to index the embedded FAQ questions and retrieve the most similar questions for a given query.
    - The default embedding model is `sentence-transformers/paraphrase-MiniLM-L6-v2`, which balances performance and accuracy.
    - The questions and answers are not saved on FAISS index to optimize memory usage and speed.

3. **Answer Generation**:
    - OpenAI's GPT-3.5-turbo is used for generating context-aware answers to the queries as a default model.
    - Other OpenAI models can be used based on cost, performance, and privacy requirements.
    - A value error if the query is too short or too long is raised to ensure the query is valid.
    - By selecting the top k (3 currently) most similar questions, we build a context from the questions and corresponding answers to generate the response.
    - There is a threshold for the similarity score to ensure the generated answer is relevant.
    - If no relevant questions are found, a default response is returned: "I'm sorry, I don't have an answer to that question."
    - If according to the LLM the context is not relevant, a default response is returned: "I'm sorry, I don't have an answer to that question."


4. **Pre-saved vs. Recreated Data**:
   - The `RUN_SETUP` environment variable allows users to run the system with pre-saved FAISS and SQLite data for faster deployment or recreate it when scraping is necessary.

5. **Trade-offs**:
   - **FAISS over Vector Databases**: FAISS is fast and lightweight but lacks distributed capabilities, unlike Pinecone or Weaviate.
   - **GPT-3.5-turbo**: Chosen for cost-effectiveness while providing reliable responses. Open-source models can be explored for cost savings or privacy concerns.

6. **Scalability**:
   - SQLite and FAISS are ideal for small to medium-sized datasets. For larger datasets, distributed databases (e.g., PostgreSQL) and vector search engines (e.g., Pinecone) can be introduced.
   - Dockerization ensures easy deployment and scaling across multiple instances.

7. **Logging**:
   - Basic logging is implemented for tracking API requests and responses, with emphasis on performance in order to track the data flow and identify potential bottlenecks.

---

## Future Improvements

1. **Scaling**:
   - Use distributed vector databases like Pinecone or Weaviate for handling larger datasets.
   - Migrate from SQLite to PostgreSQL or another robust RDBMS for higher reliability and scalability.

2. **LLM Model Improvements**:
   - Experiment with OpenAI's GPT-4 for better contextual understanding.
   - Integrate open-source language models (e.g., LLaMA, Falcon) for cost reduction and on-premise deployment.
   - Prompt engineering to improve the context generation for the LLM model.

3. **Similarity Search**:
   - Explore other embedding models and similarity metrics to improve search accuracy and relevance.
   - Explore different threshold values for similarity scores to optimize the trade-off between precision and recall

4. **Enhanced Query Handling**:
   - Introduce advanced query preprocessing and typo handling to improve search precision.

5. **Monitoring and Metrics**:
   - Add monitoring tools like Prometheus and Grafana for tracking API performance and query patterns.
   - Implement metrics for tracking the system's accuracy, speed, and cost.
   - Add tests for the API and the underlying components to ensure reliability and performance.

---

## License

This repository is for demonstration purposes as part of the Disney hiring process. No part of this codebase should be used for production without prior consent.

---

## Conclusion

This project reflects a thoughtful approach to building a **scalable, AI-powered FAQ answering system**. It balances speed, accuracy, and cost while laying the groundwork for future expansion. With further refinements, this architecture can evolve into a robust solution for handling dynamic and large-scale knowledge bases.
```
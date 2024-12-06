import sqlite3
import faiss
import os
from dotenv import load_dotenv
from functools import lru_cache
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from src.disney_contants import DisneyConstants


class QueryFAQ:
    def __init__(self):
        self.model = self.init_vector_model()
        self.index = self.init_faiss_db()
        self.k = DisneyConstants.NUMBER_OF_ANSWERS
        self.llm_model = self.init_llm_model()

    @staticmethod
    def init_vector_model() -> SentenceTransformer:
        """
        Initialize the SentenceTransformer model
        :return: SentenceTransformer
        """
        model = SentenceTransformer(DisneyConstants.SIMILARITY_MODEL)
        return model

    @staticmethod
    def init_faiss_db() -> faiss.IndexFlatL2:
        """
        Initialize the FAISS index
        :return:
        """
        index = faiss.read_index(DisneyConstants.FAISS_INDEX)
        return index

    @staticmethod
    def init_llm_model():
        """
        Initialize the OpenAI language model
        :return:
        """
        load_dotenv()
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
        )
        return client

    @staticmethod
    def get_sqlite_connection() -> sqlite3.Connection:
        """
        Create a new SQLite connection.
        """
        return sqlite3.connect(DisneyConstants.SQL_DB)

    def preprocess_query(self, query: str) -> str:
        """
        Preprocess the user query to ensure it is valid.
        :param query: str
        :return: str, preprocessed query
        """
        # Check query length
        if len(query) < DisneyConstants.MINIMUM_QUERY_LENGTH or len(query) > DisneyConstants.MAXIMUM_QUERY_LENGTH:
            raise ValueError("Query length must be between 5 and 500 characters.")

        # Normalize query
        query = query.strip().lower()

        return query

    def get_questions_and_distances_from_faiss(self, query: str) -> tuple:
        """
        Get the questions and distances from the FAISS index based on the query
        :param query: str
        :return: tuple, questions and distances
        """
        question_vector = self.model.encode([query])
        distances, faiss_ids = self.index.search(question_vector, self.k)
        return faiss_ids, distances

    def get_sql_id_from_faiss_id(self, faiss_id: int) -> int:
        """
        Get the SQL ID from the FAISS ID
        :param faiss_id: int
        :return: int
        """
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT sql_id FROM {DisneyConstants.FAISS_MAPPING_TABLE} WHERE faiss_id=?", (str(faiss_id),))
        sql_id = cursor.fetchone()[0]
        return sql_id

    @lru_cache(maxsize=1000)
    def get_question_and_answer_from_db(self, question_id: int) -> tuple:
        """
        Get the question and answer from the SQLite database
        Cached to improve performance
        :param question_id: int
        :return: tuple, question and answer
        """
        conn = self.get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer FROM faq WHERE id=?", (question_id,))
        question, answer = cursor.fetchone()
        return question, answer

    def get_questions_and_answer_based_on_query(self, query: str) -> list:
        """
        Get the questions and answers based on the query
        :param query: str
        :return: list
        """
        faiss_ids, distances = self.get_questions_and_distances_from_faiss(query)
        retrieved_answers = []
        for faiss_id, distance in zip(faiss_ids[0], distances[0]):
            if distance > DisneyConstants.SIMILARITY_THRESHOLD:
                break
            sql_id = self.get_sql_id_from_faiss_id(faiss_id)
            question, answer = self.get_question_and_answer_from_db(sql_id)
            retrieved_answers.append({DisneyConstants.QUESTION: question, DisneyConstants.ANSWER: answer})
        return retrieved_answers

    def build_context(self, retrieved_answers, char_limit=DisneyConstants.CONTEXT_LIMIT):
        """
        Dynamically build the context by adding questions and answers until the character limit is reached.
        :param retrieved_answers: List of retrieved answers (list of dicts with 'question' and 'answer').
        :param char_limit: Maximum character limit for the context.
        :return: A string containing the context.
        """
        context = ""
        total_chars = 0

        for item in retrieved_answers:
            q_and_a = f"Q: {item[DisneyConstants.QUESTION]}\nA: {item[DisneyConstants.ANSWER]}\n\n"
            if total_chars + len(q_and_a) > char_limit:
                break
            context += q_and_a
            total_chars += len(q_and_a)

        return context

    def get_answer_from_llm(self, query: str, context: str) -> str:
        """
        Get the answer from the LLM model
        :param query: str
        :param context: str
        :return: str
        """
        response = self.llm_model.chat.completions.create(
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant. Answer questions based only on the provided context. If the "
                            "context is not relevant, respond with 'Sorry, I don't have an answer to that question.'"},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"}
            ],
            model=DisneyConstants.LLM_MODEL
        )
        return response.choices[0].message.content

    def anwser_query(self, query: str) -> str:
        """
        Answer the user query
        :param query: str
        :return: str
        """
        query = self.preprocess_query(query)
        questions = self.get_questions_and_answer_based_on_query(query)
        if len(questions) == 0:
            return "Sorry, I don't have an answer to that question."
        context = self.build_context(questions)
        answer = self.get_answer_from_llm(query, context)
        return answer


if __name__ == "__main__":
    query_faq = QueryFAQ()
    queries = ["What is the smoking policy at Disney Resort hotels?", "Where can I find maps of Disney parks?",
               "How do I make dining reservations at Disney World?",
               "What are the operating hours for Disney World parks?",
               "Can I bring my own food into the park?",
               "What is the history of Disney World?",
               "Are pets allowed in Disney parks?",
               "Does Disney offer any discounts for military personnel?",
               "What time do the fireworks start at Disney World?",
               "What is the policy on wearing costumes to the parks?"]
    for query in queries:
        answer = query_faq.f(query)
        print(answer)




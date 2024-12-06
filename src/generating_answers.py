import sqlite3
import faiss
from sentence_transformers import SentenceTransformer

from src.disney_constants import DisneyConstants

class QueryFAQ:
    def __init__(self):
        self.model = self.init_vector_model()
        self.index = self.init_faiss_db()
        self.conn = self.init_sqlite_db()
        self.k = 5

    @staticmethod
    def init_vector_model() -> SentenceTransformer:
        """
        Initialize the SentenceTransformer model
        :return: SentenceTransformer
        """
        model = SentenceTransformer(DisneyConstants.SIMILARITY_MODEL)
        return model

    @staticmethod
    def init_sqlite_db() -> sqlite3.Connection:
        """
        Initialize the SQLite database
        :return: sqlite3.Connection
        """
        conn = sqlite3.connect(DisneyConstants.SQL_DB)
        return conn

    @staticmethod
    def init_faiss_db() -> faiss.IndexFlatL2:
        """
        Initialize the FAISS index
        :return:
        """
        index = faiss.read_index(DisneyConstants.FAISS_INDEX)
        return index

    def get_questions_and_distances_from_faiss(self, query: str) -> tuple:
        """
        Get the questions and distances from the FAISS index based on the query
        :param query: str
        :return: tuple, questions and distances
        """
        question_vector = self.model.encode([query])
        distances, faiss_ids  = self.index.search(question_vector, self.k)
        return faiss_ids, distances

    def get_question_and_answer_from_db(self, question_id: int) -> tuple:
        """
        Get the question and answer from the SQLite database
        :param question_id: int
        :return: tuple, question and answer
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT question, answer FROM faq WHERE id=?", (question_id,))
        question = cursor.fetchone()[0]
        answer = cursor.fetchone()[1]
        return question, answer

    def get_questions_and_answer_based_on_query(self, query: str) -> list:
        """
        Get the questions and answers based on the query
        :param query: str
        :return: list
        """
        faiss_ids, distances = self.get_questions_and_distances_from_faiss(query)
        questions = []
        for faiss_id, distance in zip(faiss_ids[0], distances[0]):
            question, answer = self.get_question_and_answer_from_db(faiss_id)


if __name__ == "__main__":
    query_faq = QueryFAQ()
    query = "What is the best time to visit Disney World?"
    questions = query_faq.get_questions_and_answer_based_on_query(query)
    for question in questions:
        print(question)
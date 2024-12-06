from dataclasses import dataclass


@dataclass
class DisneyConstants:
    ANSWER: str = 'answer'
    CATEGORY: str = 'category'
    CHUNCK_SIZE: int = 500
    DISABILITIES: str = 'disabilities'
    FAISS_INDEX: str = 'faq_index.faiss'
    FAISS_MAPPING_TABLE: str = 'faiss_mapping'
    FAQ_URL: str = 'https://disneyworld.disney.go.com/faq/'
    FAQ_SECTION_CLASS: str = 'help-content'
    ID: str = 'id'
    MAXIMUM_ANSWER_LENGTH: int = 3000
    MAXIMUM_QUESTION_LENGTH: int = 3000
    MINIMUM_QUERY_LENGTH: int = 5
    MINIMUM_QUESTION_LENGTH: int = 10
    MINIMUM_ANSWER_LENGTH: int = 10
    NUMBER_OF_WORKERS: int = 4
    QUESTION: str = 'question'
    QUESTION_LIST_CLASS: str = 'help-question-list__list'
    QUESTION_CLASS: str = 'help-question-item__link'
    QUESTION_TEXT_CLASS: str = 'help-question__text--question'
    ANSWER_TEXT_CLASS: str = 'help-question__text--answer'
    SIMILARITY_MODEL: str = 'all-MiniLM-L6-v2'
    SIMILARITY_THRESHOLD: float = 1.2
    SQL_DB: str = '../data/disney_faq.db'
    SQL_TABLE: str = 'faq'
    TECHNOLOGY_AND_PRIVACY: str = 'Technology and Privacy'
    TEXT_CONTENT_ATTRIBUTE: str = 'textContent'



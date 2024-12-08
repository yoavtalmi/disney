from dataclasses import dataclass


@dataclass
class DisneyConstants:
    ANSWER: str = 'answer'
    CATEGORY: str = 'category'
    CONTEXT_LIMIT: int = 10000
    CHUNCK_SIZE: int = 500
    FAISS_INDEX: str = 'data/faq_index.faiss'
    FAISS_MAPPING_TABLE: str = 'faiss_mapping'
    FAQ: str = 'faq'
    FAQ_URL: str = 'https://disneyworld.disney.go.com/faq/'
    FAQ_SECTION_CLASS: str = 'help-content'
    ID: str = 'id'
    LLM_MODEL: str = 'gpt-3.5-turbo'
    MAXIMUM_ANSWER_LENGTH: int = 3000
    MAXIMUM_QUESTION_LENGTH: int = 3000
    MAXIMUM_QUERY_LENGTH: int = 500
    MINIMUM_QUESTION_LENGTH: int = 10
    MINIMUM_ANSWER_LENGTH: int = 10
    MINIMUM_QUERY_LENGTH: int = 5
    NUMBER_OF_ANSWERS: int = 3
    NUMBER_OF_WORKERS: int = 4
    QUESTION: str = 'question'
    QUESTION_LIST_CLASS: str = 'help-question-list__list'
    QUESTION_CLASS: str = 'help-question-item__link'
    QUESTION_TEXT_CLASS: str = 'help-question__text--question'
    ANSWER_TEXT_CLASS: str = 'help-question__text--answer'
    SIMILARITY_MODEL: str = 'all-MiniLM-L6-v2'
    SIMILARITY_MODEL_DIM: int = 384
    SIMILARITY_THRESHOLD: float = 1.2
    SQL_DB: str = 'data/disney_faq.db'
    SQL_TABLE: str = 'faq'
    TECHNOLOGY_AND_PRIVACY: str = 'Technology and Privacy'
    TEXT_CONTENT_ATTRIBUTE: str = 'textContent'



import logging
import sqlite3
import pandas as pd
import random
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from multiprocessing import Pool
import time

from disney_contants import DisneyConstants

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize FAISS with IndexIDMap to support custom IDs
dim = DisneyConstants.SIMILARITY_MODEL_DIM  # Dimensionality of the embeddings
base_index = faiss.IndexFlatL2(dim)  # Base index
index = faiss.IndexIDMap(base_index)  # Add ID mapping functionality

# Load the model
model = SentenceTransformer(DisneyConstants.SIMILARITY_MODEL)


def timer(func):
    """Decorator to log the execution time of functions."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Function '{func.__name__}' executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper


@timer
def clean_data(chunk: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the data by removing duplicates, null values, and short/long questions and answers.
    :param chunk: pd.DataFrame with columns 'question' and 'answer'
    :return: cleaned pd.DataFrame
    """
    chunk.drop_duplicates(subset=[DisneyConstants.QUESTION, DisneyConstants.ANSWER], inplace=True, keep='last')
    chunk.dropna(inplace=True)
    chunk = chunk[(chunk[DisneyConstants.QUESTION].str.len() > DisneyConstants.MINIMUM_QUESTION_LENGTH) &
                  (chunk[DisneyConstants.QUESTION].str.len() < DisneyConstants.MAXIMUM_QUESTION_LENGTH) &
                  (chunk[DisneyConstants.ANSWER].str.len() > DisneyConstants.MINIMUM_ANSWER_LENGTH) &
                  (chunk[DisneyConstants.ANSWER].str.len() < DisneyConstants.MAXIMUM_ANSWER_LENGTH)]
    chunk.reset_index(drop=True, inplace=True)
    return chunk


@timer
def vectorize_data(data: pd.DataFrame) -> np.array:
    """
    Vectorize the questions using the SentenceTransformer model.
    :param data: pd.DataFrame with a 'question' column
    :return: embeddings as a np.array
    """
    questions = data[DisneyConstants.QUESTION].tolist()
    vectors = model.encode(questions, batch_size=32)
    return vectors


def process_chunk(chunk: pd.DataFrame) -> tuple:
    """
    Process each chunk: clean, vectorize, and return FAISS IDs, SQL IDs, and vectors.
    :param chunk: pd.DataFrame with columns 'id', 'question', and 'answer'
    :return: tuple of faiss_ids faiss table ids, sql_ids SQL table ids, and embeddings vectors
    """
    start_time = time.time()

    # Clean the chunk
    cleaned_chunk = clean_data(chunk)

    # Vectorize the cleaned questions
    vectors = vectorize_data(cleaned_chunk)

    # Generate unique FAISS IDs
    faiss_ids = [int(random.randint(-(2**63), 2**63 - 1)) for _ in range(len(cleaned_chunk))]

    # Convert SQL IDs to native Python int
    sql_ids = [int(id) for id in cleaned_chunk[DisneyConstants.ID].to_numpy()]

    end_time = time.time()
    logging.info(f"process_chunk took {end_time - start_time:.2f} seconds")
    return faiss_ids, sql_ids, vectors


def parallel_process_chunks(chunks: pd.DataFrame, num_workers: int = 4):
    """
    Parallelize the processing of chunks using multiprocessing.
    :param chunks: pd.DataFrame chunks with columns 'id', 'question', and 'answer'
    :param num_workers: int, number of workers to use
    :return: tuple of all_faiss_ids, all_sql_ids, and all_vectors
    """
    start_time = time.time()

    with Pool(num_workers) as pool:
        results = pool.map(process_chunk, chunks)

    # Combine results
    all_faiss_ids = np.concatenate([result[0] for result in results])
    all_sql_ids = np.concatenate([result[1] for result in results])
    all_vectors = np.vstack([result[2] for result in results])

    end_time = time.time()
    logging.info(f"parallel_process_chunks took {end_time - start_time:.2f} seconds")
    return all_faiss_ids, all_sql_ids, all_vectors


@timer
def save_mapping_table(faiss_ids: list, sql_ids: list, db_path: str,
                       mapping_table_name: str = DisneyConstants.FAISS_MAPPING_TABLE):
    """
    Save the mapping table to a SQLite database.
    :param faiss_ids: list of FAISS IDs
    :param sql_ids: list of SQL IDs
    :param db_path: path to the SQLite database
    :param mapping_table_name: name of the mapping table
    :return:
    """
    faiss_ids = [int(id) for id in faiss_ids]
    sql_ids = [int(id) for id in sql_ids]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the mapping table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {mapping_table_name} (
        faiss_id INTEGER PRIMARY KEY,
        sql_id INTEGER
    )
    """)

    mappings = list(zip(faiss_ids, sql_ids))
    cursor.executemany(f"INSERT INTO {mapping_table_name} (faiss_id, sql_id) VALUES (?, ?)", mappings)

    conn.commit()
    conn.close()
    logging.info(f"Mapping table '{mapping_table_name}' saved to {db_path}")


@timer
def process_and_store_faiss(db_path: str, table_name: str, faiss_index_path: str, chunksize: int = 1000,
                            num_workers: int = 4):
    """
    Process the data, create a FAISS index, and save it to disk.
    :param db_path: str, path to the SQLite database
    :param table_name: str, name of the table in the database
    :param faiss_index_path: str, path to save the FAISS index
    :param chunksize: int, number of rows to read at a time
    :param num_workers: int, number of workers to use
    :return:
    """
    conn = sqlite3.connect(db_path)
    query = f"SELECT id, question, answer FROM {table_name}"

    chunks = pd.read_sql_query(query, conn, chunksize=chunksize)

    all_faiss_ids, all_sql_ids, all_vectors = parallel_process_chunks(chunks, num_workers=num_workers)

    index.add_with_ids(all_vectors, all_faiss_ids)

    faiss.write_index(index, faiss_index_path)
    logging.info(f"FAISS index saved to {faiss_index_path}")

    save_mapping_table(all_faiss_ids, all_sql_ids, db_path)

    conn.close()


if __name__ == "__main__":
    process_and_store_faiss(
        db_path=DisneyConstants.SQL_DB,
        table_name=DisneyConstants.SQL_TABLE,
        faiss_index_path=DisneyConstants.FAISS_INDEX,
        chunksize=DisneyConstants.CHUNCK_SIZE,
        num_workers=DisneyConstants.NUMBER_OF_WORKERS
    )


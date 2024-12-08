from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import sqlite3
import time
import logging

from disney_contants import DisneyConstants

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def timer(func):
    """
    Decorator to measure execution time of a function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Function '{func.__name__}' executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper


@timer
def get_faq_page() -> webdriver:
    """
    Scrape the Disney World FAQ page
    :return: Driver instance
    """
    options = Options()
    options.add_argument("--headless=new")  # Use the new headless mode
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-http2")  # Optional: Force HTTP/1.1 if HTTP/2 is problematic
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )  # Simulate a real browser
    # Point to the installed chromedriver path (default in Debian/Ubuntu systems)
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    url = DisneyConstants.FAQ_URL
    driver.get(url)
    time.sleep(1)
    return driver


@timer
def get_faq_categories_dict(driver: webdriver) -> dict:
    """
    Get the FAQ categories as a dictionary
    :param driver: The WebDriver instance
    :return: A dictionary of FAQ categories
    """
    try:
        logging.info("Waiting for the FAQ section to load...")
        faq_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, DisneyConstants.FAQ_SECTION_CLASS))
        )
        logging.info("FAQ section located.")
        category_links = faq_section.find_elements(By.TAG_NAME, "a")
        faq_categories = {}
        for link in category_links:
            category_href = link.get_attribute("href")
            try:
                category_div = link.find_element(By.TAG_NAME, "div")
                category_title = category_div.get_attribute(DisneyConstants.TEXT_CONTENT_ATTRIBUTE).strip()
            except Exception as e:
                logging.error(f"Error extracting category title: {e}")
                category_title = None
            if category_title and category_href and 'faq' in category_href:
                faq_categories[category_title] = category_href
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.info("Page source for debugging:")
        logging.info(driver.page_source)
        faq_categories = {}

    driver.quit()
    return faq_categories


@timer
def extract_question_links(category_url: str, driver: webdriver) -> list:
    """
    Extract the links to the questions in a given category
    :param category_url: str, URL of the category
    :param driver: webdriver instance
    :return: question links
    """
    logging.info(f"Extracting question links from category: {category_url}")
    driver.get(category_url)
    question_list = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, DisneyConstants.QUESTION_LIST_CLASS))
    )
    question_links = question_list.find_elements(By.CLASS_NAME, DisneyConstants.QUESTION_CLASS)
    links = [link.get_attribute("href") for link in question_links if link.get_attribute("href")]
    return links


@timer
def extract_question_and_answer(question_url: str, driver: webdriver) -> tuple:
    """
    Extract the question and answer from a given question URL
    :param question_url: str, URL of the question
    :param driver: webdriver instance
    :return: question and answer
    """
    logging.info(f"Extracting question and answer from: {question_url}")
    try:
        driver.get(question_url)
        question = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, DisneyConstants.QUESTION_TEXT_CLASS))
        ).text
        answer_parts = driver.find_elements(By.CLASS_NAME, DisneyConstants.ANSWER_TEXT_CLASS)
        answer = "\n".join([part.text for part in answer_parts])
    except Exception as e:
        logging.error(f"An error occurred with question {question_url}: {e}")
        question, answer = None, None
    except TimeoutException as e:
        logging.error(f"Timeout occurred while loading {question_url}: {e}")
        question, answer = None, None
    return question, answer


@timer
def get_questions_dicts(faq_categories: dict) -> list:
    """
    Get the questions and answers for all categories
    :param faq_categories: dict, dictionary of FAQ categories
    :return: list of dictionaries containing questions and answers
    """
    questions_dicts = []
    options = Options()
    options.add_argument("--headless=new")  # Use the new headless mode
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-http2")  # Optional: Force HTTP/1.1 if HTTP/2 is problematic
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    # Point to the installed chromedriver path (default in Debian/Ubuntu systems)
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    for category, link in faq_categories.items():
        if category == DisneyConstants.TECHNOLOGY_AND_PRIVACY:
            continue
        questions = extract_question_links(link, driver)
        for question in questions:
            q, a = extract_question_and_answer(question, driver)
            questions_dicts.append({DisneyConstants.CATEGORY: category, DisneyConstants.QUESTION: q,
                                    DisneyConstants.ANSWER: a})
    driver.quit()
    return questions_dicts


@timer
def create_db(questions_dicts: list):
    """
    Create a SQLite database and insert the questions and answers
    :param questions_dicts: list, list of dictionaries containing questions and answers
    :return:
    """
    conn = sqlite3.connect(DisneyConstants.SQL_DB)
    cursor = conn.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {DisneyConstants.SQL_TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        question TEXT,
        answer TEXT
    )
    """)
    for record in questions_dicts:
        if record[DisneyConstants.QUESTION] is None or record[DisneyConstants.ANSWER] is None:
            continue
        cursor.execute("""
        INSERT INTO faq (category, question, answer)
        VALUES (?, ?, ?)
        """, (record[DisneyConstants.CATEGORY], record[DisneyConstants.QUESTION], record[DisneyConstants.ANSWER]))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # Get the FAQ page
    driver = get_faq_page()

    # Get the FAQ categories as a dictionary
    faq_categories = get_faq_categories_dict(driver)

    # Get the questions and answers
    questions_dicts = get_questions_dicts(faq_categories)
    create_db(questions_dicts)

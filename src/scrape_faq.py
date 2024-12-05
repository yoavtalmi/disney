from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_faq_page() -> webdriver:
    """
    Scrape the Disney World FAQ page
    :return: Driver instance
    """

    driver = webdriver.Chrome()  # Replace with the appropriate WebDriver for your browser

    # Open the Disney FAQ page
    url = 'https://disneyworld.disney.go.com/faq/'
    driver.get(url)

    # Allow the page to fully load
    time.sleep(1)
    return driver


def get_faq_categories_dict(driver: webdriver) -> dict:
    """
    Get the FAQ categories as a dictionary
    :param driver: The WebDriver instance
    :return: A dictionary of FAQ categories
    """

    try:
        faq_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "help-content"))
        )

        # Find all links within the FAQ section
        category_links = faq_section.find_elements(By.TAG_NAME, "a")

        faq_categories = {}

        for link in category_links:
            category_href = link.get_attribute("href")
            # Extract the title from the <div> inside the <a>
            try:
                category_div = link.find_element(By.TAG_NAME, "div")
                category_title = category_div.get_attribute("textContent").strip()
            except:
                category_title = None  # Handle cases where <div> might be missing

            # Add to the dictionary if valid
            if category_title and category_href:
                faq_categories[category_title] = category_href

    except Exception as e:
        print(f"An error occurred: {e}")

    # Close the browser
    driver.quit()
    return faq_categories


if __name__ == '__main__':
    # Get the FAQ page
    driver = get_faq_page()

    # Get the FAQ categories as a dictionary
    faq_categories = get_faq_categories_dict(driver)

    # Print the FAQ categories
    for category, link in faq_categories.items():
        print(f"{category}: {link}")
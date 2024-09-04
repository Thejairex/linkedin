from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import time
import pickle
import logging
import os

from db import Jobs


class linkedin:
    """
    Class to interact with linkedin using selenium webdriver.
    """

    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=options)
        self.loggedin = False

    def login(self, user_email: str, user_password: str):
        """
        Login to linkedin

        args:

        user_email : str
            Email of the user
        user_password : str
            Password of the user
        """

        # check if cookies exist and load cookies
        if not self.__load_cookies():
            # try to login
            self.driver.get('https://www.linkedin.com/login')
            username = self.driver.find_element(By.ID, 'username')
            password = self.driver.find_element(By.ID, 'password')
            username.send_keys(user_email)
            password.send_keys(user_password)
            self.driver.find_element(
                By.XPATH, '//button[@type="submit"]').click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'global-nav-search'))
            )
            self.__save_cookies()
            self.loggedin = True

        else:

            self.driver.get("https://www.linkedin.com/feed/")
            self.loggedin = True

        # close pop-up
        self.driver.find_element(
            By.XPATH, "//header[contains(@class, 'msg-overlay-bubble-header')]").click()

    def __save_cookies(self):
        """
        Save cookies in a pickle file.
        """
        cookies = self.driver.get_cookies()

        # create folder Data if not exist
        if not os.path.exists('Data'):
            os.makedirs('Data')

        # Save cookies in a pickle file
        with open('Data/cookies.pkl', 'wb') as file:
            pickle.dump(cookies, file)
            file.close()

    def __load_cookies(self):
        """
        Load cookies from a json file. 
        If not exist, return False
        """
        try:
            # load cookies
            self.driver.get('https://www.linkedin.com')
            with open('Data/cookies.pkl', 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                file.close()

            return True

        except FileNotFoundError:
            return False

        except Exception as e:
            raise e

    def screen_shot(self):
        """
        Save a screenshot of the current page
        """
        self.driver.save_screenshot('Images/screenshot.png')

    def search(self, keyword: str):
        """
        Search for a keyword on search bar of linkedin.

        args:
            keyword (str): keyword to search
        """
        search_box = self.driver.find_element(
            By.CLASS_NAME, 'search-global-typeahead__input')
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.ID, 'search-reusables__filters-bar'))
        )

    def close(self):
        """
        Close the current window.
        """
        self.driver.close()

    def shutdown(self):
        """
        Shutdown the driver and close the browser.
        """
        self.driver.quit()


class Searcher(linkedin):
    """
    Searcher class to search in the search bar on linkedin.
    """

    def __init__(self) -> None:
        """
        Has a super class linkedin.
        Initialize jobs database.
        Get current date.
        """
        super().__init__()
        self.jobs = Jobs('Data/jobs.db')
        self.current_date = datetime.now()

    def search_jobs(self, keyword: str, page_number: int = 1,):
        """
        Find jobs on linkedin and save them in the database using keyword.

        args:
            keyword (str): keyword to search
            page_number (int): number of pages to search
        """

        super().search(keyword)
        super().screen_shot()

        # wait for the page to load
        self.driver.find_element(
            By.CLASS_NAME, 'search-reusables__primary-filter').click()
        time.sleep(3)

        # iterate through pages
        currect_page = 0
        while currect_page < page_number:
            # get job listings from the page
            currect_page += 1
            job_listings = self.driver.find_elements(
                By.CSS_SELECTOR, ".ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item")

            # iterate through job listings
            for i, job in enumerate(job_listings):
                # scroll to the job
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", job)

                # try to collect data
                try:
                    # find job title, company name, location, and easy apply button
                    job.click()

                    link = self.driver.current_url
                    link_params = parse_qs(urlparse(link).query)
                    job_id = int(link_params.get('currentJobId', [None])[0])

                    if job_id in self.jobs.select_ids():
                        continue

                    job_title = job.find_element(By.TAG_NAME, 'strong').text
                    company_name = job.find_element(
                        By.CLASS_NAME, 'job-card-container__primary-description ').text
                    location = job.find_element(
                        By.CLASS_NAME, 'job-card-container__metadata-item ').text
                    button = job.find_element(
                        By.XPATH, "//div[contains(@class, 'jobs-apply-button--top-card')]")
                    solicitude = button.find_element(
                        By.XPATH, ".//button//span[contains(@class, 'artdeco-button__text')]").text
                    publish_jobs = self.driver.find_element(
                        By.XPATH, '//div[@class="job-details-jobs-unified-top-card__primary-description-container"]//div[@class="t-black--light mt2"]/span[3]').text

                    if 'de nuevo' in publish_jobs:
                        units = int(publish_jobs.split()[-2])
                    else:
                        units = int(publish_jobs.split()[1])

                    # control units of publish_jobs
                    if 'día' in publish_jobs:
                        publish_jobs = self.current_date - \
                            timedelta(days=units)

                    elif 'semana' in publish_jobs:
                        publish_jobs = self.current_date - \
                            timedelta(weeks=units)

                    elif 'mes' in publish_jobs:
                        publish_jobs = self.current_date - \
                            relativedelta(months=units)

                    elif 'hora' in publish_jobs and 'minuto' in publish_jobs:
                        publish_jobs = self.current_date

                    else:
                        continue

                    publish_jobs = publish_jobs.strftime('%Y-%m-%d')

                    # store job in the database
                    self.jobs.insert(job_id, job_title, company_name,
                                     location, solicitude, keyword, link, publish_jobs)

                except KeyboardInterrupt:
                    self.shutdown()
                    exit()

                # error get units od publish_jobs is str not int
                except ValueError:
                    print("Error: units od publish_jobs is str not int.")
                    print("Value Error: ", publish_jobs)
                    continue

                except Exception as e:
                    # Crear carpeta de log si no existe y guardaqr los errores en un error.log
                    if not os.path.exists('Logs'):
                        os.mkdir('Logs')
                    logging.basicConfig(
                        filename='Logs/error.log', level=logging.ERROR)
                    logging.error(e)

            # next page
            list_pages = self.driver.find_element(
                By.XPATH, "//ul[contains(@class, 'artdeco-pagination__pages artdeco-pagination__pages--number')]")
            list_pages.find_elements(By.TAG_NAME, 'li')[currect_page].click()

            # wait for the page to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.ID, 'search-reusables__filters-bar'))
            )

        self.driver.get("https://www.linkedin.com/feed/")

    def get_jobs(self):
        rows = self.jobs.select()
        return [dict(zip(self.jobs.columns, row)) for row in rows]

    def export_to_csv(self):
        return self.jobs.export_to_csv()

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
    def __init__(self) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        # options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=options)
        self.loggedin = False

    def login(self, user_email: str, user_password: str):
        """
        Login to linkedin

        Parameters
        ----------
        user_email : str
            Email of the user
        user_password : str
            Password of the user
        """
        if not self.__load_cookies():
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

        self.driver.find_element(
            By.XPATH, "//header[contains(@class, 'msg-overlay-bubble-header')]").click()

    def __save_cookies(self):
        """
        Save cookies in a json file
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
        """
        try:
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
        search_box = self.driver.find_element(
            By.CLASS_NAME, 'search-global-typeahead__input')
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.ID, 'search-reusables__filters-bar'))
        )

    def close(self):
        self.driver.close()

    def shutdown(self):
        self.driver.quit()


class searcher(linkedin):
    def __init__(self) -> None:
        super().__init__()
        self.jobs = Jobs('Data/jobs.db')
        self.current_date = datetime.now()

    def search_jobs(self, keyword: str, page_number: int = 1,):
        super().search(keyword)
        super().screen_shot()

        self.driver.find_element(
            By.CLASS_NAME, 'search-reusables__primary-filter').click()
        time.sleep(3)

        currect_page = 0
        while currect_page < page_number:
            # get job listings from the page
            currect_page += 1
            job_listings = self.driver.find_elements(
                By.CSS_SELECTOR, ".ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item")

            # iterate through job listings
            for i, job in enumerate(job_listings):
                # desplazarse hasta el elemento actual
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", job)

                # manejar el error de no encontrar el elemento
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

                    print(f'Index: {i+1}, Title: {job_title}')
                    print(publish_jobs)

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

        time.sleep(3)

        self.shutdown()


def main():
    load_dotenv()
    link = searcher()
    link.login(os.getenv('EMAIL'), os.getenv('PASSWORD'))
    link.search_jobs("Data Engineer")


if __name__ == '__main__':
    main()

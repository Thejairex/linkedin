from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dotenv import load_dotenv
import time
import pickle
import logging
import os

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
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'global-nav-search'))
            )
            self.__save_cookies()
            self.loggedin = True

        else:
            self.driver.get("https://www.linkedin.com/feed/")
            self.loggedin = True
        
    def __save_cookies(self):
        """
        Save cookies in a json file
        """
        cookies = self.driver.get_cookies()
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
        search_box = self.driver.find_element(By.CLASS_NAME, 'search-global-typeahead__input')
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'search-reusables__filters-bar'))
        )
        
    def close(self):
        self.driver.close()

class searcher(linkedin):
    def __init__(self) -> None:
        super().__init__()
    
    def search_jobs(self, keyword: str):
        super().search(keyword)
        super().screen_shot()
        
        self.driver.find_element(By.CLASS_NAME, 'search-reusables__primary-filter').click()
        
        time.sleep(3)
        
        # get job listings from the page
        job_listings = self.driver.find_elements(By.CSS_SELECTOR, ".ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item")

        for i, job in enumerate(job_listings):
            # desplazarse hasta el elemento actual
            self.driver.execute_script("arguments[0].scrollIntoView();", job)
            
            # manejar el error de no encontrar el elemento
            try:
                job_title = job.find_element(By.TAG_NAME, 'strong').text
                company_name = job.find_element(By.CLASS_NAME, 'job-card-container__primary-description ').text
                location = job.find_element(By.CLASS_NAME, 'job-card-container__metadata-item ').text
                easy_solicitude = job.find_element(By.CSS_SELECTOR, '.jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view').text
                print(f'Title: {job_title}, Company: {company_name}, Location: {location}, Easy solicitude: {easy_solicitude}')
                
            except KeyboardInterrupt:
                exit()
            
            except Exception as e:
                # Crear carpeta de log si no existe y guardaqr los errores en un error.log
                if not os.path.exists('Logs'):
                    os.mkdir('Logs')
                logging.basicConfig(filename='Logs/error.log', level=logging.ERROR)
                logging.error(e)
        
        time.sleep(3)


def main():
    load_dotenv()
    link = searcher()
    link.login(os.getenv('EMAIL'), os.getenv('PASSWORD') )
    link.search_jobs("Data Scientist")
    
if __name__ == '__main__':
    main()
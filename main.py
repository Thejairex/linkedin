from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle

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
        
        job_listings = self.driver.find_element(By.XPATH, '//ul[contains(@class, "scaffold-layout__list-container")]/li')
        
        # for job in job_listings:
        #     job_title = job.find_element(By.XPATH, './/h3').text
        #     company_name = job.find_element(By.XPATH, './/h4').text
        #     location = job.find_element(By.XPATH, './/span[contains(@class, "job-result-card__location")]').text
        #     print(f'Title: {job_title}, Company: {company_name}, Location: {location}')
        time.sleep(3)


def main():
    link = searcher()
    link.login('juarezjesusyair@gmail.com', 'Aiwa2015')
    link.search_jobs("Data Scientist")
    
if __name__ == '__main__':
    main()
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import Searcher

def main(keyword, page):
    # Load environment variables in .env file
    load_dotenv()
    # Create an instance of the Searcher class
    link = Searcher()
    # Call the login method with the user email and password
    link.login(os.getenv('EMAIL'), os.getenv('PASSWORD'))

    # Call the search_jobs method with the keyword and page number
    link.search_jobs(keyword, page)

    # get the list of jobs
    jobs = link.get_jobs()
    print(jobs)

    # export to csv
    link.export_to_csv()
    
if __name__ == "__main__":
    # Call the main function with testint data
    keyword = str(input("Keyword to seach: "))
    page = int(input("Number of pages to search: "))
    main(keyword, page)
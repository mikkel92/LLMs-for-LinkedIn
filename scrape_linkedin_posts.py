from time import sleep
from mikkel_secrets import secrets
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# how to install webdriver:
# https://github.com/password123456/setup-selenium-with-chrome-driver-on-ubuntu_debian

class ScrapeLinkedIn:

    def __init__(self):

        # Change these with your urls and credentials
        self.login_url = "https://www.linkedin.com/login/da"
        self.posts_url = "https://www.linkedin.com/in/%F0%9F%9A%80-mikkel-jensen-b2a960159/recent-activity/all/"
        self.user_mail = secrets["linkedin"]["username"]
        self.user_pass = secrets["linkedin"]["password"]

        # Options for the Chrome driver
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_experimental_option("detach", True)
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def _click(self, path):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.element_to_be_clickable((By.XPATH, path))).click()

    def login_linkedin(self):

        self.driver.get(self.login_url)

        # get username and password input boxes path
        username = self.driver.find_element(By.XPATH, "//input[@name='session_key']")
        password = self.driver.find_element(By.XPATH, "//input[@name='session_password']")

        # input the email id and password
        username.send_keys(self.user_mail)
        password.send_keys(self.user_pass)

        # click the login button
        self._click("//button[@type='submit']")

    def load_posts(self):

        # load the page containing posts
        self.driver.get(self.posts_url)
        sleep(2)

        # scroll on site until all posts are loaded
        prev_scroll_height = 0
        scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        while scroll_height > prev_scroll_height:
            prev_scroll_height = int(scroll_height)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        
        # find all posts
        posts = self.driver.find_elements(By.CLASS_NAME, "profile-creator-shared-feed-update__container")
        print("Total number of LinkedIn posts: ", len(posts))

        # put the text from posts in a list containing one entry per post
        all_texts = []
        post_texts = self.driver.find_elements(By.CLASS_NAME, "feed-shared-inline-show-more-text")
        for text in post_texts:
            all_texts.append(text.text)

        self.driver.close()

        return all_texts

    def save_posts_to_csv(self, posts):

        # save posts to a csv file
        df = pd.DataFrame({"texts" : posts})
        df.to_csv("linkedin_posts.csv", index_label="index")


if __name__ == "__main__":

    scraper = ScrapeLinkedIn()
    scraper.login_linkedin()
    posts = scraper.load_posts()
    scraper.save_posts_to_csv(posts)

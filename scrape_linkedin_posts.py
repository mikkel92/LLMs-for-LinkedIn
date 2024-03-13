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
        # add chromes cache folder to save your logins
        options.add_argument("user-data-dir=/home/mikkel/.cache/google-chrome/Profile 1")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def _click(self, path):
        wait = WebDriverWait(self.driver, 20)
        wait.until(EC.element_to_be_clickable((By.XPATH, path))).click()

    def login_linkedin(self):
        
        
        self.driver.get(self.login_url)
        sleep(1)
        if self.driver.current_url == "https://www.linkedin.com/feed/":
            print("Already logged in")

        else:
            # get username and password input boxes path
            username = self.driver.find_element(By.XPATH, "//input[@name='session_key']")
            password = self.driver.find_element(By.XPATH, "//input[@name='session_password']")

            # input the email id and password
            username.send_keys(self.user_mail)
            password.send_keys(self.user_pass)

            # click the login button
            self._click("//button[@type='submit']")

    def get_post_elements(self, post, class_name):
        
        all_texts = []
        post_texts = post.find_elements(By.CLASS_NAME, class_name)
        for text in post_texts:
            all_texts.append(text.get_attribute("innerText"))
            
        return all_texts

    def load_posts(self):

        # load the page containing posts
        self.driver.get(self.posts_url)
        sleep(2)

        # scroll on site until all posts are loaded
        prev_scroll_height = 0
        y = 0
        scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        while scroll_height > prev_scroll_height:
            prev_scroll_height = int(scroll_height)
            
            i = 0
            while i < 5:
                y += 1000
                self.driver.execute_script(f"window.scrollTo(0, {y});")
                sleep(1)
                i += 1
        
            scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")


        # find all posts
        posts = self.driver.find_elements(By.CLASS_NAME, "profile-creator-shared-feed-update__container")
        print("Total number of LinkedIn posts: ", len(posts))

        texts = []
        reactions = []
        comments = []
        reposts = []
        impressions = []

        for i, post in enumerate(posts):

            # append post texts
            texts.append(self.get_post_elements(post, "break-words")[0])

            # append post reactions if any exist
            reaction = self.get_post_elements(post, "social-details-social-counts__social-proof-fallback-number") + self.get_post_elements(post, "social-details-social-counts__reactions-count")
            if len(reaction) > 0:
                reactions.append(int(reaction[0]))
            else:
                reactions.append(0)

            # append post comments if any exist
            comment = self.get_post_elements(post, "social-details-social-counts__item--right-aligned")
            if len(comment) > 0:
                comments.append(int(comment[0].split(" ")[0]))
            else:
                comments.append(0)

            # append post reposts if any exist
            if len(comment) > 1:
                reposts.append(int(comment[1].split(" ")[0]))
            else:
                reposts.append(0)

            # append post impressions if any exist
            impression = self.get_post_elements(post, "ca-entry-point__num-views")
            if len(impression) > 0:
                impressions.append(int(impression[0].split(" ")[0].replace(",", "")))
            else:
                impressions.append(0)

        #self.driver.close()

        df = pd.DataFrame({
            "texts" : texts,
            "reactions": reactions,
            "comments": comments,
            "reposts": reposts,
            "impressions": impressions
            })

        return df

    def save_posts_to_csv(self, df):

        # save posts to a csv file
        df.to_csv("linkedin_posts.csv", index_label="index")


if __name__ == "__main__":

    scraper = ScrapeLinkedIn()
    scraper.login_linkedin()
    posts_df = scraper.load_posts()
    scraper.save_posts_to_csv(posts_df)

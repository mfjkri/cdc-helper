import time

import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from abstracts.cdc_abstract import CDCAbstract, Types



class handler(CDCAbstract):
    def __init__(self, login_data, captcha_solver, log, browser_type="firefox", headless=False):
        self.home_url = "https://www.cdc.com.sg"
        self.booking_url = "https://www.cdc.com.sg:8080"
        
        self.captcha_solver = captcha_solver
        self.log = log
        
        self.username = login_data["username"]
        self.password = login_data["password"]
        
        if browser_type.lower() == "firefox":
            options = webdriver.FirefoxOptions()
            
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument('--no-proxy-server')

            self.driver = webdriver.Firefox(executable_path="drivers/geckodriver", options=options)
        elif browser_type.lower() == "chrome":
            options = webdriver.ChromeOptions()

            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument('--no-proxy-server')

            self.driver = webdriver.Chrome(executable_path="drivers/chromedriver.exe", options=options)
        
        self.driver.set_window_size(1600, 768)
        super().__init__(username=self.username, password=self.password, headless=headless)
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.driver.close()
        
    def _open_index(self, path: str):
        self.driver.get(
            f"{self.booking_url}/{path}.html")
        
    def open_home_page(self):
        self.driver.get(self.home_url)
        assert "ComfortDelGro" in self.driver.title
        
    def account_login(self):
        self.open_home_page()
        time.sleep(2)
        
        prompt_login_btn = self.driver.find_element_by_xpath("//*[@id=\"top-menu\"]/ul/li[10]/a")
        prompt_login_btn.click()
        
        learner_id_input = self.driver.find_element_by_name("userId")
        password_input = self.driver.find_element_by_name("password")

        learner_id_input.send_keys(self.username)
        password_input.send_keys(self.password)

        # wait for user to solve recaptcha
        self.captcha_solver.solve(driver=self.driver)
        
        login_btn = self.driver.find_element_by_id("BTNSERVICE2")
        login_btn.click()
        
        alert = self.driver.switch_to.alert
        if alert:
            alert.accept()
            
        self.log.info("Logged in successfully!")
        
    def account_logout(self):
        self._open_index("NewPortal/logOut.aspx?PageName=Logout")
        
    
        
        
import time, datetime
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from abstracts.cdc_abstract import CDCAbstract, Types

from src.utils.common import selenium_common
from src.utils.common import utils

def convert_to_datetime(date_str:str, time_str:str=None):
    if time_str:
        time_str = time_str.split(' ')[0]
        return datetime.datetime.strptime(f'{date_str} | {time_str}', '%d/%b/%Y | %H:%M')
    else:
        return datetime.datetime.strptime(date_str, "%d/%b/%Y")

class handler(CDCAbstract):
    def __init__(self, login_credentials, captcha_solver, log, browser_config):
        browser_type = browser_config["type"] or "firefox"
        headless = browser_config["headless_mode"] or False
        
        if browser_type.lower() != "firefox" and browser_type.lower() != "chrome":
            log.error("Invalid browser_type was given!")
            raise Exception("Invalid BROWSER_TYPE")

        self.home_url = "https://www.cdc.com.sg"
        self.booking_url = "https://www.cdc.com.sg:8080"
        
        self.captcha_solver = captcha_solver
        self.log = log
        
        self.username = login_credentials["username"]
        self.password = login_credentials["password"]
        
        options = browser_type.lower() == "firefox" and webdriver.FirefoxOptions() or webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--no-proxy-server")

        self.driver =  ( browser_type.lower() == "firefox" and webdriver.Firefox(executable_path="drivers/geckodriver", options=options) 
                         or 
                         webdriver.Chrome(executable_path="drivers/chromedriver.exe", options=options))
        
        self.driver.set_window_size(1600, 768)
        super().__init__(username=self.username, password=self.password, headless=headless)
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass #self.driver.close()
        
    def _open_index(self, path: str, sleep_delay = None):
        self.driver.get(f"{self.booking_url}/{path}")

        if sleep_delay:
            time.sleep(sleep_delay)
            
    def __str__(self):
        return super().__str__()
    
        
    def check_access_rights(self, webpage_name:str):
        if "Alert.aspx" in self.driver.current_url:
            self.log.info(f"You do not have access to {webpage_name}.")
            return False
        return True
        
    def dismiss_normal_captcha(self, solve_captcha:bool=False, force_enabled:bool=False):
        is_captcha_present = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_CaptchaImg", timeout=5)
        if is_captcha_present:
            success, _ = self.captcha_solver.solve(driver=self.driver, captcha_type="normal_captcha", force_enable=force_enabled)
            return False
            
    def get_course_data(self):
        course_selection = Select(self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlCourse"))
        number_of_options = len(course_selection.options)
        
        course_data = {"course_selection" :course_selection, "available_courses" : []}
        
        for option_index in range(0, number_of_options):
            option = course_selection.options[option_index]
            course_data["available_courses"].append(str(option.text.strip()))

        return course_data
        
    def select_course_from_name(self, course_data:Dict, course_name:str):
        for selection_idx in range(0, len(course_data["available_courses"])):
            current_course = course_data["available_courses"][selection_idx]
            if course_name in current_course:
                course_data["course_selection"].select_by_index(selection_idx)
                return selection_idx
        return False
    
    def open_home_page(self, sleep_delay = None):
        self.driver.get(self.home_url)
        assert "ComfortDelGro" in self.driver.title
        
        if sleep_delay:
            time.sleep(sleep_delay)
        
    def account_login(self):
        self.open_home_page(sleep_delay=2)
        
        prompt_login_btn = selenium_common.wait_for_elem(self.driver, By.XPATH, "//*[@id=\"top-menu\"]/ul/li[10]/a")
        prompt_login_btn.click()
        
        learner_id_input = selenium_common.wait_for_elem(self.driver, By.NAME, "userId")
        password_input = selenium_common.wait_for_elem(self.driver, By.NAME, "password")

        learner_id_input.send_keys(self.username)
        password_input.send_keys(self.password)

        # wait for user to solve recaptcha
        success, status_msg = self.captcha_solver.solve(driver=self.driver, captcha_type="recaptcha_v2")
        if success:
            login_btn = selenium_common.wait_for_elem(self.driver, By.ID, "BTNSERVICE2")
            login_btn.click()
            
            _, alert_text = selenium_common.dismiss_alert(driver=self.driver, timeout=5)    
            if "complete the captcha" in alert_text:
                self.log.info("Wrong captcha given.")
                self.account_logout()
                time.sleep(1)
                return self.account_login()
            else:
                return True
                
    def open_etrial_test_book_page(self):
        self._open_index("NewPortal/Booking/BookingETrial.aspx", sleep_delay=1)

        if self.check_access_rights("Booking E-trial Test"):
            course_data = self.get_course_data()
            if self.select_course_from_name(course_data, "E-Trial Test"):
                if self.dismiss_normal_captcha(True, force_enabled=True):
                    time.sleep(0.5)
                    return True
                else:
                    return self.open_etrial_test_book_page()
        return False 
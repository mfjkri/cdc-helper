import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from abstracts.cdc_abstract import CDCAbstract, Types

from utils.common import selenium_common
from utils.common import utils

class handler(CDCAbstract):
    def __init__(self, login_credentials, captcha_solver, log, browser_type="firefox", headless=False):
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
        self.driver.close()
        
    def _open_index(self, path: str, sleep_delay = None):
        self.driver.get(f"{self.booking_url}/{path}")

        if sleep_delay:
            time.sleep(sleep_delay)
        
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
        success, status_msg = self.captcha_solver.solve(driver=self.driver)
        self.log.debug(success, status_msg)
        
        login_btn = selenium_common.wait_for_elem(self.driver, By.ID, "BTNSERVICE2")
        login_btn.click()
        
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        if alert:
            alert.accept()
            
        self.log.info("Logged in successfully!")
        
    def account_logout(self):
        self._open_index("NewPortal/logOut.aspx?PageName=Logout")
        self.log.info("Logged out.")
        
    def open_booking_overview(self):
        self._open_index("NewPortal/Booking/StatementBooking.aspx")
        self._open_index("NewPortal/Booking/StatementBooking.aspx")

    def get_booked_lesson_date_time(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table#ctl00_ContentPlaceHolder1_gvBooked tr")

        # Check which practical lesson is the latest (in case there are e.g. lesson 5 and 6 bookings)
        latest_booked_practical_lesson_number = 0
        for row in rows:
            td_cells = row.find_elements_by_tag_name("td")
            if len(td_cells) > 0:
                lesson_name: str = td_cells[4].text
                if "2BL" in lesson_name:
                    lesson_number: int = int(lesson_name[len(lesson_name) - 1])
                    if lesson_number > latest_booked_practical_lesson_number:
                        latest_booked_practical_lesson_number = lesson_number

        for row in rows:
            td_cells = row.find_elements_by_tag_name("td")
            if len(td_cells) > 0:
                lesson_name = td_cells[4].text
                if "2BL" in lesson_name:
                    # do not consider old (to be cancelled) lessons because they could influence the earlier notification detection
                    if lesson_name[len(lesson_name) - 1] != str(latest_booked_practical_lesson_number):
                        self.log.debug(f"Not considering {lesson_name} lesson as there are more recent lessons available (2BL{latest_booked_practical_lesson_number})")
                        continue
                    self.lesson_name_practical = lesson_name
                    self.booked_sessions_practical.update({
                        td_cells[0].text: f'{td_cells[2].text} - {td_cells[3].text}'})
                if "RTT" in lesson_name:
                    self.lesson_name_rtt = lesson_name
                    self.booked_sessions_rtt.update({
                        td_cells[0].text: f'{td_cells[2].text} - {td_cells[3].text}'})
                if "BTT" in lesson_name:
                    self.lesson_name_btt = lesson_name
                    self.booked_sessions_btt.update({
                        td_cells[0].text: f'{td_cells[2].text} - {td_cells[3].text}'})
                if "PT" in lesson_name:
                    self.lesson_name_pt = lesson_name
                    self.booked_sessions_pt.update({
                        td_cells[0].text: f'{td_cells[2].text} - {td_cells[3].text}'})
        
    def open_theory_test_booking_page(self, type: str):
        self._open_index("NewPortal/Booking/BookingTT.aspx")
        self._open_index("NewPortal/Booking/BookingTT.aspx", sleep_delay=2)

        if "Alert.aspx" in self.driver.current_url:
            # "You do not have access to this facility."
            return False

        # now agree to terms and conditions
        try:
            terms_checkbox = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_chkTermsAndCond")
            terms_checkbox.click()

            agree_btn = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnAgreeTerms")
            agree_btn.click()
        except Exception:
            # ignore (sometimes check terms not necessary to be done)
            pass

        test_name_element = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblResAsmBlyDesc")

        if type == Types.BTT and "Basic Theory Test" in test_name_element.text:
            return True
        elif type == Types.RTT and "Riding Theory Test" in test_name_element.text:
            return True
        else:
            return False
    
    def open_practical_test_booking_page(self):
        self._open_index("NewPortal/Booking/BookingPT.aspx")
        self._open_index("NewPortal/Booking/BookingPT.aspx")

        if "Alert.aspx" in self.driver.current_url:
            # "You do not have access to this facility."
            return False

        try:
            # now say "No" to the "Do you currently hold other classes of Qualified Driving Licence?" question
            no_btn = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnNo")
            no_btn.click()

            # now agree to terms and conditions
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_chkTermsAndCond")))

            terms_checkbox = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_chkTermsAndCond")
            terms_checkbox.click()
            
            agree_btn = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btnAgreeTerms")            
            agree_btn.click()
        except Exception:
            # ignore (sometimes check terms not necessary to be done)
            pass
        return True
    
    def open_practical_lessons_booking(self, type=Types.PRACTICAL):
        self._open_index("NewPortal/Booking/BookingPL.aspx")
        self._open_index("NewPortal/Booking/BookingPL.aspx", sleep_delay=5)

        select = Select(self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlCourse"))

        # sometimes there are multiple options (like "CLASS 2B CIRCUIT REVISION" and "Class 2B Lesson 5")
        # in that case, choose the "Class 2B Lesson *" as this is much more relevant to be notified for
        select_indx = 1
        avail_options = []
        if len(select.options) > 1:
            for i, option in enumerate(select.options):
                # skip first option ("Select")
                if i == 0:
                    continue
                avail_options.append(option.text.strip())
                if "Class 2B Lesson" in option.text:
                    select_indx = i
        if len(select.options) > 2:
            self.log.info(f"There are two options ({avail_options}) available. Choosing the practical lesson ({select.options[select_indx].text.strip()}).")
        
        if len(avail_options) > 0:
            self.lesson_name_practical = avail_options[select_indx - 1]
            select.select_by_index(select_indx)

            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.ID, 'ctl00_ContentPlaceHolder1_lblSessionNo')))
            return True
        else:
            self.log.info("No available course found for booking of practical lessons!")
    
    # finds all available days and time slots (without knowing which slots are free or not)
    def get_all_session_date_times(self, type: str):
        for row in self.driver.find_elements(By.CSS_SELECTOR, "table#ctl00_ContentPlaceHolder1_gvLatestav tr"):
            th_cells = row.find_elements_by_tag_name("th")
            
            supported_type = type == Types.PRACTICAL or type == Types.BTT or type == Types.RTT or type == Types.PT or False
            selected_times_table =  ((type == Types.PRACTICAL and self.available_times_practical) or 
                                     (type == Types.BTT and self.available_times_btt) or 
                                     (type == Types.RTT and self.available_times_rtt) or 
                                     (type == Types.PT and self.available_times_pt) or None) 
                                    
            for i, th_cell in enumerate(th_cells):
                if i < 2:
                    continue
                if supported_type and selected_times_table:
                    selected_times_table.append(str(th_cell.text).split("\n")[1])

            td_cells = row.find_elements_by_tag_name("td")
            if len(td_cells) > 0:
                if supported_type and selected_times_table:
                    selected_times_table.append(td_cells[0].text)
                continue

    def get_all_available_sessions(self, type: str):
        # iterate over all "available motorcycle" images to get column and row
        # to later on get the date & time of that session
        input_elements = self.driver.find_elements(By.TAG_NAME, "input")
        last_practical_input_element: WebElement = None
        has_booked_lessons = False
        has_booked_lessons_in_view = False
        for input_element in input_elements:
            # Images1.gif -> available slot
            input_element_src = input_element.get_attribute("src")
            if "Images1.gif" in input_element_src or "Images3.gif" in input_element_src:
                # e.g. ctl00_ContentPlaceHolder1_gvLatestav_ctl02_btnSession4 (02 is row, 4 is column)
                element_id = str(input_element.get_attribute("id"))
                # remove 2 to remove th row (for mapping to available_days)
                row = int(element_id.split('_')[3][-1:]) - 2
                # remove 1 to remove first column (for mapping to available_times)
                column = int(element_id[-1]) - 1
                if "Images1.gif" in input_element_src:
                    available_sessions = {}
                    available_days = {}
                    available_times = {}

                    # get the input values depending on the type to avoid redundant code
                    if type == Types.PRACTICAL:
                        available_sessions = self.available_sessions_practical
                        available_days = self.available_days_practical
                        available_times = self.available_times_practical
                        last_practical_input_element = input_element
                    elif type == Types.BTT:
                        available_sessions = self.available_sessions_btt
                        available_days = self.available_days_btt
                        available_times = self.available_times_btt
                    elif type == Types.RTT:
                        available_sessions = self.available_sessions_rtt
                        available_days = self.available_days_rtt
                        available_times = self.available_times_rtt
                    elif type == Types.PT:
                        available_sessions = self.available_sessions_pt
                        available_days = self.available_days_pt
                        available_times = self.available_times_pt

                    # create or append to list of times (in case there are multiple sessions per day)
                    # row is date, column is time
                    if row not in available_sessions.keys():
                        available_sessions.update({available_days[row]: [available_times[column]]})
                    else:
                        available_sessions.update({available_days[row]: available_sessions[row].append(available_times[column])})

                if "Images3.gif" in input_element_src:
                    has_booked_lessons_in_view = True

        if type == Types.PRACTICAL:
            if has_booked_lessons_in_view or len(self.booked_sessions_practical) > 0:
                has_booked_lessons = True

            # check if next session can be booked, else skip (e.g. in case BTT not done or PDL for lesson 6)
            if "Lesson 6" in self.lesson_name_practical and last_practical_input_element is not None and not has_booked_lessons:
                last_practical_input_element_id = last_practical_input_element.get_attribute("id")
                try:
                    self.log.info("Attempting to reserve a session to check if user can book next lesson")
                    last_practical_input_element.click()
                    WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert = self.driver.switch_to.alert
                    
                    if "PDL" in alert.text or "BTT" in alert.text:
                        self.log.warning(f"User can't book lesson 6 because '{alert.text}'")
                        self.can_book_next_practical_lesson = False
                    alert.accept()
                except Exception:
                    # if no alert, means user could book lesson. Now we have to unreserve it again.
                    self.driver.find_element(By.ID, last_practical_input_element_id).click()
                    self.log.info("Reverted reservation of session successfully")
                    time.sleep(2)

        if type == Types.PT:
            if has_booked_lessons_in_view or len(self.booked_sessions_pt) > 0:
                has_booked_lessons = True

            # check if practical test can be booked, else skip (e.g. in case simulator modules not done)
            if last_practical_input_element is not None and not has_booked_lessons_in_view:
                last_practical_input_element_id = last_practical_input_element.get_attribute("id")
                try:
                    self.log.info("Attempting to reserve a session to check if user can book practical test")
                    last_practical_input_element.click()
                    WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                    alert = self.driver.switch_to.alert
                    self.log.warning(f"User can't book practical test because '{alert.text}'")
                    self.can_book_pt = False
                    alert.accept()
                except Exception:
                    # if no alert, means user could book lesson. Now we have to unreserve it again.
                    self.driver.find_element(By.ID, last_practical_input_element_id).click()
                    self.log.info("Reverted reservation of session successfully")
                    time.sleep(2)

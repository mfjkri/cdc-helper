import time

from selenium import webdriver
from selenium.webdriver.common.by import By
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
        #self.driver.close()
        pass
        
    def _open_index(self, path: str, sleep_delay = None):
        self.driver.get(f"{self.booking_url}/{path}")

        if sleep_delay:
            time.sleep(sleep_delay)
            
    def __str__(self):
        return super().__str__()
        
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
            
            alert_dismissed = selenium_common.dismiss_alert(driver=self.driver, timeout=5)    
            if alert_dismissed:
                self.log.info("Logged in successfully!")
            return alert_dismissed
        return False
        
        
    def account_logout(self):
        self._open_index("NewPortal/logOut.aspx?PageName=Logout")
        self.log.info("Logged out.")
        
    def open_booking_overview(self):
        self._open_index("NewPortal/Booking/StatementBooking.aspx")
        self._open_index("NewPortal/Booking/StatementBooking.aspx")

    #TODO: Update this
    def get_booked_lesson_date_time(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table#ctl00_ContentPlaceHolder1_gvBooked tr")

        # Check which practical lesson is the latest (in case there are e.g. lesson 5 and 6 bookings)
        latest_booked_practical_lesson_number = 0
        for row in rows:
            td_cells = row.find_elements_by_tag_name("td")
            if len(td_cells) > 0:
                lesson_name = td_cells[4].text
                if "2BL" in lesson_name:
                    lesson_number = int(lesson_name[len(lesson_name) - 1])
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
                        td_cells[0].text: f"{td_cells[2].text} - {td_cells[3].text}"})
                if "RTT" in lesson_name:
                    self.lesson_name_rtt = lesson_name
                    self.booked_sessions_rtt.update({
                        td_cells[0].text: f"{td_cells[2].text} - {td_cells[3].text}"})
                if "BTT" in lesson_name:
                    self.lesson_name_btt = lesson_name
                    self.booked_sessions_btt.update({
                        td_cells[0].text: f"{td_cells[2].text} - {td_cells[3].text}"})
                if "PT" in lesson_name:
                    self.lesson_name_pt = lesson_name
                    self.booked_sessions_pt.update({
                        td_cells[0].text: f"{td_cells[2].text} - {td_cells[3].text}"})
        
    def open_theory_test_booking_page(self, field_type:str):
        self._open_index("NewPortal/Booking/BookingTT.aspx", sleep_delay=2)


        if "Alert.aspx" in self.driver.current_url:
            self.log.info("You do not have access to Booking TT.")
            return False

        # solve captcha
        is_captcha_present = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_CaptchaImg")
        if is_captcha_present:
            success, status_msg = self.captcha_solver.solve(driver=self.driver, captcha_type="normal_captcha", force_enable=False)
            captcha_submit_btn = selenium_common.wait_for_elem(self.driver, By.ID, "ctl00_ContentPlaceHolder1_Button1")
            captcha_submit_btn.click()
            
        #dismiss alert if found
        _, alert_text = selenium_common.dismiss_alert(driver=self.driver, timeout=5)   
        
        if "incorrect captcha" in alert_text:
            selenium_common.dismiss_alert(driver=self.driver, timeout=5)   
            time.sleep(1)
            self.log.info("Normal captcha failed for opening theory test booking page.")
            return self.open_theory_test_booking_page(field_type)        

        # now agree to terms and conditions
        terms_checkbox = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_chkTermsAndCond")
        agree_btn = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_btnAgreeTerms")
        if terms_checkbox and agree_btn:
            terms_checkbox.click()
            agree_btn.click()
        
        test_name_element = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblResAsmBlyDesc")

        if field_type == Types.BTT and "Basic Theory Test" in test_name_element.text:
            return True
        elif field_type == Types.RTT and "Riding Theory Test" in test_name_element.text:
            return True
        else:
            return False
    
    def open_practical_test_booking_page(self):
        self._open_index("NewPortal/Booking/BookingPT.aspx")
        self._open_index("NewPortal/Booking/BookingPT.aspx", sleep_delay=2)

        if "Alert.aspx" in self.driver.current_url:
            self.log.info("You do not have access to Booking PT.")
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
    
    def open_practical_lessons_booking(self, field_type:str=Types.PRACTICAL):
        self._open_index("NewPortal/Booking/BookingPL.aspx")
        self._open_index("NewPortal/Booking/BookingPL.aspx", sleep_delay=5)

        course_selection = Select(self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ddlCourse"))
        number_of_options = len(course_selection.options)
        
        # sometimes there are multiple options (like "CLASS 2B CIRCUIT REVISION" and "Class 2B Lesson 5")
        # in that case, choose the "Class 2B Lesson *" as this is much more relevant to be notified for
        selection_idx = 1
        avail_options = ["-"]
        
        if number_of_options > 1:
            for option_index in range(1, number_of_options):
                option = course_selection.options[option_index]
                avail_options.append(str(option.text.strip()))
                
                if "Class 2B Lesson" in option.text:
                    selection_idx = option_index

            if number_of_options > 2:
                self.log.info(f"There are multiple options ({avail_options}) available. Choosing: {avail_options[selection_idx]}.")
        else:
            self.log.info("No available course found for booking of practical lessons!")
            return False
        
        self.lesson_name_practical = avail_options[selection_idx]
        course_selection.select_by_index(selection_idx)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_lblSessionNo')))
        return True
    
    #TODO: Update this
    # finds all available days and time slots (without knowing which slots are free or not)
    def get_all_session_date_times(self, field_type:str):
        for row in self.driver.find_elements(By.CSS_SELECTOR, "table#ctl00_ContentPlaceHolder1_gvLatestav tr"):
            th_cells = row.find_elements(By.TAG_NAME, "th")
                
            selected_times_array = (
                self.available_times_practical if field_type == Types.PRACTICAL else
                self.available_times_btt if field_type == Types.BTT else
                self.available_times_rtt if field_type == Types.RTT else
                self.available_times_pt
            )
            
            selected_days_array = (
                self.available_days_practical if field_type == Types.PRACTICAL else
                self.available_days_btt if field_type == Types.BTT else
                self.available_days_rtt if field_type == Types.RTT else
                self.available_days_pt
            )
                
            for i, th_cell in enumerate(th_cells):
                if i < 2:
                    continue
                selected_times_array.append(str(th_cell.text).split("\n")[1])

            td_cells = row.find_elements(By.TAG_NAME, "td")
            if len(td_cells) > 0:
                selected_days_array.append(td_cells[0].text)
                continue
    
    #TODO: Update this
    def get_all_available_sessions(self, field_type:str):
        # iterate over all "available motorcycle" images to get column and row
        # to later on get the date & time of that session
        input_elements = self.driver.find_elements(By.TAG_NAME, "input")
        last_practical_input_element = None
        has_booked_lessons = False
        has_booked_lessons_in_view = False
        
        for input_element in input_elements:
            # Images1.gif -> available slot
            input_element_src = input_element.get_attribute("src")
            if "Images1.gif" in input_element_src or "Images3.gif" in input_element_src:
                # e.g. ctl00_ContentPlaceHolder1_gvLatestav_ctl02_btnSession4 (02 is row, 4 is column)
                element_id = str(input_element.get_attribute("id"))
                element_id_spliced = element_id.split('_')
                
                row = int(element_id_spliced[3][-2:]) - 2
                column = int(element_id_spliced[-1][10:]) - 1 

                if "Images1.gif" in input_element_src:
                    
                    available_sessions = (
                        self.available_sessions_practical if field_type == Types.PRACTICAL else
                        self.available_sessions_btt if field_type == Types.BTT else
                        self.available_sessions_rtt if field_type == Types.RTT else
                        self.available_sessions_pt
                    )
                    
                    available_days = (
                        self.available_days_practical if field_type == Types.PRACTICAL else
                        self.available_days_btt if field_type == Types.BTT else
                        self.available_days_rtt if field_type == Types.RTT else
                        self.available_days_pt
                    )
                    
                    available_times = (
                        self.available_times_practical if field_type == Types.PRACTICAL else
                        self.available_times_btt if field_type == Types.BTT else
                        self.available_times_rtt if field_type == Types.RTT else
                        self.available_times_pt
                    )
                    
                    last_practical_input_element = (
                        input_element if field_type == Types.PRACTICAL else last_practical_input_element
                    )
                    
                    # create or append to list of times (in case there are multiple sessions per day)
                    # row is date, column is time
                    if available_days[row] not in available_sessions.keys():
                        available_sessions.update({available_days[row]: [available_times[column]]})
                    else:
                        available_sessions[available_days[row]].append(available_times[column])

                if "Images3.gif" in input_element_src:
                    has_booked_lessons_in_view = True
                    
        # TODO: To confirm this part works
        if field_type == Types.PRACTICAL:
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

        if field_type == Types.PT:
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

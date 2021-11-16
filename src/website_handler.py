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
    def __init__(self, login_credentials, captcha_solver, log, notification_manager, browser_config):
        browser_type = browser_config["type"] or "firefox"
        headless = browser_config["headless_mode"] or False
        
        if browser_type.lower() != "firefox" and browser_type.lower() != "chrome":
            log.error("Invalid browser_type was given!")
            raise Exception("Invalid BROWSER_TYPE")

        self.home_url = "https://www.cdc.com.sg"
        self.booking_url = "https://www.cdc.com.sg:8080"
        
        self.captcha_solver = captcha_solver
        self.log = log
        self.notification_manager = notification_manager
        
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
            
    def __str__(self):
        return super().__str__()

    def check_call_depth(self, call_depth:int):
        if call_depth > 4:
            self.account_logout()
            self.account_login()
            return False
        return True
    
    def check_access_rights(self, webpage_name:str):
        if "Alert.aspx" in self.driver.current_url:
            self.log.info(f"You do not have access to {webpage_name}.")
            return False
        return True
        
    def dismiss_normal_captcha(self, solve_captcha:bool=False, secondary_alert_timeout:int=5, force_enabled:bool=False):
        is_captcha_present = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_CaptchaImg", timeout=5)
        if is_captcha_present:
            if solve_captcha:
                success, _ = self.captcha_solver.solve(driver=self.driver, captcha_type="normal_captcha", force_enable=force_enabled)
                if success:
                    captcha_submit_btn = selenium_common.wait_for_elem(self.driver, By.ID, "ctl00_ContentPlaceHolder1_Button1")
                    captcha_submit_btn.click()
                else:
                    return False
            else:
                captcha_close_btn = selenium_common.wait_for_elem(self.driver, By.CLASS_NAME, "close")
                captcha_close_btn.click()
        else:
            return True
            
        #dismiss alert if found
        _, alert_text = selenium_common.dismiss_alert(driver=self.driver, timeout=2)   
        if "incorrect captcha" in alert_text:
            selenium_common.dismiss_alert(driver=self.driver, timeout=secondary_alert_timeout)   
            self.log.info("Normal captcha failed for opening theory test booking page.")
            return False  
        return True
    
    def accept_terms_and_conditions(self):
        terms_checkbox = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_chkTermsAndCond")
        agree_btn = selenium_common.is_elem_present(self.driver, By.ID, "ctl00_ContentPlaceHolder1_btnAgreeTerms")
        if terms_checkbox and agree_btn:
            terms_checkbox.click()
            agree_btn.click()
            
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
            
    def select_course_from_idx(self, course_data:Dict, course_idx:str):
        if course_idx > 0 and course_idx < len(course_data["available_courses"]):
            self.log.error(f"Course selected is out of range. {course_data['available_courses']}")
            return False
        
        course_data["course_selection"].select_by_index(course_idx)
        return course_data["available_courses"][course_idx]
        
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
                self.logged_in = True
                return True
        
    def account_logout(self):
        self._open_index("NewPortal/logOut.aspx?PageName=Logout")
        self.log.info("Logged out.")
        self.logged_in = False
        
    def open_booking_overview(self):
        self._open_index("NewPortal/Booking/StatementBooking.aspx")
        self._open_index("NewPortal/Booking/StatementBooking.aspx")

    def get_booked_lesson_date_time(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table#ctl00_ContentPlaceHolder1_gvBooked tr")

        # Check which practical lesson is the latest (in case there are e.g. lesson 5 and 6 bookings)
        latest_booked_practical_lesson_number = 0
        for row in rows:
            td_cells = row.find_elements(By.TAG_NAME, "td")
            if len(td_cells) > 0:
                lesson_name = td_cells[4].text
                if "2BL" in lesson_name:
                    lesson_number = int(lesson_name[len(lesson_name) - 1])
                    if lesson_number > latest_booked_practical_lesson_number:
                        latest_booked_practical_lesson_number = lesson_number

        for row in rows:
            td_cells = row.find_elements(By.TAG_NAME, "td")
            if len(td_cells) > 0:
                lesson_name = td_cells[4].text
                
                field_type = (
                    Types.PRACTICAL if "2BL" in lesson_name else
                    Types.ETT if "E-TRIAL" in lesson_name else
                    Types.BTT if "BTT" in lesson_name else
                    Types.RTT if "RTT" in lesson_name else
                    Types.PT if "PT" in lesson_name else
                    None
                )
                
                if field_type:
                    if field_type != Types.PRACTICAL or (field_type == Types.PRACTICAL and lesson_name[len(lesson_name) - 1] == str(latest_booked_practical_lesson_number)):
                        self.set_attribute_with_fieldtype("lesson_name", field_type, lesson_name)
                        selected_booked_sessions = self.get_attribute_with_fieldtype("booked_sessions", field_type)
                        
                        if td_cells[0].text not in selected_booked_sessions.keys():
                            selected_booked_sessions.update({td_cells[0].text: [f"{td_cells[2].text} - {td_cells[3].text}"]})
                        else:
                            selected_booked_sessions[td_cells[0].text].append(f"{td_cells[2].text} - {td_cells[3].text}")
    
    def open_etrial_test_book_page(self, call_depth:int=0):
        if not self.check_call_depth(call_depth):
            call_depth = 0
        self._open_index("NewPortal/Booking/BookingETrial.aspx", sleep_delay=1)

        if self.check_access_rights("Booking E-trial Test"):
            course_data = self.get_course_data()
            if self.select_course_from_name(course_data, "E-Trial Test"):
                if self.dismiss_normal_captcha(True, secondary_alert_timeout=1):
                    time.sleep(0.5)
                    return True
                else:
                    return self.open_etrial_test_book_page(call_depth=call_depth+1)
        return False 
        
    def open_theory_test_booking_page(self, field_type:str, call_depth:int=0):
        if not self.check_call_depth(call_depth):
            call_depth = 0
        self._open_index("NewPortal/Booking/BookingTT.aspx", sleep_delay=1)

        if self.check_access_rights("Booking Theory Test"):
            if self.dismiss_normal_captcha(False):
                time.sleep(0.5)  
                self.accept_terms_and_conditions()
                
                test_name_element = selenium_common.wait_for_elem(self.driver, By.ID, "ctl00_ContentPlaceHolder1_lblResAsmBlyDesc")
                return (field_type == Types.BTT and "Basic Theory Test" in test_name_element.text) or (field_type == Types.RTT and "Riding Theory Test" in test_name_element.text) 
            else:
                return self.open_theory_test_booking_page(field_type, call_depth=call_depth+1)
        else:
            return False
    
    # TODO: Fix and test this part when I have access
    def open_practical_test_booking_page(self, call_depth:int=0):
        if not self.check_call_depth(call_depth):
            call_depth = 0
        self._open_index("NewPortal/Booking/BookingPT.aspx", sleep_delay=1)

        if self.check_access_rights("Booking Practical Test"):
            if self.dismiss_normal_captcha(True):
                time.sleep(0.5)  
                self.accept_terms_and_conditions()

                return True
            else:
                return self.open_practical_test_booking_page(call_depth=call_depth+1)
        else:
            return False
    
    # TODO: Fix and test this part when I have access
    def open_practical_lessons_booking(self, call_depth:int=0):
        if not self.check_call_depth(call_depth):
            call_depth = 0
        self._open_index("NewPortal/Booking/BookingPL.aspx", sleep_delay=1)
        
        if self.check_access_rights("Booking Practical Test"):
            course_data = self.get_course_data()
            if self.select_course_from_name(course_data, "Class 2B Lesson") or self.select_course_from_idx(course_data, 1):
                if self.dismiss_normal_captcha(True):
                    time.sleep(0.5)
                    WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'ctl00_ContentPlaceHolder1_lblSessionNo')))
                    return True
                else:
                    return self.open_practical_lessons_booking(call_depth=call_depth+1)
        return False
    
    def get_all_session_date_times(self, field_type:str):
        for row in self.driver.find_elements(By.CSS_SELECTOR, "table#ctl00_ContentPlaceHolder1_gvLatestav tr"):
            th_cells = row.find_elements(By.TAG_NAME, "th")
            
            selected_times_array = self.get_attribute_with_fieldtype("available_times", field_type)
            selected_days_array = self.get_attribute_with_fieldtype("available_days", field_type)
                
            for i, th_cell in enumerate(th_cells):
                if i < 2:
                    continue
                selected_times_array.append(str(th_cell.text).split("\n")[1])

            td_cells = row.find_elements(By.TAG_NAME, "td")
            if len(td_cells) > 0:
                selected_days_array.append(td_cells[0].text)
    
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
                    
                    available_sessions = self.get_attribute_with_fieldtype("available_sessions", field_type)
                    available_days = self.get_attribute_with_fieldtype("available_days", field_type)
                    available_times = self.get_attribute_with_fieldtype("available_times", field_type)                                         
                    
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
                    
    def send_notification_update(self, field_type:str):
        earlier_sessions = self.get_attribute_with_fieldtype("earlier_sessions", field_type)
        booked_sessions = self.get_attribute_with_fieldtype("booked_sessions", field_type)

        notif_msg = "\n"
        
        notif_msg += "--------------------------\n"
        notif_msg += "Booked sesssions:\n"
        for _, booked_date_str in enumerate(booked_sessions):
            notif_msg += f"{booked_date_str}:\n"
            
            booked_time_slots = booked_sessions[booked_date_str]
            for i in range (0, len(booked_time_slots)):
                time_slot = booked_time_slots[i]
                notif_msg += f"  -> {time_slot}\n"
        notif_msg += "--------------------------\n\n"
        
        notif_msg += "Available sesssions:\n"
        for _, earlier_date_str in enumerate(earlier_sessions):
            notif_msg += f"{earlier_date_str}:\n"
            
            earlier_time_slots = earlier_sessions[earlier_date_str]
            for i in range (0, len(earlier_time_slots)):
                time_slot = earlier_time_slots[i]
                notif_msg += f"  -> {time_slot}\n"
            notif_msg += "\n"

        self.notification_manager.send_notification_all(
            title=f"{field_type.upper()}: UPDATE",
            msg=notif_msg
        )
        
        return notif_msg

    def check_if_earlier_available_sessions(self, field_type:str):
        available_sessions = self.get_attribute_with_fieldtype("available_sessions", field_type)    
        booked_sessions = self.get_attribute_with_fieldtype("booked_sessions", field_type)
        earlier_sessions = self.get_attribute_with_fieldtype("earlier_sessions", field_type)
        hasChanges = False
        
        for _, available_date_str in enumerate(available_sessions):
            available_date = convert_to_datetime(available_date_str)
            
            for _, booked_date_str in enumerate(booked_sessions):
                booked_date = convert_to_datetime(booked_date_str)
                
                if available_date < booked_date:
                    available_time_slots = available_sessions[available_date_str]

                    if available_date_str not in earlier_sessions.keys():
                        hasChanges = True
                        earlier_sessions[available_date_str] = available_time_slots
                    else:
                        for i in range(0, len(available_time_slots)):
                            time_slot = available_time_slots[i]
                            
                            if time_slot not in earlier_sessions[available_date_str]:
                                hasChanges = True
                                earlier_sessions[available_date_str].append(time_slot)
                    
                elif available_date == booked_date:
                    booked_time_slots = booked_sessions[booked_date_str] 
                    available_time_slots = available_sessions[available_date_str]
                    
                    for i in range(0, len(available_time_slots)):
                        available_time_slot = available_time_slots[i]
                        for j in range(0, len(booked_time_slots)):
                            booked_time_slot = booked_time_slots[j]
                            
                            available_datetime = convert_to_datetime(available_date_str, available_time_slot)
                            booked_datetime = convert_to_datetime(booked_date_str, booked_time_slot)
                            
                            if available_datetime < booked_datetime:
                                if available_date_str not in earlier_sessions.keys():
                                    hasChanges = True
                                    earlier_sessions[available_date_str] = [available_time_slot]
                                else:
                                    if available_time_slot not in earlier_sessions[available_date_str]:
                                        hasChanges = True
                                        earlier_sessions[available_date_str].append(available_time_slot)

        if hasChanges:
            notif_msg = self.send_notification_update(field_type)
            self.log.info(f"There are updates to {field_type.upper()} available sessions. More info here: \n{notif_msg}")
            
        return hasChanges
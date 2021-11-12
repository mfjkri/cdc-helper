import traceback, time, os, tempfile, base64
from types import LambdaType

from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException, NetworkException
from twocaptcha.solver import TimeoutException

from utils.log import Log
from utils.common import selenium_common, utils

from selenium import webdriver
from selenium.webdriver.common.by import By

class Captcha:
    def __init__(self, api_key:str, log:Log, is_enabled:bool=False, debug_enabled:bool=False):
        solver = TwoCaptcha(apiKey=api_key)
        self.solver = solver
        self.log = log
        self.enabled = is_enabled
        self.debug_enabled = debug_enabled
        
    def _solve_captcha(self, solve_callback:LambdaType, result_callback:LambdaType, debug_enabled:bool):
        result = None
        try:
            result = solve_callback()
            self.log.debug_if(debug_enabled, "Received 2Captcha response...")
        except TimeoutException as e:
            self.log.debug_if(debug_enabled, f"2Captcha API has timed-out! : {str(e)}")
            result = (False, f"TIMEOUT: {str(e)}")
        except NetworkException as e:
            self.log.debug_if(debug_enabled, f"2Captcha API has encountered a network error! : {str(e)}")
            result = (False, f"NETWORK_ERROR: {str(e)}")
        except ApiException as e:
            self.log.debug_if(debug_enabled, f"2Captha API has encountered an API error : {str(e)}")
            result = (False, f"API_ERROR: {str(e)}")
        except Exception as e:
            self.log.error(e)
            self.log.error(traceback.format_exc())
            result = (False, f"UNKNOWN_ERROR : {str(e)}")
        else:
            result_callback(result)
            result = (True, f"SOLVED: {str(result)}")
        finally:
            self.log.debug_if(debug_enabled, result)
            return result
    
    def normal_captcha(self, driver:webdriver, page_url:str, debug_enabled:bool):
        captcha_element = selenium_common.is_elem_present(driver, By.ID, "ctl00_ContentPlaceHolder1_CaptchaImg")
        captcha_input = selenium_common.is_elem_present(driver, By.ID, "ctl00_ContentPlaceHolder1_txtVerificationCode")

        if captcha_element and captcha_input:
            img_base64_str = captcha_element.get_attribute("src")[23:];
            img_base64 = str.encode(img_base64_str)

            captcha_image_filepath = "temp/" + f"normal_captcha_{utils.get_datetime_now('dd-mm-yy hh:mm:ss')}.jpeg"
            with open(captcha_image_filepath, "wb") as image_file:
                image_file.write(base64.decodebytes(img_base64))
                image_file.close()
            
            success, status_msg = self._solve_captcha(
                solve_callback=lambda:self.solver.normal(captcha_image_filepath),
                result_callback=lambda result:captcha_input.send_keys(str(result["code"])),
                debug_enabled=debug_enabled
            )

            utils.remove_files([captcha_image_filepath])
            return (success, status_msg)
            
    def recaptcha_v2(self, driver:webdriver, page_url:str, debug_enabled:bool):
        site_key_element = selenium_common.is_elem_present(driver, By.CSS_SELECTOR, "[data-sitekey]")
        if site_key_element:        
            site_key = site_key_element.get_attribute("data-sitekey")
            return self._solve_captcha(
                solve_callback=lambda:self.solver.recaptcha(sitekey=site_key, url=page_url),
                result_callback=lambda result:driver.execute_script("""document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(str(result["code"]))),
                debug_enabled=debug_enabled
            )
            
        else:
            return (False, f"NO RECAPTCHA_V2 FOUND IN: {page_url}")
        
    def solve(self, driver:webdriver, captcha_type:str = None, page_url:str=None, force_enable:bool=False, force_debug:bool=False):
        t_start = time.perf_counter()
        page_url = page_url or driver.current_url
        captcha_type = captcha_type or "recaptcha_v2"
        debug_enabled = self.debug_enabled or force_debug

        if self.enabled or force_enable:
            self.log.debug_if(debug_enabled, f"Solving {captcha_type.upper()} for: {page_url}")
            
            success, status_msg = False, ""
            
            if captcha_type.lower() == "recaptcha_v2":
                success, status_msg = self.recaptcha_v2(driver=driver, page_url=page_url, debug_enabled=debug_enabled)
            elif captcha_type.lower() == "normal_captcha":
                success, status_msg = self.normal_captcha(driver=driver, page_url=page_url, debug_enabled=debug_enabled)
            
            if success:
                self.log.debug_if(debug_enabled, "Took {t} seconds to solve the {n} using two-captcha!".format(
                    t = time.perf_counter() - t_start, 
                    n = captcha_type.upper()
                ))
            return (success, status_msg)
        else:
            self.log.debug_if(debug_enabled, f"Manually solving CAPTCHA for: {page_url}")
            input("Press enter to proceed: ")
            self.log.debug_if(debug_enabled, "Took exactly {t} seconds to solve the {n} manually!".format(
                t = time.perf_counter() - t_start, 
                n = captcha_type.upper()
            ))
            return (True, "Manually solved CAPTCHA")
        
        
            
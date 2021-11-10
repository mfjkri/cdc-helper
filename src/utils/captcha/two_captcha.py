import traceback, time

from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException, NetworkException
from twocaptcha.solver import TimeoutException

from utils.log import Log
from selenium import webdriver

class Captcha:
    def __init__(self, api_key:str, log:Log, is_enabled:bool=False, debug_enabled:bool=False):
        solver = TwoCaptcha(apiKey=api_key)
        self.solver = solver
        self.log = log
        self.enabled = is_enabled
        self.debug_enabled = debug_enabled
    
    def _debug_wrapper(self, debug_enabled, debug_type, msg):
        if debug_enabled:
            debug_type(msg)
        
    def solve(self, driver:webdriver, page_url:str=None):
        t_start = time.perf_counter()
        page_url = page_url or driver.current_url
        
        if self.enabled:
            self.log.debug_if(self.debug_enabled, f"Solving CAPTCHA for: {page_url}")
            site_key_element = driver.find_element_by_css_selector("[data-sitekey]")
            site_key = site_key_element.get_attribute("data-sitekey")
            
            try:
                result = self.solver.recaptcha(sitekey=site_key, url=page_url)
                self.log.debug_if(self.debug_enabled, "Received 2Captcha response...")
            except TimeoutException as e:
                self.log.debug_if(self.debug_enabled, f"2Captcha API has timed-out! : {str(e)}")
                result = (False, f"TIMEOUT: {str(e)}")
            except NetworkException as e:
                self.log.debug_if(self.debug_enabled, f"2Captcha API has encountered a network error! : {str(e)}")
                result = (False, f"NETWORK_ERROR: {str(e)}")
            except ApiException as e:
                self.log.debug_if(self.debug_enabled, f"2Captha API has encountered an API error : {str(e)}")
                result = (False, f"API_ERROR: {str(e)}")
            except Exception as e:
                self.log.error(e)
                self.log.error(traceback.format_exc())
                result = (False, f"UNKNOWN_ERROR : {str(e)}")
            else:
                driver.execute_script("""document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(str(result["code"])))
                self.log.debug_if(self.debug_enabled, "Took {t} seconds to solve the reCaptcha using two-captcha!".format(t = time.perf_counter() - t_start))
                result = (True, f"SOLVED: {str(result)}")
            finally:
                self.log.debug("t", result)
                return result
        else:
            self.log.debug_if(self.debug_enabled, f"Manually solving CAPTCHA for: {page_url}")
            input("Press enter to proceed: ")
            self.log.debug_if(self.debug_enabled, "Took exactly {t} seconds to solve the reCaptcha manually!".format(t = time.perf_counter() - t_start))
            return (True, "Manually solved CAPTCHA")
        
        
            
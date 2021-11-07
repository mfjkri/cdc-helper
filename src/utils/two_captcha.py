import traceback, time
from twocaptcha import TwoCaptcha

from utils.log import Log
from selenium import webdriver

class TwoCaptcha:
    def __init__(self, api_key:str, log:Log, is_enabled:bool=False, debug_enabled:bool=False):
        solver = TwoCaptcha(apiKey=api_key)
        self.solver = solver
        self.log = log
        self.enabled = is_enabled
        self.debug_enabled = debug_enabled
    
    def _debug_wrapper(self, debug_enabled, debug_type, message):
        if debug_enabled:
            debug_type(message)
        
    def solve(self, driver:webdriver, page_url:str=None):
        t_start = time.perf_counter()
        page_url = page_url or driver.current_url
        
        if self.enabled:
            self._debug_wrapper(debug_enabled=self.debug_enabled, debug_type=self.log.info, message="Solving CAPTCHA for: " + page_url)
            site_key_element = driver.find_element_by_css_selector("[data-sitekey]")
            site_key = site_key_element.get_attribute("data-sitekey")
            
            try:
                result = self.solver.recaptcha(sitekey=site_key, url=page_url)
                self._debug_wrapper(debug_enabled=self.debug_enabled, debug_type=self.log.info, message="Solved CAPTCHA!")
            except Exception as e:
                self.log.error(e)
                self.log.error(traceback.format_exc())
                return False
            else:
                driver.execute_script("""document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(str(result["code"])))
                self._debug_wrapper(debug_enabled=self.debug_enabled, debug_type=self.log.info, message="Took {t} seconds to solve the reCaptcha using two-captcha!".format(t = time.perf_counter() - t_start))
                return True
        else:
            self._debug_wrapper(debug_enabled=self.debug_enabled, debug_type=self.log.info, message="Manually solving  CAPTCHA for: " + page_url)
            input("Press enter to proceed: ")
            self._debug_wrapper(debug_enabled=self.debug_enabled, debug_type=self.log.info, message="Took exactly {t} seconds to solve the reCaptcha manually!".format(t = time.perf_counter() - t_start))
            return True
        
        
            
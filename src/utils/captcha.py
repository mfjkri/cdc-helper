import traceback, time
from twocaptcha import TwoCaptcha

class Captcha:
    def __init__(self, api_key, log, is_enabled):
        solver = TwoCaptcha(apiKey=api_key)
        self.solver = solver
        self.log = log
        self.enabled = is_enabled
        
    def solve(self, driver, page_url = None):
        t_start = time.perf_counter()
        page_url = page_url or driver.current_url
        
        if self.enabled:
            self.log.info('Solving CAPTCHA for: ' + page_url)
            site_key_element = driver.find_element_by_css_selector('[data-sitekey]')
            site_key = site_key_element.get_attribute("data-sitekey")
            
            try:
                result = self.solver.recaptcha(sitekey=site_key, url=page_url)
                self.log.info('Solved CAPTCHA!')
            except Exception as e:
                self.log.error(e)
                self.log.error(traceback.format_exc())
                return False
            else:
                driver.execute_script("""document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(str(result['code'])))
                self.log.info("Took {t} seconds to solve the reCaptcha using two-captcha!".format(t = time.perf_counter() - t_start))
                return True
        else:
            self.log.info('Manually solving CAPTCHA for: ' + page_url)
            input("Press enter to proceed: ")
            self.log.info("Took exactly {t} seconds to solve the reCaptcha manually!".format(t = time.perf_counter() - t_start))
            return True
        
        
            
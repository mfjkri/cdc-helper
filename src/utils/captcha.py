import traceback
from twocaptcha import TwoCaptcha

is_enabled = True

class Captcha:
    def __init__(self, api_key, log):
        solver = TwoCaptcha(apiKey=api_key)
        self.solver = solver
        self.log = log
        
    def solve(self, driver, page_url = None):
        page_url = page_url or driver.current_url
        
        if is_enabled:
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
                self.log.info('Executed captcha script! + ' + str(result))
                return True
        else:
            self.log.info('Manually solving CAPTCHA for: ' + page_url)
            input("Press enter to proceed: ")
            return True
            
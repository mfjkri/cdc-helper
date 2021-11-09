from enum import Enum
from typing import Tuple
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
import requests
import os
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import selenium

from utils.log import Log
from utils.common import selenium_common
from utils.common import utils

class NoCaptchaException(Exception):
    def __init__(self, error, *args: object) -> None:
        super().__init__(*args)

class RatedLimitedException(Exception):
    def __init__(self, error, *args: object) -> None:
        super().__init__(*args)


class Captcha:
    def __init__(self, log:Log, is_enabled:bool=False):
        self.log = log
        self.is_enabled = is_enabled
    
    def _get_default_iframe(self, driver:selenium.webdriver):
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            if iframe.get_attribute("src").startswith("https://www.google.com/recaptcha/api2/anchor"):
                return iframe
            
        return None

    
    def solve(self, driver:selenium.webdriver, captcha_iframe=None, timeout:int=5):
        return_status = None

        captcha_iframe = captcha_iframe or self._get_default_iframe(driver)
        if not captcha_iframe:
            return (False, "CAPTCHA NOT FOUND")
        
        temp_dir = tempfile.gettempdir()
        self.log.debug(temp_dir)
        mp3_file = os.path.join(temp_dir, "_tmp.mp3")
        wav_file = os.path.join(temp_dir, "_tmp.wav")
        temp_files = [mp3_file, wav_file]

        time.sleep(2)

        
        # Switch current context
        driver.switch_to.frame(captcha_iframe)

        # Click the checkbox
        do_captcha_checkbox = selenium_common.wait_for_elem(driver, By.CLASS_NAME, "recaptcha-checkbox-border", timeout)
        do_captcha_checkbox.click()

        time.sleep(5)
        

        # Switch back to the main page since actual captcha window is on another iframe
        driver.switch_to.default_content()

        try:
            driver.switch_to.frame(selenium_common.wait_for_elem(driver, By.XPATH, "//iframe[@title=\"recaptcha challenge\"]", timeout))

            # Get the audio challenge instead
            select_audio_captcha_btn = selenium_common.wait_for_elem(driver, By.ID, "recaptcha-audio-button", timeout)
            select_audio_captcha_btn.click()

            time.sleep(5)
            
            # Download & convert the file
            download_url = selenium_common.wait_for_elem(driver, By.CLASS_NAME, "rc-audiochallenge-tdownload-link", timeout)

            if not download_url:
                raise RatedLimitedException
            
            with open(mp3_file, "wb") as file:
                raw_link = download_url.get_attribute("href")
                read_mp3_file = requests.get(raw_link, allow_redirects=True)
                file.write(read_mp3_file.content)
                file.close()

            # Convert to wav here
            AudioSegment.from_mp3(mp3_file).export(wav_file, format="wav")

            # Using google's own api against them
            recognizer = sr.Recognizer()

            with sr.AudioFile(wav_file) as source:
                recorded_audio = recognizer.listen(source)
                text = recognizer.recognize_google(recorded_audio)

            # Type out the answer
            response_textbox = selenium_common.wait_for_elem(driver, By.ID, "audio-response", timeout)
            response_textbox.send_keys(text)

            time.sleep(5)
            

            # Click the "Verify" button to complete
            verify_btn = selenium_common.wait_for_elem(driver, By.ID, "recaptcha-verify-button", timeout)
            verify_btn.click()

            # Return the text used for the answer
            return_status = (True, text)

        except TimeoutException as e:
            return_status = (False, "CAPTCHA BYPASS HAS TIMED_OUT")

        except RatedLimitedException as e:
            return_status = (False , "CAPTCHA SERVICE HAS BEEN RATE LIMITED. PLEASE TRY AGAIN LATER")
        except Exception as e:
            return_status = (False, "UNKNOWN EXCEPTION THROWN: " + str(e))

        finally:
            driver.switch_to.default_content()
            utils.remove_files(temp_files)
            return return_status
            
    
    



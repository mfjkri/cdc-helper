#!/media/Programming/repos/py/_selenium/CDC_HELPER/venv/bin/python
import time
from src.website_handler import handler, Types

from src.utils.common import utils
from src.utils.log import Log
from src.utils.captcha.two_captcha import Captcha as TwoCaptcha
from src.utils.captcha.captcha_bypass import Captcha as CaptchaBypass
from src.utils.notifications.notification_manager import NotificationManager


if __name__ == "__main__":
    #captcha_solver = CaptchaBypass(log=log, is_enabled=True) 
    config = utils.load_config_from_yaml_file(file_path="config.yaml")

    log = Log(directory="logs/", name="cdc-helper", config=config["log_config"])
    captcha_solver = TwoCaptcha(log=log, config=config["two_captcha_config"])

    with handler(
            login_credentials=config["cdc_login_credentials"], 
            captcha_solver=captcha_solver, 
            log=log, 
            browser_config=config["browser_config"]
        ) as cdc_handler:
        
        success_logging_in = cdc_handler.account_login()
        
        while success_logging_in:
            cdc_handler.open_etrial_test_book_page()
            time.sleep(0.05)
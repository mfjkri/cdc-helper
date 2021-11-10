import time
from logging import log

from website_handler import handler, Types

from utils.common import utils
from utils.log import Log
from utils.captcha.two_captcha import Captcha as TwoCaptcha
from utils.captcha.captcha_bypass import Captcha as CaptchaBypass
from utils.notifications.notification_manager import NotificationManager


if __name__ == "__main__":
    #captcha_solver = CaptchaBypass(log=log, is_enabled=True) 
    log = Log(directory="logs/", name="cdc-helper", config={"LOG_LEVEL":1, "PRINT_TO_OUTPUT":True, "LOG_TO_FILE":True, "CLEAR_OUTPUT_ON_RESET":True, "SHOW_STACK":False})
    config = utils.load_config_from_yaml_file(file_path="config.yaml", log=log)
    captcha_solver = TwoCaptcha(api_key=config["two_captcha_apikey"], log=log, is_enabled=True, debug_enabled=config["captcha_debug"])
    notification_manager = NotificationManager(log = log, mail_config=config["mail_config"], telegram_config=config["telegram_config"])

    with handler(login_credentials=config["cdc_login_credentials"], captcha_solver=captcha_solver, log=log, browser_type="firefox", headless=False) as cdc_handler:
        cdc_handler.account_login()
        
        while True:
            # Step 2: Get booking information
            cdc_handler.open_booking_overview()
            cdc_handler.get_booked_lesson_date_time()

            # Step 3: Check for practical lesson availability
            if config["check_practical"]:
                cdc_handler.open_practical_lessons_booking(type=Types.PRACTICAL)
                if "REVISION" in cdc_handler.lesson_name_practical:
                    log.debug("No practical lesson available for user, seems user has completed practical lessons")
                else:
                    cdc_handler.get_all_session_date_times(type=Types.PRACTICAL)
                    cdc_handler.get_all_available_sessions(type=Types.PRACTICAL)
                    if cdc_handler.can_book_next_practical_lesson:
                        # TODO: Why does this print??
                        log.info("Earlier date available!") 
                        #inform_user_if_earlier_session_available(config["username"], type=Types.PRACTICAL)

            time.sleep(config["refresh_rate"])

    
        cdc_handler.account_logout()
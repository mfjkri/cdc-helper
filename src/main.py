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
    config = utils.load_config_from_yaml_file(file_path="config.yaml")

    log = Log(directory="logs/", name="cdc-helper", config=config["log_config"])
    captcha_solver = TwoCaptcha(api_key=config["two_captcha_apikey"], log=log, is_enabled=True, debug_enabled=config["captcha_debug"])
    notification_manager = NotificationManager(log = log, mail_config=config["mail_config"], telegram_config=config["telegram_config"])

    with handler(login_credentials=config["cdc_login_credentials"], captcha_solver=captcha_solver, log=log, browser_type="firefox", headless=False) as cdc_handler:
        success_logging_in = cdc_handler.account_login()
        monitored_types = config["monitored_types"]

        while True and success_logging_in:
            # Step 2: Get booking information
            cdc_handler.open_booking_overview()
            cdc_handler.get_booked_lesson_date_time()

            # Step 3: Check for practical lesson availability
            if monitored_types["practical"]:
                if cdc_handler.open_practical_lessons_booking(field_type=Types.PRACTICAL):
                    if "REVISION" in cdc_handler.lesson_name_practical:
                        log.debug("No practical lesson available for user, seems user has completed practical lessons")
                    else:   
                        #TODO: Test this part
                        cdc_handler.get_all_session_date_times(field_type=Types.PRACTICAL)
                        cdc_handler.get_all_available_sessions(field_type=Types.PRACTICAL)
                        if cdc_handler.can_book_next_practical_lesson:
                            log.info("Earlier date available!") 
                            #inform_user_if_earlier_session_available(config["username"], field_type=Types.PRACTICAL)
                else:
                    pass # No course found
            
            # Step 4: Check for btt availability as well
            if monitored_types["btt"]:
                if cdc_handler.open_theory_test_booking_page(field_type=Types.BTT):
                    cdc_handler.get_all_session_date_times(field_type=Types.BTT)
                    cdc_handler.get_all_available_sessions(field_type=Types.BTT)
                    #inform_user_if_earlier_session_available(config['username'], field_type=Types.BTT)
                else:
                    log.debug("BTT not bookable for user")
                    
            # TODO: Add more checks (RTT, PT)

            time.sleep(config["refresh_rate"])

    
        cdc_handler.account_logout()
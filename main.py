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
    program_config = config["program_config"]

    log = Log(directory="logs/", name="cdc-helper", config=config["log_config"])
    captcha_solver = TwoCaptcha(log=log, config=config["two_captcha_config"])
    notification_manager = NotificationManager(log = log, mail_config=config["mail_config"], telegram_config=config["telegram_config"])

    utils.clear_directory("temp/", log)

    with handler(
            login_credentials=config["cdc_login_credentials"], 
            captcha_solver=captcha_solver, 
            log=log, 
            notification_manager=notification_manager, 
            browser_config=config["browser_config"],
            program_config=program_config
        ) as cdc_handler:
        
        success_logging_in = cdc_handler.account_login()
        monitored_types = program_config["monitored_types"]

        while True:
            
            while not cdc_handler.logged_in:
                time.sleep(1)
            
            # Step 2: Get booking information
            cdc_handler.open_booking_overview()
            cdc_handler.get_booked_lesson_date_time()
            cdc_handler.get_reserved_lesson_date_time()

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
                            # TODO: Notify user if earlier sessions are available
                else:
                    pass # No course found
                
            if monitored_types["ett"]:
                if cdc_handler.open_etrial_test_book_page():
                    cdc_handler.get_all_session_date_times(field_type=Types.ETT)
                    cdc_handler.get_all_available_sessions(field_type=Types.ETT)
                    cdc_handler.check_if_earlier_available_sessions(Types.ETT)
                else:
                    log.debug("User does not have ETT as an available option.")
            
            if monitored_types["btt"]:
                if cdc_handler.open_theory_test_booking_page(field_type=Types.BTT):
                    cdc_handler.get_all_session_date_times(field_type=Types.BTT)
                    cdc_handler.get_all_available_sessions(field_type=Types.BTT)
                    cdc_handler.check_if_earlier_available_sessions(Types.BTT)
                else:
                    log.debug("User does not have BTT as an available option.")
                    
            if monitored_types["rtt"]:
                if cdc_handler.open_theory_test_booking_page(field_type=Types.RTT):
                    cdc_handler.get_all_session_date_times(field_type=Types.RTT)
                    cdc_handler.get_all_available_sessions(field_type=Types.RTT)
                    cdc_handler.check_if_earlier_available_sessions(Types.RTT)
                else:
                    log.debug("User does not have RTT as an available option.")
                    
            # TODO: Add more checks (SIMULATOR, PT)

            log.info(cdc_handler)
            if program_config["refresh_rate"]:
                time.sleep(program_config["refresh_rate"])
            else:
                break

    
        cdc_handler.account_logout()
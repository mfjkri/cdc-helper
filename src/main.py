#!/media/Programming/repos/py/_selenium/CDC_HELPER/venv/bin/python
import datetime
import time, sys, os
sys.path.insert(0, os.getcwd())

from src.website_handler import handler, Types

from src.utils.common import utils
from src.utils.log import Log
from src.utils.captcha.two_captcha import Captcha as TwoCaptcha
from src.utils.notifications.notification_manager import NotificationManager


if __name__ == "__main__":
    #captcha_solver = CaptchaBypass(log=log, is_enabled=True) 
    config = utils.load_config_from_yaml_file(file_path="config.yaml")
    program_config = config["program_config"]

    log = Log(directory="logs", name="cdc-helper", config=config["log_config"])
    captcha_solver = TwoCaptcha(log=log, config=config["two_captcha_config"])
    notification_manager = NotificationManager(log = log, mail_config=config["mail_config"], telegram_config=config["telegram_config"])

    utils.clear_directory("temp", log)

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
            
            cdc_handler.open_booking_overview()
            cdc_handler.get_booked_lesson_date_time()
            cdc_handler.get_reserved_lesson_date_time()
            
            for monitor_type, monitor_active in monitored_types.items():
                if monitor_active:
                    if cdc_handler.open_field_type_booking_page(field_type=monitor_type):
                        cdc_handler.get_all_session_date_times(field_type=monitor_type)
                        cdc_handler.get_all_available_sessions(field_type=monitor_type)
                        cdc_handler.check_if_earlier_available_sessions(field_type=monitor_type)
                    else:
                        log.debug(f"User does not have {monitor_type.upper()} as an available option.") 
            
            log.info(cdc_handler)
            cdc_handler.flush_notification_update()

            if program_config["refresh_rate"] > 0:
                sleep_time = program_config["refresh_rate"]
                cdc_handler.log.info(f"Program now sleeping for {datetime.timedelta(seconds=sleep_time)}...")
                time.sleep(program_config["refresh_rate"])
                cdc_handler.log.info(f"Program now resuming! Cached log in ?: {cdc_handler.logged_in}")
            else:
                break

        cdc_handler.account_logout()
        cdc_handler.driver.quit()
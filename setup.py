import os, argparse, logging, datetime, subprocess, sys

if __name__ == "__main__":
    
    is_windows, is_linux = "win32" in sys.platform, "linux" in sys.platform

    log = logging.getLogger("CDC_HANDLER setup")
    log.setLevel(10)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    terminal_output = logging.StreamHandler(sys.stdout)
    terminal_output.setFormatter(formatter)
    log.addHandler(terminal_output)

    log_filename = f"project_setup.log"
    log_file = logging.FileHandler(log_filename)
    log_file.setFormatter(formatter)
    log.addHandler(log_file)

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "--intepreter_keyword", 
        type=str,
        help="Python version to use (USE PYTHON 3 WHEN POSSIBLE) (dependent on your OS i.e python could point to either python 2 OR python3, Use python --version to check python version)",
        #default="python", 
        required=True
    )
    ARGS = PARSER.parse_args()
    
    prjDir = os.getcwd()
    log.info(f"Changing working directory to: {prjDir}")
    os.chdir(prjDir)


    # -------------------- Creating temp and logs directories -------------------- #
    log.info("Creating logs and temp directories...")
    subprocess.run(["mkdir", "logs"], shell=is_windows)
    subprocess.run(["mkdir", "temp"], shell=is_windows)
    # ------------------------------------- - ------------------------------------ #
    

    python_ver_keyword = ARGS.intepreter_keyword
    python_version = subprocess.check_output([python_ver_keyword, "--version"], shell=is_windows)
    log.info(f"PYTHON VERSION BEING USED IS: {python_version}")


    # ---------------------------- Creating python env --------------------------- #
    if not os.path.exists(os.path.join(prjDir, "venv")):
        log.info(f"Creating Python venv...")
        subprocess.run([python_ver_keyword, "-m", "venv", "venv"])
    else:
        log.info(f"Python venv already exist! Skipping this part...")
        
    # ------------------------------------- - ------------------------------------ #
    
    
    # ------------------------- Creating config.yaml file ------------------------ #
    try:
        with open("config.yaml") as config_file:
            log.info("config.yaml file already exits. Skipping this part...")
    except IOError:
        log.info(f"No config.yaml file found! Creating one with default template...")
        with open("config.yaml", "w") as config_file:
            config_file.writelines(
                [
                    "# ---------------------------- TWO-CAPTCHA CONFIG ---------------------------- #\n",
                    "two_captcha_config:    # This program uses the 2captcha API to solve captchas on the website. See README.md for more info.\n",
                    "  api_key: !KEY_HERE! \n",
                    "  enabled: True\n",
                    "  debug_mode: True\n",
                    "# ------------------------------------- - ------------------------------------ #\n\n\n",


                    "# ------------------------------- EMAIL CONFIG ------------------------------- #\n",
                    "mail_config:\n",
                    "  email_notification_enabled: False        # Whether or not to push notification to your email.\n\n",

                    "  # If you are you using a different email provider, search for its smtp_server and port.\n",
                    "  smtp_server: smtp.gmail.com\n",
                    "  smtp_port: 587\n\n",

                    "  smtp_user: !EMAIL! @gmail.com            # Your email address here.\n",
                    "  smtp_pw: !PASSWORD_HERE!                 # Your password here. See README.md if you use 2FA for your email.\n\n",
    
                    "  recipient_address: !EMAIL! @gmail.com    # Who to send the notification to.\n",
                    "# ------------------------------------- - ------------------------------------ #\n\n\n",


                    "# ---------------------------- TELEGRAM BOT CONFIG --------------------------- #\n",
                    "telegram_config:   # See README.md for more info on how to set up a telegram bot for this.\n",
                    "  telegram_notification_enabled: True  # Whether or not to push notification to telegram bot.\n\n",

                    "  telegram_bot_token: !TOKEN_HERE!\n",
                    "  telegram_chat_id: !CHAT_ID_HERE!\n",
                    "# ------------------------------------- - ------------------------------------ #\n\n\n",


                    "# ------------------------------ PROGRAM CONFIG ------------------------------ #\n",
                    "cdc_login_credentials:\n",
                    "  username: !USER_NAME_HERE!   # CDC Username\n",
                    "  password: !PASSWORD_HERE!    # CDC Password\n\n",

                    "program_config:\n",
                    "  auto_reserve: True           # Whether to (try and) reserve earliest available slots. User must still log in to confirm these sessions.\n",
                    "  reserve_for_same_day: True   # Whether to consider slots on the same days as currently booked slots.\n",
                    "  refresh_rate: 1800           # How long to wait between checks on the wesite (in seconds).\n\n",

                    "  slots_per_type:      # How many slots to try and reserve per type\n",
                    "    practical : 6\n",
                    "    ett       : 1\n",
                    "    btt       : 1\n",
                    "    rtt       : 1\n",
                    "    pt        : 1\n",
                    "    rr        : 1\n\n",

                    "  monitored_types:     # Toggle these values for which types you want the bot to be checking for.\n",
                    "    practical : False\n",
                    "    ett       : True\n",
                    "    btt       : True\n",
                    "    rtt       : False\n",
                    "    pt        : False\n",
                    "    rr        : False\n\n",

                    "browser_config:\n",
                    "  type: firefox        # Uses firefox driver as default (other option is chrome if you have its binaries.\n",
                    "  headless_mode: True  # If true, selenium_driver will run without the visible UI.\n",
                    "# ------------------------------------- - ------------------------------------ #\n\n\n",

                    "# -------------------------------- LOG CONFIG -------------------------------- #\n",
                    "log_config:\n",
                    "  log_level: 1                      # 1 - DEBUG, 2 - INFO, 3 - WARN, 4- ERROR: If log_level == 3, then only WARN, ERROR will be shown in logs\n",
                    "  print_log_to_output: True         # Whether to prints log to console\n",
                    "  write_log_to_file: True           # Whether to write log to file (found in $(workspace)/logs/)\n",
                    "  clear_logs_init: False            # Whether to delete old log files before at the start of every execution\n",
                    "  appends_stack_call_to_log : False # Whether to display stack_info in log\n",
                ]
            )
    # ------------------------------------- - ------------------------------------ #


    # ----------------- Modify shebang in main.py to relativepath ---------------- #
    log.info(f"Setting shebang of src/main.py to venv intepreter...")    
    data = None
    path_to_main_py = os.path.join("src", "main.py")
    with open(path_to_main_py, 'r') as main_py:
        data = main_py.readlines()
        
    
    data[0] = f"#!{os.path.join(prjDir, 'venv', 'bin', python_ver_keyword)}\n"
    with open(path_to_main_py, 'w') as main_py:
        main_py.writelines(data)
    # ------------------------------------- - ------------------------------------ #


    if is_linux:

        # ---------------------- Giving program executable perm ---------------------- #
        log.info(f"Setting drivers to be an executable...")
        for platform_dir in os.listdir("drivers"):
            for driver_file in os.listdir(os.path.join("drivers", platform_dir)):
                file_path = os.path.join("drivers", platform_dir, driver_file)
                subprocess.run(["sudo", "chmod", "u+x", file_path])
        
        log.info(f"Setting src/main.py to be an executable...")
        subprocess.run(["sudo", "chmod", "u+x", "src/main.py"])
        # ------------------------------------- - ------------------------------------ #

    
        # -------------------------- Installing dependencies ------------------------- #
        log.info(f"Installing dependencies from requirements.txt into venv now...")
        subprocess.run([f"venv/bin/{python_ver_keyword}", "-m", "pip", "install", "-r", "requirements.txt"])
        # ------------------------------------- - ------------------------------------ #
        
    elif is_windows:
        
        # -------------------------- Installing dependencies ------------------------- #
        log.info(f"Installing dependencies from requirements.txt into venv now...")
        subprocess.run([os.path.join("venv", "Scripts", f"{python_ver_keyword}.exe"), "-m", "pip", "install", "-r", r".\requirements.txt"], shell=True)
        # ------------------------------------- - ------------------------------------ #
        
    elif "darwin" in sys.sys.platform:
        log.error("setup.py currently does not support installing of dependencies. Please do this manually.")
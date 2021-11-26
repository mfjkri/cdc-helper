<h2>CDC-HELPER</h2>

<h2>Features:</h2>
<ul>
  <li>Fetch available dates for E-Trial, BTT, RTT, Practical Lesson, PT</li>
  <li>Compare with booked dates for each</li>
  <li>Notify user (via Telegram & E-mail) if earlier date is found</li>
  <li>Attempt and reserve the slot if possible</li>
</ul> 

<h2>Prerequisites</h2>

<h3>Python 3</h3>

<p>If you do not already have Python3 install it from the official website [here](https://www.python.org/downloads).</p>
  

<h3>Setting Up</h3>


<hr>
<h4>A) Using <a href="https://github.com/mfjkri/cdc-helper/blob/master/setup.py" title="setup.py">setup.py</a>:</h4>
<p></p> 


<h5><b>For Windows & Linux:</b></h5>

<p>Ensure that the python version you're using is python 3</p>

```
python setup.py --intepreter_keyword "python"
```

<p>If python keyword in your system points Python2, then use the keyword that points to Python3 and replace the intepreter_keyword with it accordingly.</p>

<h5><b>Others:</b></h5>

<p>This project isn't guaranteed to work on other operating systems. You can try building the project by following the manual steps.</p>


<hr>
<h4>B) Manually</h4>

<ol>
  <li>Create a virtual environment, <a href="https://docs.python.org/3/library/venv.html" title="Python venv">venv</a>, for your project</li>
  <li>Install dependencies: ```path/to/venv_python -m pip install -r "requirements.txt"```</li>
  <li>Create <a href="#config-yaml">config.yaml</a> file</li>
</ol> 


<hr>
<h4 id="config-yaml">config.yaml</h4>

```
# ---------------------------- TWO-CAPTCHA CONFIG ---------------------------- #
two_captcha_config:    # This program uses the 2captcha API to solve captchas on the website. See README.md for more info.
  api_key: !KEY_HERE! 
  enabled: True
  debug_mode: True
# ------------------------------------- - ------------------------------------ #


# ------------------------------- EMAIL CONFIG ------------------------------- #
mail_config:
  email_notification_enabled: False        # Whether or not to push notification to your email.

  # If you are you using a different email provider, search for its smtp_server and port.
  smtp_server: smtp.gmail.com
  smtp_port: 587

  smtp_user: !EMAIL! @gmail.com            # Your email address here.
  smtp_pw: !PASSWORD_HERE!                 # Your password here. See README.md if you use 2FA for your email.

  recipient_address: !EMAIL! @gmail.com    # Who to send the notification to.
# ------------------------------------- - ------------------------------------ #


# ---------------------------- TELEGRAM BOT CONFIG --------------------------- #
telegram_config:   # See README.md for more info on how to set up a telegram bot for this.
  telegram_notification_enabled: True  # Whether or not to push notification to telegram bot.

  telegram_bot_token: !TOKEN_HERE!
  telegram_chat_id: !CHAT_ID_HERE!
# ------------------------------------- - ------------------------------------ #


# ------------------------------ PROGRAM CONFIG ------------------------------ #
cdc_login_credentials:
  username: !USER_NAME_HERE!   # CDC Username
  password: !PASSWORD_HERE!    # CDC Password

program_config:
  auto_reserve: True           # Whether to (try and) reserve earliest available slots. User must still log in to confirm these sessions.
  reserve_for_same_day: True   # Whether to consider slots on the same days as currently booked slots.
  refresh_rate: 1800           # How long to wait between checks on the wesite (in seconds).

  slots_per_type:      # How many slots to try and reserve per type
    practical : 6
    ett       : 1
    btt       : 1
    rtt       : 1
    pt        : 1
    rr        : 1

  monitored_types:     # Toggle these values for which types you want the bot to be checking for.
    practical : False
    ett       : True
    btt       : True
    rtt       : False
    pt        : False
    rr        : False

browser_config:
  type: firefox        # Uses firefox driver as default (other option is chrome if you have its binaries.
  headless_mode: True  # If true, selenium_driver will run without the visible UI.
# ------------------------------------- - ------------------------------------ #


# -------------------------------- LOG CONFIG -------------------------------- #
log_config:
  log_level: 1                      # 1 - DEBUG, 2 - INFO, 3 - WARN, 4- ERROR: If log_level == 3, then only WARN, ERROR will be shown in logs
  print_log_to_output: True         # Whether to prints log to console
  write_log_to_file: True           # Whether to write log to file (found in $(workspace)/logs/)
  clear_logs_init: False            # Whether to delete old log files before at the start of every execution
  appends_stack_call_to_log : False # Whether to display stack_info in log
```


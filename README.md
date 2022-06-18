<h1>CDC-HELPER</h1>

&nbsp;

---

## ⚠️ THIS PROJECT IS NO LONGER BEING MAINTAINED. ⚠️

### I am retiring this project and archiving it.

### The major reason for it is that I have gotten my license and as such no longer have access to the CDC booking platform. I am also no longer interested/motivated to, as this project was only to aid me in getting my license earlier, so please do not contact me with hopes that I will update it.

### Feel free to clone this project for your own use.

---

&nbsp;

<p>Inspired by <a href="https://github.com/SilverJan/cdc-camper">cdc-camper</a> by <a href="https://github.com/SilverJan">SilverJan</a>.<p>

<h1>Features:</h1>
<ul>
  <li>Fetch available dates for BTT, RTT, FTT, Practical Lesson, PT and more</li>
  <li>Compare with booked dates for each</li>
  <li>Notify user (via Telegram & E-mail) if earlier date is found</li>
  <li>Attempt and reserve the slot if possible</li>
</ul>

<h1>Prerequisites</h1>

<h2>Python 3</h2>

<p>If you do not already have Python3 install it from the official website [here](https://www.python.org/downloads).</p>

<h2>Setting Up</h2>

<h3>1) TwoCaptcha</h3>
<p></p>
<p>This project uses a third party API that is unfortunately a <b>paid</b> service. </p>  
<p>As of writing this, the rates of using this API are <i>relatively cheap</i> (SGD$5 can last you for about a month of the program runtime).</p>
<p>To continue using this project, head over to <a href="https://2captcha.com/" title = "2captcha">2captcha.com</a><p>
<ul>
  <li>Create an account.</li>
  <li>Top up your account with sufficient credits.</li>
  <li>Copy your API Token and paste it into <a href="#config-yaml" title = "config">config.yaml</a>.</li>
</ul>
<p>If you do not wish to use this service and have some python knowledge, you can attempt to swap out the service for a machine learning model for solving captchas (reCaptchaV2 + normal Captcha). </p>

<hr>
<h3>2) Telegram & Email Notifications</h3>

<h4><b>Email:</b></h4>

<p>If you wish to enable Email  notifications:</p>
<ol>
  <li>Set <i>email_notification_enabled<sup>1</sup></i> to <b>True</b>.</li>
  <li>Set <i>smtp_server<sup>1</sup></i> and <i>smtp_port<sup>1</sup></i> accordingly (Default values are for gmail).</li>
  <li>Set <i>smtp_user<sup>1</sup></i> to your email address.</li>
  <li>Set <i>smtp_pw<sup>1</sup></i> to your email account password (you may have to create an App password if your account has 2FA enabled; for <a href = "https://www.nucleustechnologies.com/supportcenter/kb/how-to-create-an-app-password-for-gmail">gmail</a>).</li>
  <li>Set <i>recipient_address<sup>1</sup></i> to the email address to send notifications to (You should set it to be the same as <i>smtp_user<sup>1</sup></i>).</li>
   
</ol>

<h4><b>Telegram:</b></h4>

<p>If you wish to enable Telegram notifications:</p>
<ol>
  <li>Set <i>telegram_notification_enabled<sup>2</sup></i> to <b>True</b>.</li>
  <li>Follow this <a href = "https://www.teleme.io/articles/create_your_own_telegram_bot?hl=en" title = "Creating telegram bot">guide</a> to create your telegram bot.</li>
  <li>Copy the API Token generated and paste it into <i>telegram_bot_token<sup>2</sup></i>.</li>
  <li>Send your bot \start on Telegram.</li>
  <li>Visit this URL: https://api.telegram.org/botBOT_TOKEN/getUpdates, replacing <i>BOT_TOKEN</i> with your API Token from (3).</li>
  <li>Send a test message to your bot on Telegram.</li>
  <li>There should be an new entry in the JSON on the URL you opened from (5).</li>
  <li>Copy the chat ID from the JSON (result::[X]::message::chat::id) and paste it into <i>telegram_chat_id<sup>2</sup></i>.</li>
</ol>

<p><sup>1</sup> - <i>mail_config</i> in <a href="#config-yaml">config.yaml</a></p>
<p><sup>2</sup> - <i>telegram_config</i> in <a href="#config-yaml">config.yaml</a></p>

<hr>
<h3>3A) Using <a href="https://github.com/mfjkri/cdc-helper/blob/master/setup.py" title="setup.py">setup.py</a>:</h3>
<p></p>

<h4><b>For Windows & Linux:</b></h4>

<p>Ensure that the python version you're using is python 3</p>

```
$ python setup.py --intepreter_keyword "python"
```

<p>If python keyword in your system points Python2, then use the keyword that points to Python3 and replace the intepreter_keyword with it accordingly.</p>

<h4><b>Others:</b></h4>

<p>This project isn't guaranteed to work on other operating systems. You can try building the project by following the <a href="#manual-steps">manual steps (3B)</a>.</p>

<hr>
<h3 id="manual-steps">3B) Manually</h3>

<ol>
  <li>Create a virtual environment, <a href="https://docs.python.org/3/library/venv.html" title="Python venv">venv</a>, for your project.</li>
  <li>Install dependencies:</li>
  
  ```$ path/to/project/venv/.../python -m pip install -r "requirements.txt"```

  <li>Create <a href="#config-yaml">config.yaml</a> file.</li>
</ol>

<h1>Running</h1>

```
$ path/to/project/venv/.../python src/main.py
```

<p>OR, if you have <a href="https://github.com/mfjkri/cdc-helper/blob/master/src/main.py">main.py</a> set to be an execeutable with a valid shebang:<p>

```
$ cd path/to/project
$ src/main.py
```

<h1>Appendix</h1>

<h3 id="config-yaml">config.yaml</h3>

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
  book_from_other_teams: True  # Whether to book from other OneTeams (User must be a OneTeam member)
  refresh_rate: 1800           # How long to wait between checks on the wesite (in seconds).

  slots_per_type:      # How many slots to try and reserve per type
    practical : 6
    btt       : 1
    rtt       : 1
    ftt       : 1
    pt        : 1

  monitored_types:     # Toggle these values for which types you want the bot to be checking for.
    practical : False
    btt       : False
    rtt       : False
    ftt       : False
    pt        : False

browser_config:
  type: firefox        # Uses firefox driver as default (other option is chrome if you have its binaries).
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

import os, shutil, sys, logging
from datetime import datetime 


formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
log_config = {
    "CLEAR_OUTPUT_ON_RESET" : True,
    "SHOW_STACK" : True,
    "OUTPUT_LEVEL" : 1,
}

class Log:

    def __init__(self, directory, name="cdc-helper", log_config=log_config):
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)

        self.logger = log  
        self.name = name
        self.directory = directory 
        self.log_config = log_config  
    
        if log_config["CLEAR_OUTPUT_ON_RESET"]:
            self.clean()
        
        terminal_output = logging.StreamHandler(sys.stdout)
        terminal_output.setFormatter(formatter)
        log.addHandler(terminal_output)
        
        file_output = logging.FileHandler('{dir}/tracker_{date}.log'.format(dir=directory, date=datetime.today().strftime("%Y-%m-%d_%H-%M")))
        file_output.setFormatter(formatter)
        log.addHandler(file_output)
        
    def clean(self, exceptFileName=""):
        for filename in os.listdir(self.directory):
            if filename != exceptFileName:
                file_path = os.path.join(self.directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.error('Failed to delete %s. Reason: %s' % (file_path, e))   
        
    def info(self, msg):
        if log_config["SHOW_STACK"]:
            caller_info = self.logger.findCaller()
            
            self.logger.info("============================================")
            self.logger.info(msg)
            self.logger.info(caller_info)
        else:
            self.logger.info(msg)
            
    def error(self, msg):
        self.logger.error(msg)
        
    def debug(self, msg):
        self.logger.debug(msg)
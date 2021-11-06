import os, shutil, sys, logging
from datetime import datetime 

from utils.common import common

FORMATTER = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
DEFAULT_CONFIG = {
    "PRINT_TO_OUTPUT" : True,
    "LOG_TO_FILE" : True,
    
    "CLEAR_OUTPUT_ON_RESET" : False,
    
    "SHOW_STACK" : True,
}

class Log:

    def __init__(self, directory, name="cdc-helper", config=DEFAULT_CONFIG):
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)

        self.logger = log  
        self.name = name
        self.directory = directory 
        self.config = self._init_config(config)

        if self.config["CLEAR_OUTPUT_ON_RESET"]:
            self.clean()
        
        if self.config["PRINT_TO_OUTPUT"]:
            terminal_output = logging.StreamHandler(sys.stdout)
            terminal_output.setFormatter(FORMATTER)
            log.addHandler(terminal_output)
        
        if self.config["LOG_TO_FILE"]:        
            file_output = logging.FileHandler('{dir}/tracker_{date}.log'.format(dir=directory, date=datetime.today().strftime("%Y-%m-%d_%H-%M")))
            file_output.setFormatter(FORMATTER)
            log.addHandler(file_output)
        
    def _init_config(self, config):
        for configValue, configType in enumerate(DEFAULT_CONFIG):
            if not common.checkKeyExistence(config, configType):
                config[configType] = configValue
        return config
                    
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
        if self.config["SHOW_STACK"]:
            caller_info = self.logger.findCaller()
            
            self.logger.info("============================================")
            self.logger.info(msg)
            self.logger.info(caller_info)
        else:
            self.logger.info(msg)
            
    def error(self, msg):
        self.logger.error(msg)
        
    def warning(self, msg):
        self.logger.warning(msg)
        
    def debug(self, msg):
        self.logger.debug(msg)
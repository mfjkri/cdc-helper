import os, shutil, sys, logging
from datetime import datetime

from utils.common import utils
from utils.common import selenium_common

FORMATTER = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
DEFAULT_CONFIG = {
    "LOG_LEVEL" : 1, # 1 - DEBUG, 2 - INFO, 3 - WARN, 4- ERROR
    
    "PRINT_TO_OUTPUT" : True,
    "LOG_TO_FILE" : True,
    
    "CLEAR_OUTPUT_ON_RESET" : False,
    
    "SHOW_STACK" : True,
}

class Log:

    def __init__(self, directory:str, name:str="cdc-helper", config:dict=DEFAULT_CONFIG):
        log = logging.getLogger(name)

        self.logger = log  
        self.name = name
        self.directory = directory 
        self.config = utils.init_config_with_default(config, DEFAULT_CONFIG)

        if self.config["CLEAR_OUTPUT_ON_RESET"]:
            utils.clear_directory(directory=self.directory, log=self.logger)
        
        if self.config["PRINT_TO_OUTPUT"]:
            terminal_output = logging.StreamHandler(sys.stdout)
            terminal_output.setFormatter(FORMATTER)
            log.addHandler(terminal_output)
        
        if self.config["LOG_TO_FILE"]:        
            file_output = logging.FileHandler('{dir}/tracker_{date}.log'.format(dir=directory, date=datetime.today().strftime("%Y-%m-%d_%H-%M")))
            file_output.setFormatter(FORMATTER)
            log.addHandler(file_output)

        log.setLevel(int(self.config["LOG_LEVEL"]) * 10)
        
    def info(self, *output):
        msg = utils.concat_tuple(output)
                
        if self.config["SHOW_STACK"]:
            caller_info = self.logger.findCaller()
            
            self.logger.info("============================================")
            self.logger.info(msg)
            self.logger.info(caller_info)
        else:
            self.logger.info(msg)
            
    def debug(self, *output):
        self.logger.debug(utils.concat_tuple(output))
            
    def error(self, *output):
        self.logger.error(utils.concat_tuple(output))
        
    def warning(self, *output):
        self.logger.warning(utils.concat_tuple(output))
        
        
    
    
    def info_if(self, condition:bool, *output):
        if condition:
            self.info(*output)
            
    def debug_if(self, condition:bool, *output):
        if condition:
            self.debug(*output)

    def error_if(self, condition:bool, *output):
        if condition:
            self.error(*output)
        
    def warning_if(self, condition:bool, *output):
        if condition:
            self.warning(*output)
    
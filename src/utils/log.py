import sys, logging
from datetime import datetime 


formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

class Log:

    def __init__(self, dir, name):
        log = logging.getLogger('cdc_helper')
        log.setLevel(logging.INFO)
        
        terminal_output = logging.StreamHandler(sys.stdout)
        terminal_output.setFormatter(formatter)
        log.addHandler(terminal_output)
        
        file_output = logging.FileHandler('{dir}/tracker_{date}.log'.format(dir=dir, date=datetime.today().strftime("%Y-%m-%d_%H-%M")))
        file_output.setFormatter(formatter)
        log.addHandler(file_output)
        
        self.logger = log    
        
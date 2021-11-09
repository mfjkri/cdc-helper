import shutil, os, yaml

class selenium_common:
    import selenium
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    def wait_for_elem(driver: selenium.webdriver, locator_type: str, locator: str, timeout: int=5):
        return selenium_common.WebDriverWait(driver, timeout).until(selenium_common.EC.presence_of_element_located((locator_type, locator)))


    def is_elem_present(driver: selenium.webdriver, locator_type: str, locator: str, timeout: int=2):
        try:
            return selenium_common.wait_for_elem(driver, locator_type, locator, timeout)
        except selenium_common.TimeoutException:
            return False


class utils:
    
    
    class DEFAULT_LOG:
        def info(*args):
            print("[INFO]", utils.concat_tuple(args))
        def debug(*args):
            print("[DEBUG]", utils.concat_tuple(args))
        def error(*args):
            print("[ERROR]", utils.concat_tuple(args))
        def warn(*args):
            print("[WARN]", utils.concat_tuple(args))

    def load_config_from_yaml_file(file_path:str, log):
        if not os.path.isfile(file_path):
            raise Exception(f"No file found at {file_path}")
        with open(file_path, 'r') as stream:
            config = {}
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exception:
                log.error(exception)
            return config
    
    def init_config_with_default(config:dict, default_config:dict):
        for configValue, configType in enumerate(default_config):
            if not utils.check_key_existence_in_dict(config, configType):
                config[configType] = configValue
        return config
    
    def check_key_value_pair_exist_in_dict(dic, key, value):
        try:
            return dic[key] == value
        except KeyError:
            return False

    def check_key_existence_in_dict(dic, key):
        try:
            _ = dic[key]
            return True
        except KeyError:
            return False
        
    def concat_tuple(ouput_tuple):
        result = ""
        for m in ouput_tuple:
            result += str(m) + ' '
        
        return result
    
    def clear_directory(directory:str, log=DEFAULT_LOG):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                log.error('Failed to delete %s. Reason: %s' % (file_path, e))   

    def remove_files(files: list, log=DEFAULT_LOG):
        for file in files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    log.error("Failed to delete %s. Reason %s" % (str(file), e))
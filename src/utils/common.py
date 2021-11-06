class common:
    def checkKeyValuePairExistence(dic, key, value):
        try:
            return dic[key] == value
        except KeyError:
            return False

    def checkKeyExistence(dic, key):
        try:
            _ = dic[key]
            return True
        except KeyError:
            return False
class APIResult(dict):
    def __init__(self, data):
        print('data type:',type(data))
        self['status'] = 1
        if isinstance(data, dict):
            print("data is dict")
            self['data'] = data
        elif isinstance(data, list):
            print("data is list")
            self['data'] = data
        else:
            print("data is not dict or list")
            self['data'] = list(data)
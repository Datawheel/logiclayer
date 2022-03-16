class MalformedParameterException(Exception):
    def __init__(self, param_name: str):
        super(self)
        self.param_name = param_name

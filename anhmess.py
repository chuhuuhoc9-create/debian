class NanhMessenger:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return self
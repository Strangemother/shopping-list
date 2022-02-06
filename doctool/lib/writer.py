

class WriterUnit(object):
    """Write finalised config units to somewhere.
    """

    def __init__(self, config=None):
        if config:
            self.setup(config)

    def setup(self, config):
        self.config = config

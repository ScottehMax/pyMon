import time


class TriggerRegistry(type):
    """Trigger registry. This allows one to easily obtain a list of loaded triggers."""
    triggers = []

    def __init__(cls, name, bases, attrs):
        if name != 'Trigger':
            TriggerRegistry.triggers.append(cls)


class Trigger(object):
    """Base trigger class."""
    __metaclass__ = TriggerRegistry

    def __init__(self, ch):
        self.lastused = int(time.time())
        self.ch = ch  # ChatHandler instance, passed into the trigger

    def match(self, info):
        """Checks whether the information in the 'info' dict will cause the trigger to fire."""
        raise NotImplementedError

    def response(self, info):
        """If the trigger fires, this will obtain the response to send back."""
        raise NotImplementedError
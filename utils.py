import re

def condense(string):
    return (re.sub(r'[^A-Za-z0-9]', '', string)).lower()

class switch(object):
    # Taken from the following URL to allow for readable switch-like syntax in python:
    # http://code.activestate.com/recipes/410692-readable-switch-construction-without-lambdas-or-di/history/8/
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

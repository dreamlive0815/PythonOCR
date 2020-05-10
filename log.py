
import sys

class Log():

    @classmethod
    def i(cls, msg):
        print(msg)

    @classmethod
    def e(cls, msg):
        print('!!!ERROR!!! ' + msg, file = sys.stderr)


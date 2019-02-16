from datetime import datetime
from os.path import isfile
import sys

from .helpers import cmk_dir
from .paths import ERROR_LOGS_DIR, ERROR_LOGS_F_PATH


class Logger:
    def __init__(self, log_to_stdout=False):
        self.log_to_stdout = log_to_stdout

    def log_error(self, error_msg):
        if self.log_to_stdout:
            print("ERROR: %s" % error_msg)
        else:
            cmk_dir(ERROR_LOGS_DIR)
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not isfile(ERROR_LOGS_F_PATH):
                open(ERROR_LOGS_F_PATH, 'w').close()
            with open(ERROR_LOGS_F_PATH, 'a') as logs_file:
                logs_file.write('%s: %s\n' % (time, error_msg))
        sys.exit(1)

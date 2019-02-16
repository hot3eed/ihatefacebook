from pathlib import Path

SERVICE_ID = 'com.hot3eed.ihatefacebook'
HOME = str(Path.home())
CONFIG_DIR = '%s/Library/Application Support/%s' % (HOME, SERVICE_ID)
CONFIG_F_PATH = '%s/config.json' % CONFIG_DIR
PAGES_F_PATH = '%s/pages.json' % CONFIG_DIR
CACHE_DIR = '%s/Library/Caches/%s' % (HOME, SERVICE_ID)
ERROR_LOGS_DIR = '%s/Library/Logs/%s' % (HOME, SERVICE_ID)
ERROR_LOGS_F_PATH = '%s/errors.log' % ERROR_LOGS_DIR

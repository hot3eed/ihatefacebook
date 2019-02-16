import platform
import os
import subprocess
from setuptools import setup, find_packages

from ihatefacebook import paths
from ihatefacebook import helpers

if platform.system() != 'Darwin':
    print("ERROR: Only macOS is currently supported.")
    exit(1)


HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ihatefacebook",
    version=0.5,
    description="Get notified by email whenever a Facebook page adds a new event.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hot3eed/ihatefacebook',
    license='Apache License 2.0',
    author_email="hot3eed@gmail.com",
    python_requires='>=3.3',
    install_requires=['selenium', 'click', 'keyring'],
    packages=find_packages(),
    entry_points={
        "console_scripts": ['ihatefacebook=ihatefacebook.cli:main']
        }
)


helpers.cmk_dir(paths.ERROR_LOGS_DIR)

executable_path = subprocess.check_output(["which", "ihatefacebook"]).decode('utf-8').rstrip()

launchd_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{0}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{1}</string>
        <string>run</string>
    </array>
    <key>StandardErrorPath</key>
    <string>{2}</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
""".format(paths.SERVICE_ID, executable_path, paths.ERROR_LOGS_F_PATH)

launchd_plist_path = "%s/Library/LaunchAgents/%s.plist" % (paths.HOME, paths.SERVICE_ID)
launchd_plist_f = open(launchd_plist_path, 'w+')
launchd_plist_f.write(launchd_plist)
launchd_plist_f.close()

os.system("launchctl load %s" % launchd_plist_path)

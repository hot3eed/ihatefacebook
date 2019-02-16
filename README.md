# ihatefacebook
ihatefacebok is a Python script that allows you to get notified by email whenever a Facebook page adds a new event, 
without having to interact with Facebook yourself. The script runs by default every time your machine starts up 
(after login), but you can also set it up with the `run` command as a `cron` job. Currently supports macOS only.


## Installation
`$ pip install ihatefacebook`


## Usage
```
$ ihatefacebook COMMAND [OPTION] [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  config  Add or list email and SMTP server configurations
  page    Add, remove or list pages to be scraped for events
  run     Run scraping utility with currently set configurations and pages
```
#### Subcommands
```
$ ihatefacebook config OPTION [ARGS]

  Add or list email and SMTP server configurations

Options:
  -a, --add key=value   Add user.email, smtp.host, smtp.port configurations, with
                            the format key=val
  -p, --password        Set password for the user.email added using the -a option
  -l, --list            List currently set configurations
  --help                Show this message and exit.
```
```
$ ihatefacebook page OPTION [ARGS]

  Add, remove or list pages to be scraped for events

Options:
  -a, --add PAGE_ID     Add a page to the list of pages to be scraped, using its
                            Facebook page ID
  -r, --remove PAGE_ID  Remove a page using its Facebook page ID
  -l, --list            List all pages from the list of pages to be scraped
  --help                Show this message and exit.
```


## Requirements
[pip](https://pypi.org/project/pip/) installs needed dependencies but you'll need to have these on your machine as well:
* Google Chrome
* [ChromeDriver](http://chromedriver.chromium.org/), make sure it's the version corresponding to that of the browser, 
and have it located in `/usr/local/bin/`.


## Notes
* The scraping code could break anytime Facebook change their DOM, if you notice this before I update the code, 
please let me know.
* If you're using Gmail as your SMTP server, you'll need to turn on [less secure app access](https://support.google.com/a/answer/6260879?hl=en).
* The script uses [launchd](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html) 
on macOS for launching every time your machine starts up, `ihatefacebook` calls `launchd` and adds needed configuration
at installation. However, you wanna check the status of the script in `launchd` to make sure it'll work properly. This 
can be done using `launchctl list | grep ihatefacebook` (or use [LaunchControl](https://www.soma-zone.com/LaunchControl/)), 
0 means OK. Check `~/Library/Logs/com.hot3eed.ihatefacebook/log.error` 
(or use [Console](https://support.apple.com/en-eg/guide/console/welcome/mac)) for debugging. All this hard manual labor
 could be automated in a future update.


## TODO
* Add Linux support.
* Add Windows support.


## License
[Apache License 2.0](https://github.com/hot3eed/ihatefacebook/blob/master/LICENSE)

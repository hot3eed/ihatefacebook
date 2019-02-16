from os.path import isfile, getsize
import json
from json.decoder import JSONDecodeError
import os
import subprocess

import click
import keyring
import getpass

from . import helpers as helpers
from .facebook import page as facebook_page
from . import messages as messages
from .paths import *
from . import scraper as scraper


@click.group()
def main():
    pass


@main.command()
@click.option('-a', '--add', 'a_page_id', help='Add a page to the list of pages to be scraped, '
                                               'using its Facebook page ID')
@click.option('-r', '--remove', 'r_page_id', help='Remove a page using its Facebook page ID')
@click.option('-l', '--list', is_flag=True, help='List all pages from the list of pages to be scraped')
def page(a_page_id, r_page_id, list):
    """Add, remove or list pages to be scraped for events"""

    if a_page_id:
        add_page(a_page_id)
    elif r_page_id:
        remove_page(r_page_id)
    elif list:
        list_pages()
    else:
        print(click.get_current_context().get_help())


def add_page(page_id):
    """Add a page to the list of pages to be scraped"""

    helpers.cmk_dir(CONFIG_DIR)

    if not isfile(PAGES_F_PATH):
        open(PAGES_F_PATH, 'a').close()

    page_added = False

    with open(PAGES_F_PATH, 'r+') as pages_file:
        pages = list()
        if getsize(PAGES_F_PATH) == 0:
            print("Getting page title from Facebook...")
            page_title = facebook_page.get_page_title(page_id)
            pages.append({'id': page_id, 'title': page_title})
        else:
            try:
                pages = json.load(pages_file)
                if not any(p['id'] == page_id for p in pages):
                    print("Getting page title from Facebook...")
                    page_title = facebook_page.get_page_title(page_id)
                    pages.append({'id': page_id, 'title': page_title})
                    page_added = True
                    print("Page added successfully.")
                else:
                    print("Page already added.")
                    return
            except JSONDecodeError:
                print(messages.CORRUPTED_PAGES_F_ERR)
        try:
            pages_file.seek(0)
            json.dump(pages, pages_file)
        except Exception as e:
            print("ERROR: %s" % e)

    if page_added:
        print("Now scraping...")
        scraper.main(log_to_stdout=True)


def remove_page(page_id):
    """Remove a page from the list of pages to be scraped"""

    if isfile(PAGES_F_PATH) and getsize(PAGES_F_PATH) != 0:
        with open(PAGES_F_PATH, 'r+') as pages_file:
            try:
                pages = json.load(pages_file)
                for page in pages:
                    if page['id'] == page_id:
                        pages.remove(page)
                        page_cache_f_path = "%s/%s.html" % (CACHE_DIR, page_id)
                        try:
                            os.remove(page_cache_f_path)
                        except:
                            pass
                try:
                    pages_file.seek(0)
                    pages_file.truncate(0)
                    json.dump(pages, pages_file)
                except Exception as ex:
                    print("ERROR: %s" % ex)
            except JSONDecodeError:
                print(messages.CORRUPTED_PAGES_F_ERR)
            except Exception as ex:
                print("ERROR: %s" % ex)
    else:
        print(messages.NO_PAGES)


def list_pages():
    """Show list of pages to be scraped"""

    try:
        pages = helpers.read_json(PAGES_F_PATH)
        if type(pages) is list:
            for page in pages:
                print('%s, id: %s' % (page['title'], page['id']))
        elif type(pages) is bool:
            print(messages.NO_PAGES)
    except JSONDecodeError:
        print(messages.CORRUPTED_PAGES_F_ERR)
    except Exception as ex:
        print('ERROR: %s' % ex)


@main.command()
@click.option('-a', '--add', 'keyval', help='Add user.email, smtp.host, smtp.port configurations, '
                                            'using the format key=val')
@click.option('-p', '--password', is_flag=True, help='Set password for the user.email added with the -a option')
@click.option('-l', '--list', is_flag=True, help='List currently set configurations')
def config(keyval, password, list):
    """Add or list email and SMTP server configurations"""

    if keyval:
        add_config(keyval)
    elif password:
        add_pass_config()
    elif list:
        list_configs()
    else:
        print(click.get_current_context().get_help())


def add_config(keyval):
    keyval = keyval.split('=')
    if len(keyval) != 2:
        print("ERROR: Invalid parameter format. Correct format: key=value")
        return
    key = keyval[0]
    value = keyval[1]

    legal_keys = ["smtp.host", "smtp.port", "user.email"]
    if key not in legal_keys:
        print("ERROR: Illegal setting: %s" % key)
        return

    helpers.cmk_dir(CONFIG_DIR)

    if not isfile(CONFIG_F_PATH):
        open(CONFIG_F_PATH, 'a').close()

    with open(CONFIG_F_PATH, 'r+') as config_file:
        configs = dict()
        if getsize(CONFIG_F_PATH) != 0:
            try:
                configs = json.load(config_file)
            except JSONDecodeError:
                print(messages.CORRUPTED_CONFIG_F_ERR)
                print("The file will be overwritten.")
        configs[key] = value
        try:
            config_file.seek(0)
            json.dump(configs, config_file)
        except Exception as e:
            print("ERROR: %s." % e)


def add_pass_config():
    if not isfile(CONFIG_F_PATH) or getsize(CONFIG_F_PATH) == 0:
        print(messages.NO_CONIGS_ERR)
        return
    with open(CONFIG_F_PATH) as config_file:
        try:
            configs = json.load(config_file)
            email = configs['user.email']
            if email is None:
                print(messages.NO_EMAIL_ERR)
                return
            try:
                keyring.set_password(SERVICE_ID, email, getpass.getpass())
            except Exception as err:
                print("ERROR: %s" % err)
        except JSONDecodeError:
            print(messages.CORRUPTED_CONFIG_F_ERR)


def list_configs():
    try:
        configs = helpers.read_json(CONFIG_F_PATH)
        if type(configs) is dict:
            for (key, value) in configs.items():
                print('%s=%s' % (key, value))
        elif type(configs) is bool:
            print(messages.NO_CONFIGS)
    except JSONDecodeError:
        print(messages.CORRUPTED_CONFIG_F_ERR)
    except Exception as ex:
        print('ERROR: %s' % ex)


@main.command()
def run():
    """Run scraping utility with currently set configurations and pages"""

    scraper.main(log_to_stdout=True)

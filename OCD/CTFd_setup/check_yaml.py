"""
Checks the syntax of setup.yml and makes sure files are present
"""
import os
import sys
import time
import calendar
import re

import yaml
import pycountry


class Error:
    """
    Global error checker
    """
    def __init__(self):
        self.error = 0
        self.section = ''

    def print_section(self):
        """
        Print the error
        """
        return 'Under ' + self.section + ': '


class Colors:
    """
    Colored output
    """
    FAIL = '\033[1;31m'
    SUCCES = '\033[1;32m'
    NORMAL = '\033[0m'


def read_setup_yaml(YAMLfile):
    """
    Read setup.yml
    """
    with open(YAMLfile, 'r') as setup:
        if setup.read()[:-1] == 'Configure me':
            print("You need to alter 'setup.yml' before trying to setup CTFd with CTFdeploy")
            quit(1)

    with open(YAMLfile, 'r') as setup:
        try:
            yamldict = yaml.safe_load(setup)
            if isinstance(yamldict, dict):
                return yamldict
            else:
                raise yaml.parser.ParserError
        except yaml.parser.ParserError:
            raise Exception('Please format setup.yml correctly')


def check_error(func):
    """
    Check error wrapper - quit if an error was found
    """
    def error_quit(*args, **kwargs):
        func(*args, **kwargs)
        if error.error == 1:
            print(Colors().NORMAL, end='')
            quit(1)
    return error_quit


def check_yaml_none(*args, **kwargs):
    """
    Make sure yaml doesn't contain None values
    """
    for key in kwargs:
        if isinstance(kwargs[key], dict):
            check_yaml_none(*args, key, **kwargs[key])
        elif isinstance(kwargs[key], list):
            for item in kwargs[key]:
                if item is None:
                    for arg in args:
                        print(arg, end=', ')
                    print(key + ': Has an empty value')
                    error.error = 1
        elif kwargs[key] is None:
            for arg in args:
                print(arg, end=', ')
            print(key + ': Has an emtpy value')
            error.error = 1

def check_config_musts(YAMLfile, key):
    """
    Check if key is in YAMLfile
    """
    if key not in YAMLfile:
        print(error.print_section() + 'missing ' + key)
        error.error = 1


def check_if_int(key, value):
    """
    Check if key is int
    """
    try:
        int(value)
        if int(value) < 0:
            raise
    except:
        print(error.print_section() + key + ', must be a positive number')
        error.error = 1


def check_if_vorv(key, keyvalue, value1, value2):
    """
    Check between keyvalue and two values and print error
    """
    if keyvalue in (value1, value2):
        return
    print(error.print_section() + key + ', must be either ' + str(value1) + ' or ' + str(value2))
    error.error = 1


def check_time(key, timevalue):
    """
    Check if timeformat is correct
    """
    try:
        if not calendar.timegm(time.strptime(timevalue, '%d/%m/%Y %H:%M')) >= 0:
            print(error.print_section() + key + ', must be set to a time later than 01/01/1970 00:00')
            error.error = 1
    except ValueError:
        print(error.print_section() + key + ', is formatted incorrectly')
        error.error = 1


def check_whitelist(key, domains):
    """
    Check if email domains are formatted correctly
    """
    for domain in domains:
        try:
            if not re.match(re.compile(r'^(([a-zA-Z]*\d+\.?)*(\d*[a-zA-Z]+\.?)*)+[^\.]\.[a-zA-Z]+$'), domain):
                print(error.print_section() + key + ', is formatted incorrectly, ' + domain)
                error.error = 1
        except TypeError:
            print(error.print_section() + key + ', please check your whitelist members')
            error.error = 1


def check_email(key, email):
    """
    Check if email is formatted correctly - stolen from http://emailregex.com/
    """
    if not re.match(re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""), email):
        print(error.print_section() + key + ', is formatted incorrectly, ' + email)
        error.error = 1


def check_file(key, folder, keyfile):
    """
    Check if file exists
    """
    if not os.path.isfile(folder + keyfile):
        print(error.print_section() + key + ', file does not exist, ' + keyfile)
        error.error = 1


def check_website(key, website):
    """
    Check if website is valid format - stolen from https://www.regextester.com/93652
    """
    if not re.match(re.compile(r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'), website):
        print(error.print_section() + key + ', is formatted incorrectly, ' + website)
        error.error = 1


def check_countrycode(key, countrycode):
    """
    Check if countrycode is valid
    """
    if pycountry.countries.get(alpha_2=countrycode) is None:
        print(error.print_section() + key + ', is formatted incorrectly, ' + countrycode)
        error.error = 1


def check_challenge(key, requirement, challengesList):
    """
    Check if challenge exists
    """
    if requirement not in challengesList:
        print(error.print_section() + key + ', this challenge is not defined in the setup, ' + requirement)
        error.error = 1


@check_error
def CTFd_config_check(YAMLfile):
    check_config_musts(YAMLfile, 'CTFd')


@check_error
def root_config_check(YAMLfile):
    """
    Check key configs - config, users, pages, and challenges
    """
    configKeys = YAMLfile['CTFd']

    # Check if key values exist
    check_config_musts(configKeys, 'config')
    check_config_musts(configKeys, 'users')
    check_config_musts(configKeys, 'pages')
    check_config_musts(configKeys, 'challenges')


def config_check(YAMLfile):
    """
    Check keys in config
    """
    # Check if key values exist
    @check_error
    def config_key_check():
        check_config_musts(configKeys, 'name')
        check_config_musts(configKeys, 'description')
        check_config_musts(configKeys, 'user_mode')
        check_config_musts(configKeys, 'start')
        check_config_musts(configKeys, 'end')

    # Check if syntax is correct
    @check_error
    def syntax_check():
        check_time('start', configKeys['start'])
        check_time('end', configKeys['end'])

        check_if_vorv('user_mode', configKeys['user_mode'], 'users', 'teams')


        if 'team_size' in configKeys:
            check_if_int('team_size', configKeys['team_size'])

        if 'name_changes' in configKeys:
            check_if_vorv('name_changes', configKeys['name_changes'], 1, 0)

        if 'whitelist' in configKeys:
            check_whitelist('whitelist', configKeys['whitelist'])

        if 'logo' in configKeys:
            check_file('logo', 'OCD/config_files/', configKeys['logo'])

        if 'style' in configKeys:
            check_file('style', 'OCD/config_files/', configKeys['style'])

        if 'theme_header' in configKeys:
            check_file('theme_header', 'OCD/config_files/', configKeys['theme_header'])

        if 'theme_footer' in configKeys:
            check_file('theme_footer', 'OCD/config_files/', configKeys['theme_footer'])


    configKeys = YAMLfile['CTFd']['config']
    config_key_check()
    syntax_check()


def users_check(YAMLfile):
    """
    Check keys in users
    """
    # Check if key values exist
    @check_error
    def users_key_check(user):
        check_config_musts(usersKeys[user], 'password')
        check_config_musts(usersKeys[user], 'email')
        check_config_musts(usersKeys[user], 'type')


    # Check if syntax is correct
    @check_error
    def syntax_check(user):
        check_email('email', usersKeys[user]['email'])
        check_if_vorv('type', usersKeys[user]['type'], 'admin', 'user')

        if 'hidden' in usersKeys[user]:
            check_if_vorv('hidden', usersKeys[user]['hidden'], 1, 0)

        if 'website' in usersKeys[user]:
            check_website('website', usersKeys[user]['website'])

        if 'country' in usersKeys[user]:
            check_countrycode('country', usersKeys[user]['country'])


    # Loop through all users
    usersKeys = YAMLfile['CTFd']['users']
    for user in usersKeys:
        error.section = 'users, ' + user
        users_key_check(user)
        syntax_check(user)


def pages_check(YAMLfile):
    """
    Check keys in pages
    """
    # Check if key values exist
    @check_error
    def pages_key_check(page):
        check_config_musts(pagesKeys[page], 'page')

    # Check if syntax is correct
    @check_error
    def syntax_check(page):
        if 'file' in pagesKeys[page]:
            for pagefile in pagesKeys[page]['file']:
                check_file('file', 'OCD/pages_files/', pagefile)
        if 'auth_required' in pagesKeys[page]:
            check_if_vorv('auth_required', pagesKeys[page]['auth_required'], 1, 0)


    # Loop through all pages
    pagesKeys = YAMLfile['CTFd']['pages']
    check_config_musts(pagesKeys, 'index')
    for page in pagesKeys:
        error.section = 'pages, ' + page
        pages_key_check(page)
        syntax_check(page)


def challenges_check(YAMLfile):
    """
    check keys in challenges
    """
    # Check if key values exist
    @check_error
    def challenges_key_check(category, challenge):
        check_config_musts(challengesKeys[category][challenge], 'value')
        check_config_musts(challengesKeys[category][challenge], 'description')
        check_config_musts(challengesKeys[category][challenge], 'flag')

    # Check if syntax is correct
    @check_error
    def syntax_check(category, challenge):
        # Check if flag syntax is valid
        @check_error
        def flag_check(flag):
            error.section = 'challenges, ' + category + ', ' + challenge + ', flag'
            check_config_musts(flag, 'flag')

            if 'type' in flag:
                check_if_vorv('type', flag['type'], 'static', 'regex')
            if 'case' in flag:
                check_if_vorv('type', flag['case'], 'insensitive', 'sensitive')

        # Check if hint syntax is valid
        @check_error
        def hint_check(hint):
            error.section = 'challenges, ' + category + ', ' + challenge + ', ' + hint
            check_config_musts(challengesKeys[category][challenge][hint], 'description')

            if 'description' in challengesKeys[category][challenge][hint]:
                check_file('description', 'OCD/challenge_files/', challengesKeys[category][challenge][hint]['description'])
            if 'cost' in challengesKeys[category][challenge][hint]:
                check_if_int('cost', challengesKeys[category][challenge][hint]['cost'])


        if 'max_attempts' in challengesKeys[category][challenge]:
            check_if_int('max_attempts', challengesKeys[category][challenge]['max_attempts'])

        if 'file' in challengesKeys[category][challenge]:
            for challengeFile in challengesKeys[category][challenge]['file']:
                check_file('file', 'OCD/challenge_files/', challengeFile)

        if 'requirements' in challengesKeys[category][challenge]:
            for requirement in challengesKeys[category][challenge]['requirements']:
                check_challenge('requirements', requirement, challengesList)


        hintmatches = [hint for hint in challengesKeys[category][challenge] if re.match(re.compile('^hint*'), hint)]
        for hint in hintmatches:
            hint_check(hint)

        flag_check(challengesKeys[category][challenge]['flag'])


    challengesKeys = YAMLfile['CTFd']['challenges']

    # Get a list of all challenges
    challengesList = []
    for challenges in [challengesKeys[challenge] for challenge in [category for category in challengesKeys]]:
        for name in challenges.keys():
            challengesList.append(name)

    # Loop through all the challenges
    for category in challengesKeys:
        for challenge in challengesKeys[category]:
            error.section = 'challenges, ' + category + ', ' + challenge
            challenges_key_check(category, challenge)
            syntax_check(category, challenge)


# Global error tracker
error = Error()

def main():
    print(Colors().FAIL, end='')
    YAMLfile = read_setup_yaml(sys.argv[1])

    check_yaml_none(**YAMLfile)

    error.section = 'Base'
    CTFd_config_check(YAMLfile)

    error.section = 'CTFd'
    root_config_check(YAMLfile)

    error.section = 'config'
    config_check(YAMLfile)

    error.section = 'users'
    users_check(YAMLfile)

    error.section = 'pages'
    pages_check(YAMLfile)

    error.section = 'challenges'
    challenges_check(YAMLfile)

    print(Colors().SUCCES, end='')
    print('setup.yml seems good')
    print(Colors().NORMAL, end='')


if __name__ == '__main__':
    main()

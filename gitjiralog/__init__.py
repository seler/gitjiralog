#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import configparser
import os
import re
import subprocess
import sys

from jinja2 import Template
from jira import JIRA
from jira.exceptions import JIRAError

"""
Simple script that lists JIRA issues referenced in commit messages.
"""

__author__ = "Rafal Selewonko <rafal@selewonko.com>"
# https://www.python.org/dev/peps/pep-0008/#version-bookkeeping
# https://www.python.org/dev/peps/pep-0440/
__version_info__ = (0, 1, 'dev1',)
__version__ = '.'.join(map(str, __version_info__))

_CONFIG_FILENAME = 'gjl.ini'
CONFIG_FILENAME = os.path.expanduser(os.path.join('~', _CONFIG_FILENAME))
REGEXP = r'([a-zA-Z]+[-][1-9]\d*)'
REGEXP_MISTAKE = r'[@]([a-zA-Z]+[ ]\d+)'
ISSUES_PER_PAGE = 50

CONFIG_EXAMPLE = """
[DEFAULT]
JIRA_URL = http://webvrt59:8080
JIRA_USER = USER123
JIRA_PASS = Password123
"""

CONFIG_HELP = """
This is config example. Should be in {}.
{}
""".format(CONFIG_FILENAME, CONFIG_EXAMPLE)

OUTPUT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>JIRA report</title>
    <meta charset="utf-8" />
</head>
<body>
    <h2>JIRA Issues</h2>
    <ul>
    {% for issue in issues %}
      <li><a href="{{ issue.permalink() }}">{{ issue.key }}</a> - {{ issue.fields.summary }}</li>
    {% endfor %}
    {% if not_matching %}
    </ul>
    <h2>Non JIRA commits</h2>
    <ul>
    {% for issue in not_matching %}
      <li>{{ issue }}</li>
    {% endfor %}
    </ul>
    {% endif %}
</body>
</html>
"""


class GitJiraLogger(object):
    def __init__(self, config_filename=CONFIG_FILENAME):
        self.config_filename = config_filename
        self.parser = self.get_parser()

    @staticmethod
    def get_parser():
        class MyHelpFormatter(argparse.HelpFormatter):
            def _format_usage(self, usage, actions, groups, prefix):
                usage = super(MyHelpFormatter, self)._format_usage(usage, actions, groups, prefix)
                return "{} <git log arguments>\n\n".format(usage[:-2])
        parser = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=MyHelpFormatter,
                                         epilog="optional text below args list")
        # group = parser.add_mutually_exclusive_group()
        # group.add_argument("-v", "--verbose", action="store_true")
        # group.add_argument("-q", "--quiet", action="store_true")
        parser.add_argument('-V', '--version', action='version',
                            version='%(prog)s {}'.format(__version__))
        parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'),
                            default=sys.stdout)
        return parser

    def get_jira_config(self):
        config = configparser.ConfigParser()
        config.read_file(open(self.config_filename))
        return (config['DEFAULT']['JIRA_URL'],
                config['DEFAULT']['JIRA_USER'],
                config['DEFAULT']['JIRA_PASS'])

    def _jira_get_issues(self, jira, pattern, limit):
        try:
            issues = jira.search_issues(pattern, maxResults=limit, fields='summary')
        except JIRAError as error:
            sys.stderr.write(error.text + '\n')
            repa = r"An issue with key '([A-Z]+[-]\d+)' does not exist for field 'key'."
            match = re.match(repa, error.text)
            if match:
                pattern = pattern.replace("{} or key=".format(match.groups()[0]), '')
                issues = self._jira_get_issues(jira, pattern, limit)
            else:
                raise error
        return issues

    def get_jira_issues(self, keys, limit=ISSUES_PER_PAGE):
        jira = JIRA({'server': self.jira_url}, basic_auth=(self.jira_user, self.jira_pass))
        i = 0
        pattern = ""
        all_keys = []
        while True:
            try:
                key = next(keys)
                if key not in all_keys:
                    all_keys.append(key)
                    if pattern:
                        pattern += " or "
                    i += 1
                    pattern += "key={}".format(key)
                    if i == limit:
                        raise IndexError('as')
            except (IndexError, StopIteration) as e:
                issues = self._jira_get_issues(jira, pattern, limit)
                yield from issues
                if isinstance(e, StopIteration):
                    raise e
                i = 0
                pattern = ""

    def configure(self):
        try:
            self.jira_url, self.jira_user, self.jira_pass = self.get_jira_config()
        except FileNotFoundError as e:
            message = "Config file {} not found.".format(e.filename)
            self.parser.error(message + CONFIG_HELP)
        except KeyError as e:
            message = "Config file does not have {} key.".format(e.args[0])
            self.parser.error(message + CONFIG_HELP)
        except Exception as e:
            message = "Could not read config file at {}".format(self.config_filename)
            self.parser.error(message + CONFIG_HELP)

    def run(self):
        args, self.git_log_args = self.parser.parse_known_args()
        if not self.git_log_args:
            self.parser.error("git log arguments are missing.")
        self.configure()
        self.not_matching = []
        ids = self.get_keys_from_git(self.git_log_args, args.outfile.encoding)
        issues = self.get_jira_issues(ids)
        template = Template(OUTPUT_TEMPLATE)
        self.result = template.stream(issues=issues, not_matching=self.not_matching)
        self.result.dump(args.outfile)

    def get_keys_from_git(self, gitlogargs, encoding):
        cmd = 'git log'.split()
        cmd.extend(gitlogargs)
        cmd.extend(['--pretty=%s by %an on %ai (%h)'])
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for line in p.stdout:
            keys = []
            line = line.decode(encoding).strip()
            keys = re.findall(REGEXP, line)
            if not keys:
                keys = re.findall(REGEXP_MISTAKE, line)
                keys = list(map(lambda x: x.replace(' ', '-'), keys))
            if not keys:
                self.not_matching.append(line)
            yield from keys
        p.communicate()


def main():
    gitjiralogger = GitJiraLogger()
    gitjiralogger.run()


if __name__ == '__main__':
    main()

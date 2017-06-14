===========

git jiralog

===========

Simple script that lists JIRA issues referenced in commit messages.

-------------------------------------------------------------------



Installation

============



::



    cd path/to/pyframe/tools/gitjiralog

    python -m pip install . --proxy http://10.71.16.7:8008



Dependencies

============



Script should work on both Python 2.7 and 3.*.



It relies on:



* `jira <http://jira.readthedocs.io/en/latest/installation.html#dependencies>`

which in turn depends on some other stuff and `pycrypto`.

* `Jinja2 <http://jinja2.readthedocs.io/en/latest/>`



Both of these and their dependencies should be installed automatically except

`pycrypto` which we do not need. In case we'll ever need `pycrypto`

`here <https://github.com/axper/python3-pycrypto-windows-installer/raw/master/pycrypto-2.6.1.win32-py3.4.exe>

you can download cp3.4 version for Windows x86.





Setup

=====



Put config file in `~/gjl.ini`.



::



        [DEFAULT]

        JIRA_URL = http://webvrt59:8080

        JIRA_USER = ANDRZEJ123

        JIRA_PASS = Haslo123



Usage

=====





::

   

    git jiralog <git log params> [-o <output file>]



    #example:

    git jiralog v0.1..v0.2



    git jiralog --since=2016-01-01 --until=2017-01-01 --author="Lukasz Matczynski" --no-merges -o test.html 

    

Script uses revision range format exactly same as `git log` command. You can

read more about revision range specification 

`here <https://git-scm.com/docs/git-log#git-log-ltrevisionrangegt>` .

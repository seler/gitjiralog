from setuptools import setup





def readme():

    with open('README.rst') as f:

        return f.read()





setup(name='gitjiralog',

      version='0.1',

      description="Simple script that lists JIRA issues referenced in commit messages.",

      long_description=readme(),

      classifiers=[

        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',

      ],

      keywords='git jira changelog',

      url='http://tasbb-em2-01:7990/projects/PYFRAME',

      author='Rafal Selewonko',

      author_email='rafal.selewonko@willistowerswatson.com',

      license='',

      packages=['gitjiralog'],

      install_requires=[

          'jira', 'jinja2'

      ],

      test_suite='nose.collector',

      tests_require=['nose', 'nose-cover3'],

      entry_points={

          'console_scripts': ['git-jiralog=gitjiralog:main'],

      },

      include_package_data=True,

      zip_safe=False)

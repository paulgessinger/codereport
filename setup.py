from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='codereport',
    version='0.1.6',
    description='Make annotated code reports',
    url='https://github.com/paulgessinger/codereport',
    license='MIT',

    author='Paul Gessinger',

    author_email='hello@paulgessinger.com',

    packages=find_packages(exclude=[]),
    package_data={
        'codereport': ['templates/*'],
    },

    install_requires=['jinja2', 'python-slugify', 'Pygments'],
    tests_require = ['pytest', 'mock']
)

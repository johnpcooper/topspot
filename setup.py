# Writing the setup script: https://pythonhosted.org/an_example_pypi_project/setuptools.html
import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "topspot",
    version = "2.0.0",
    author = "John P. Cooper",
    author_email = "jpcoope@utexas.edu",
    description = ("A package of adapters to spotipy to create ready for command line shortcuts"),
    license = "BSD",
    keywords = "spotify ahk organization",
    url = "https://github.com/johnpcooper/topspot",
    packages=find_packages(),
    package_data={'topspot': ['*.csv', '*.json']},
    include_package_data=True,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
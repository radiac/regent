import os
from setuptools import setup, find_packages

VERSION = "0.0.1"

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "regent",
    version = VERSION,
    author = "Richard Terry",
    author_email = "code@radiac.net",
    description = ("A framework to let users run privileged commands"),
    license = "BSD",
    keywords = "sudo",
    url = "https://radiac.net/projects/regent/",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['six'],
    extras_require = {},
    zip_safe=True,
    packages=find_packages(exclude=('docs', 'tests*',)),
    include_package_data=True,
)

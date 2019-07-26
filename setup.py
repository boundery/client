#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

with io.open('./boundery/__init__.py', encoding='utf8') as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open('README.md', encoding='utf8') as readme:
    long_description = readme.read()


setup(
    name='boundery',
    version=version,
    description='Client for the Boundery home server',
    long_description=long_description,
    author='Nolan Leake',
    author_email='nolan@sigbus.net',
    license='GNU General Public License v3 or later (GPLv3+)',
    packages=find_packages(
        exclude=[
            'docs', 'tests',
            'windows', 'macOS', 'linux',
            'iOS', 'android',
            'django'
        ]
    ),
    include_package_data=True,
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    install_requires=[
        'requests', 'hkdf', 'PyNaCl', 'bottle', 'waitress', 'appdirs'
    ],
    options={
        'app': {
            'formal_name': 'Boundery Client',
            'bundle': 'me.boundery'
        },

        # Desktop/laptop deployments
        'macos': {
            'app_requires': [
	        'rubicon-objc',
            ]
        },
        'linux': {
            'app_requires': [
            ]
        },
        'windows': {
            'app_requires': [
                'pywin32',
            ]
        },

        # Mobile deployments
        'ios': {
            'app_requires': [
            ]
        },
        'android': {
            'app_requires': [
            ]
        },

        # Web deployments
        'django': {
            'app_requires': [
            ]
        },
    }
)

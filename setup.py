import sys
from setuptools import setup, find_packages

requirements = ['aiopg','websockets','aiohttp']

setup(
    version='0.0.0-dev',
    author = 'Simon Wittber',
    author_email = 'simonwittber@differentmethods.com',
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description = 'A MOG Server using asyncio in Python3',
    download_url = '',
    install_requires = requirements,
    package_data = {
        '' : ['*.txt'],
        'network': ['data/*.sql'],
    },
    keywords = ['API', 'Game', 'MMO', 'MOG'],
    license = 'MIT',
    name = 'NetWrok-Server',
    platforms = 'any',
    packages = find_packages('src'),
    package_dir = {'':'src'},
    url = 'http://github.com/DifferentMethods/netwrok-server',
    zip_safe = True,
    entry_points={
        'console_scripts': [
            'netwrok = netwrok.main:run',
            'create_netwrok = netwrok.cmd:create',
        ]
    }
)

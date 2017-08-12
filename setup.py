import os
import codecs
import subprocess

import setuptools

import twitter_logger


with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    install_requires = f.read().splitlines()
    print(install_requires)

setuptools.setup(
    name='twitter_logger',
    version=twitter_logger.__version__,
    description='Twitter logger command',
    author='Takuma Watanabe',
    author_email='takumaw@sfo.kuramae.ne.jp',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords='twitter',
    packages=setuptools.find_packages(exclude=['docs', 'tests*']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'twitter_logger=twitter_logger.cli:main',
        ],
    },
)

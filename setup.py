#!/usr/bin/env python

from setuptools import setup


with open("README.rst") as readme_f:
    README = readme_f.read()

setup(
    name="gmute",
    version="1.4.0",
    python_requires=">=3.5",
    description="Gmail mute support for mutt and other email clients",
    long_description=README,
    url="https://github.com/cdown/gmute",
    license="MIT",
    author="Chris Down",
    author_email="chris@chrisdown.name",
    py_modules=["gmute"],
    entry_points={"console_scripts": ["gmute=gmute:main"]},
    keywords="email gmail mutt headers mute productivity",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Communications :: Email",
        "Topic :: Utilities",
    ],
)

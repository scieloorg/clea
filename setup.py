#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="clea",
    url="https://github.com/scieloorg/clea",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "lxml",
        "numpy",
        "pandas",
        "python-Levenshtein",
        "regex",
        "unidecode",
    ],
    extras_require={"server": ["flask"]},
)

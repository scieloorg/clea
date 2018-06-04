#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="clea",
    url="https://github.com/scieloorg/clea",
    license="2-clause BSD",
    packages=setuptools.find_packages(),
    include_package_data=True,
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
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: XML",
        "Operating System :: OS Independent",
    ),
)

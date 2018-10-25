#!/usr/bin/env python3
import ast, os, setuptools

setup_path = os.path.dirname(__file__)

# Get __version__ from the package __init__.py without importing it
with open(os.path.join(setup_path, "clea", "__init__.py")) as dinit:
    assignment_node = next(el for el in ast.parse(dinit.read()).body
                              if isinstance(el, ast.Assign) and
                                 el.targets[0].id == "__version__")
    version = ast.literal_eval(assignment_node.value)

with open(os.path.join(setup_path, "README.md")) as readme:
    long_description = readme.read()

setuptools.setup(
    name="scielo-clea",
    version=version,
    author="Danilo de Jesus da Silva Bellini",
    author_email="danilo.bellini@gmail.com",
    url="https://github.com/scieloorg/clea",
    description="SciELO Publishing Schema XML document "
                "front matter metadata reader/sanitizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="2-clause BSD",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "lxml",
        "numpy",
        "python-Levenshtein",
        "regex",
        "unidecode",
    ],
    extras_require={"server": ["flask"],
                    "pandas": ["pandas"]},
    classifiers=(
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: XML",
        "Operating System :: OS Independent",
    ),
)

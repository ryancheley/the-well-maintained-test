from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="the-well-maintained-test",
    description="Programatically tries to answer the 12 questions from Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Ryan Cheley",
    url="https://github.com/ryancheley/the-well-maintained-test",
    project_urls={
        "Issues": "https://github.com/ryancheley/the-well-maintained-test/issues",
        "CI": "https://github.com/ryancheley/the-well-maintained-test/actions",
        "Changelog": "https://github.com/ryancheley/the-well-maintained-test/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["the_well_maintained_test"],
    entry_points="""
        [console_scripts]
        the-well-maintained-test=the_well_maintained_test.cli:cli
    """,
    install_requires=["click", "requests"],
    extras_require={
        "test": ["pytest"]
    },
    python_requires=">=3.6",
)

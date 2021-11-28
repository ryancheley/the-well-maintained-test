import os

from setuptools import setup

VERSION = "0.5.0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="the-well-maintained-test",
    description="Programatically tries to answer the 12 questions from \
        Adam Johnson's blog post https://adamj.eu/tech/2021/11/04/the-well-maintained-test/",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Ryan Cheley",
    url="https://github.com/ryancheley/the-well-maintained-test",
    project_urls={
        "Issues": "https://github.com/ryancheley/the-well-maintained-test/issues",
        "CI": "https://github.com/ryancheley/the-well-maintained-test/actions",
        "Changelog": "https://github.com/ryancheley/the-well-maintained-test/releases",
        "Documentation": "https://github.com/ryancheley/the-well-maintained-test/blob/main/README.md",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["the_well_maintained_test"],
    entry_points="""
        [console_scripts]
        the-well-maintained-test=the_well_maintained_test.cli:cli
    """,
    install_requires=["click", "requests", "rich"],
    extras_require={"test": ["pytest", "black", "isort"]},
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

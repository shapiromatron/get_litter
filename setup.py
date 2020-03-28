import re
from pathlib import Path

from setuptools import setup

readme = Path("README.md").read_text()
history = Path("HISTORY.md").read_text()


def get_version():
    regex = r'^__version__ = "(.*)"$'
    with open("litter_getter/__init__.py", "r") as f:
        text = f.read()
    return re.findall(regex, text, re.MULTILINE)[0]


test_requirements = ("pytest",)

setup(
    name="litter_getter",
    version=get_version(),
    description="Retrieve literature from biomedical reference libraries such as PubMed, EPA's HERO, and imports from Endnote RIS exports",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    author="Andy Shapiro",
    author_email="shapiromatron@gmail.com",
    url="https://github.com/shapiromatron/litter_getter",
    packages=["litter_getter"],
    package_dir={"litter_getter": "litter_getter"},
    include_package_data=True,
    install_requires=["requests", "XlsxWriter", "RISparser"],
    extras_require={
        "dev": [
            "wheel",
            "black==19.10b0",
            "flake8==3.7.9",
            "isort==4.3.21",
            "flake8-isort==2.8.0",
            "twine",
        ],
        "test": test_requirements,
    },
    license="MIT license",
    zip_safe=False,
    keywords="litter_getter",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=test_requirements,
)

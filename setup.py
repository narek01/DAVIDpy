from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pandas>=1.0.0", "suds>=0.4", "biomart"]

setup(
    name="DAVIDpy",
    version="0.1.1",
    author="Narek Engibaryan",
    author_email="narek030601@yandex.ru",
    description="Python3 extension for DAVID Bioinformatics Tool",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/narek01/DAVIDpy",
    license="GPLv3",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "davidpy=davidpy.davidpy:main",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
)
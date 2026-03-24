from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name= "YT SEO INSIGHTS GEN",
    version= "1.0.0",
    author= "Sudhanshu",
    packages=find_packages(),
    install_requires=requirements,
)
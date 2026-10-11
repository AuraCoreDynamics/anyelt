from setuptools import setup, find_packages

setup(
    name="anyelt",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "anyelt = anyelt.cli:main",
        ],
    },
)

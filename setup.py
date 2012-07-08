from setuptools import setup, find_packages

setup(
    name="artichoke",
    version="0.1.1",
    packages = find_packages(),
    package_data={
        'artichoke' : [
            '*.*',
        ]
    },
    long_description="Tool to easily manipulate and generate .ini config files."
)


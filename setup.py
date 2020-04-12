from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='natLight',
	version='0.1',
	description='Natural Ligth to RGB Converter',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://gitlab.com/stroblme/naturalLight.git',
	author='Melvin Strobl',
	packages=['natLight'],
	zip_safe=False)
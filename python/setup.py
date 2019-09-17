from distutils.core import setup

setup(name='weles',
	version='1.0',
	description='The Python client package for communication with model governance base "vimo".',
	url='https://github.com/WojciechKretowicz/vimo',
	author='Wojciech Kretowicz',
	author_email='wojtekkretowicz@gmail.com',
	packages=['weles'],
	install_requires=[
		'requests',
		'pandas',
		'tqdm'
	],
      zip_safe=False)

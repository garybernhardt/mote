from setuptools import setup, find_packages

setup(name='mote',
      version='0.1',
      description='Mote',
      author='Gary Bernhardt',
      author_email='gary.bernhardt@gmail.com',
      packages=['mote'],
      license='BSD',
      entry_points={
          'console_scripts': ['mote=mote.runner:main']
      }
     )

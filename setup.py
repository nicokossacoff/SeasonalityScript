import setuptools
from setuptools import setup

setup(name= 'SeasonalityScript',
      packages= ["SeasonalityScript"],
      version= '1.0.0',
      description= 'Bank holidays and seasonality variables creation',
      author= 'Nicolás Kossacoff',
      author_email= 'nicokossacoff@gmail.com',
      install_requires= ["pandas>=2.0.0",
                         "numpy>=1.26.4",
                         "requests>=2.31.0"],
      license= 'Apache',
      packages= setuptools.find_packages(),
      classifiers= ["Programming Language :: Python :: 3", "License :: OSI Approved :: Apache License"],
      zip_safe= False)
from setuptools import setup

setup(name="submodular_approximation",
      version='0.1.0',
      author="Andrew Downie",
      author_email="acdownie@uwaterloo.ca",
      packages=['submodular_approximation'],
      scripts=['scripts/test_script.py','scripts/new_york_city_taxi_experiment.py','scripts/visualize_nyc_taxi.py'],
      description="A submodular optimization package for using approximate marginal returns.",
      #long_description = open("README.md").read(),
      install_requires = [
          
      ]
      )
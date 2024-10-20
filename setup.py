from setuptools import setup, find_packages
import os
import yaml
import subprocess

# we're on jenkins.  just do what Jenkins tells us
if 'APP_VERSION' in os.environ.keys():
  version = os.environ['APP_VERSION']

# let's figure out the version and branch from local files
else:
  with open('application.yaml') as f:
    application = yaml.safe_load(f)
  branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD'.split(), encoding='UTF-8')
  version = '{version}.{build}+snapshot.{branch}'.format(
    version=application['version'],
    build=application['build'],
    branch=branch.rstrip()
  )

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

setup(
  name='meta-hackathon-finance',
  packages=find_packages(),
  version=version,
)

__author__ = 'mmikofski'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from pvmismatch import __version__ as VERSION, __name__ as NAME


setup(name=NAME,
      version=VERSION,
      description='PV Mismatch Calculator',
      author=__author__,
      author_email='mark.mikofski@sunpower.com',
      url='https://github.com/SunPower/PVMismatch',
      packages=['pvmismatch', 'pvmismatch_tk'],
      requires=['numpy (>=1.8)', 'matplotlib (>=1.3)', 'scipy (>=0.12.0)'],
      scripts=['pv_tk.py'],
      package_data={'pvmismatch_tk':
                        ['pvmismatch_json/messagetext.English.json',
                         'pvmismatch_json/validationConstants.json',
                         'res/logo.png', 'res/logo_bg.png', 'docs/conf.py',
                         'docs/*.rst', 'docs/Makefile', 'docs/make.bat']})

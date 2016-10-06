__author__ = 'mmikofski'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from pvmismatch import __version__, __name__


setup(name=__name__,
      version=__version__,
      description='PV Mismatch Calculator',
      author=__author__,
      author_email='mark.mikofski@sunpower.com',
      url='https://github.com/SunPower/PVMismatch',
      packages=['pvmismatch', 'pvmismatch.pvmismatch_lib',
                'pvmismatch.pvmismatch_tk'],
      requires=['numpy (>=1.8)', 'matplotlib (>=1.3)', 'scipy (>=0.12.0)'],
      scripts=['pv_tk.py'],
      package_data={'pvmismatch':
                        ['pvmismatch_json/messagetext.English.json',
                         'pvmismatch_json/validationConstants.json',
                         'res/logo.png', 'res/logo_invert.png',
                         'res/logo_bg.png', 'docs/conf.py', 'docs/*.rst',
                         'docs/Makefile', 'docs/make.bat']})

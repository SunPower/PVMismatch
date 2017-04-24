__author__ = 'mmikofski'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from pvmismatch import __version__, __name__, __email__, __url__
import os

README = 'README.rst'
try:
    with open(os.path.join(os.path.dirname(__file__), README), 'r') as readme:
        README = readme.read()
except IOError:
    pass

setup(name=__name__,
      version=__version__,
      description='PV Mismatch Calculator',
      long_description=README,
      author=__author__,
      author_email=__email__,
      url=__url__,
      license='BSD 3-clause',
      packages=['pvmismatch', 'pvmismatch.pvmismatch_lib',
                'pvmismatch.pvmismatch_tk', 'pvmismatch.contrib',
                'pvmismatch.contrib.gen_coeffs'],
      requires=['numpy (>=1.8)', 'matplotlib (>=1.3)', 'scipy (>=0.12.0)'],
      scripts=['pv_tk.py'],
      package_data={'pvmismatch':
                        ['pvmismatch_json/messagetext.English.json',
                         'pvmismatch_json/validationConstants.json',
                         'res/logo.png', 'res/logo_invert.png',
                         'res/logo_bg.png', 'docs/conf.py', 'docs/*.rst',
                         'docs/Makefile', 'docs/make.bat']})

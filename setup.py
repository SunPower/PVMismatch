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

INSTALL_REQUIRES = [
    'numpy>=1.13.3', 'matplotlib>=2.1.0', 'scipy>=1.0.0', 'future>=0.16.0',
    'six>=1.11.0'
]

TESTS_REQUIRES = [
    'nose>=1.3.7', 'pytest>=3.2.1', 'sympy>=1.1.1', 'pvlib>=0.5.1'
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Scientific/Engineering',
]

setup(
    name=__name__,
    version=__version__,
    description='PV Mismatch Calculator',
    long_description=README,
    author=__author__,
    author_email=__email__,
    url=__url__,
    license='BSD 3-clause',
    packages=[
        'pvmismatch', 'pvmismatch.pvmismatch_lib',
        'pvmismatch.pvmismatch_tk', 'pvmismatch.contrib',
        'pvmismatch.contrib.gen_coeffs'
    ],
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRES,
    scripts=['pv_tk.py'],
    package_data={
        'pvmismatch': [
            'pvmismatch_json/messagetext.English.json',
            'pvmismatch_json/validationConstants.json',
            'res/logo.png', 'res/logo_invert.png',
            'res/logo_bg.png', 'docs/conf.py', 'docs/*.rst',
            'docs/Makefile', 'docs/make.bat'
        ]
    },
    classifiers=CLASSIFIERS
)

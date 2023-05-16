"""Distribution package setup script."""
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as readme_file:
    readme = readme_file.read()
try:
    with open('CHANGELOG.rst') as changelog_file:
        changelog = changelog_file.read()
    long_description = '\n\n'.join((readme, changelog))
except FileNotFoundError:
    long_description = readme

setup(
    name='mca',
    description='Graph based signal processing tool.'
                ' Data is being passed between blocks via inputs and outputs'
                ' in a block diagram. Allows sequential and parallel execution'
                ' of various processing steps in a easy and trivial manner.',
    long_description=long_description,
    author='Kevin Koch',
    author_email='kevink2@mail.uni-paderborn.de',
    url='https://github.com/emtpb/mca/',
    license='BSD',

    # Automatically generate version number from git tags
    use_scm_version=True,

    # Automatically detect the packages and sub-packages
    packages=find_packages(),

    # Runtime dependencies
    install_requires=[
        'numpy', 'scipy', 'networkx', 'matplotlib', 'appdirs', 'PySide2',
        'united', 'sounddevice', 'qdarkstyle', 'handyscope', 'dsch'],

    # Python version requirement
    python_requires='>=3',

    # Additional package data
    package_data={'mca': ['version.txt', 'images/emt_logo.png',
                          'locales/*/LC_MESSAGES/*.po',
                          'locales/*/LC_MESSAGES/*.mo']},

    # Dependencies of this setup script
    setup_requires=[
        'setuptools_scm',  # For automatic git-based versioning
    ],

    # For a full list of valid classifiers, see:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],
    entry_points={
        'console_scripts': ['mca=mca.main:main'],
    },
)

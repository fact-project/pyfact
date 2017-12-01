from setuptools import setup, find_packages

with open('fact/VERSION', 'r') as f:
    __version__ = f.read().strip()


setup(
    name='pyfact',
    version=__version__,
    description='A module containing useful methods for working with fact',
    url='http://github.com/fact-project/pyfact',
    author='Maximilian Noethe, Dominik Neise',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=find_packages(),
    package_data={
        '': [
            'VERSION',
            'resources/*',
            'credentials/credentials.encrypted',
        ]
    },
    entry_points={
        'console_scripts': [
            'fact_calculate_theta = fact.analysis.scripts.theta:main',
            'fact_calculate_radec = fact.analysis.scripts.radec:main',
        ]
    },
    tests_require=['pytest>=3.0.0'],
    setup_requires=['pytest-runner'],
    install_requires=[
        'astropy',
        'h5py',
        'matplotlib>=1.4',
        'numpy',
        'pandas',
        'peewee',
        'pymongo>=2.7',
        'pymysql',
        'python-dateutil',
        'scipy',
        'setuptools',
        'simple-crypt',
        'sqlalchemy',
        'tables',  # pytables in anaconda
        'wrapt',
    ],
    zip_safe=False,
)

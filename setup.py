from setuptools import setup


setup(
    name='pyfact',
    version='0.8.6',
    description='A module containing useful methods for working with fact',
    url='http://github.com/fact-project/pyfact',
    author='Maximilian Noethe, Dominik Neise',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=[
        'fact',
        'fact.plotting',
        'fact.slowdata',
        'fact.credentials',
        'fact.auxservices',
        'fact.factdb',
    ],
    package_data={
        '': ['resources/*', 'credentials/credentials.encrypted']
    },
    tests_require=['pytest>=3.0.0'],
    setup_requires=['pytest-runner'],
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib>=1.4',
        'python-dateutil',
        'pymongo>=2.7',
        'simple-crypt',
        'setuptools',
        'sqlalchemy',
        'pymysql',
        'pandas',
        'astropy',
        'peewee',
    ],
    zip_safe=False,
)

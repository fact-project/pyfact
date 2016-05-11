from distutils.core import setup


setup(
    name='fact',
    version='0.5.0',
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
    ],
    package_data={
        '': ['resources/*', 'credentials/credentials.encrypted']},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib>=1.4',
        'python-dateutil',
        'pymongo>=2.7',
        'simple-crypt',
        'setuptools',
        'sqlalchemy',
    ],
    zip_safe=False,
)

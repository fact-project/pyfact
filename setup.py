from distutils.core import setup

setup(
    name='fact',
    version='0.2',
    description='a module containing usefull methods for working with fact',
    url='http://bitbucket.org/MaxNoe/pyfact',
    author='Maximilian Noethe, Dominik Neise',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=['fact',
              'fact.plotting',
              'fact.dim'
              ],
    package_data={'': ['resources/*']},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
    ],
    zip_safe=False
)

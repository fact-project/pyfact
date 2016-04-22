from distutils.core import setup, Extension
from sys import platform

dimc_module = Extension(
    'fact.dim.dimc',
    define_macros=[
        ('PROTOCOL', '1'),
        ('unix', None),
        ('linux', None),
        ('MIPSEL', None),
    ],
    include_dirs=['./fact/dim/dim_src/include'],
    sources=[
       './fact/dim/dim_src/wrapper/dimmodule.cpp',
       './fact/dim/dim_src/wrapper/pydim_utils.cpp',
       './fact/dim/dim_src/src/dis.c',
       './fact/dim/dim_src/src/conn_handler.c',
       './fact/dim/dim_src/src/dtq.c',
       './fact/dim/dim_src/src/copy_swap.c',
       './fact/dim/dim_src/src/open_dns.c',
       './fact/dim/dim_src/src/dna.c',
       './fact/dim/dim_src/src/tcpip.c',
       './fact/dim/dim_src/src/dic.c',
       './fact/dim/dim_src/src/hash.c',
       './fact/dim/dim_src/src/utilities.c',
       './fact/dim/dim_src/src/sll.c',
       './fact/dim/dim_src/src/dll.c',
       './fact/dim/dim_src/src/swap.c',
       './fact/dim/dim_src/src/dim_thr.c',
      ]
    )

packages = [
    'fact',
    'fact.plotting',
    'fact.slowdata'
    ]
ext_modules = []

if not platform == 'darwin':
    packages.append('fact.dim')
    ext_modules.append(dimc_module)

setup(
    name='fact',
    version='0.3',
    description='A module containing useful methods for working with fact',
    url='http://github.com/fact-project/pyfact',
    author='Maximilian Noethe, Dominik Neise',
    author_email='maximilian.noethe@tu-dortmund.de',
    license='MIT',
    packages=packages,
    package_data={'': ['resources/*']},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib>=1.4',
        'python-dateutil',
        'pymongo>=2.7',
    ],
    ext_modules=ext_modules,
    scripts=[],
    zip_safe=False,
)

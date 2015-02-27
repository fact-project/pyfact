from distutils.core import setup, Extension

dimc_module = Extension('dimc',
    define_macros = [('PROTOCOL', '1'),
                     ('unix', None),
                     ('linux', None),
                     ('MIPSEL', None), ],
    include_dirs = ['./unused/dim/dim_src/include'],
    sources = [
       './unused/dim/dim_src/wrapper/dimmodule.cpp', 
       './unused/dim/dim_src/wrapper/pydim_utils.cpp',
       './unused/dim/dim_src/src/dis.c',
       './unused/dim/dim_src/src/conn_handler.c',
       './unused/dim/dim_src/src/dtq.c',
       './unused/dim/dim_src/src/copy_swap.c',
       './unused/dim/dim_src/src/open_dns.c',
       './unused/dim/dim_src/src/dna.c',
       './unused/dim/dim_src/src/tcpip.c',
       './unused/dim/dim_src/src/dic.c',
       './unused/dim/dim_src/src/hash.c',
       './unused/dim/dim_src/src/utilities.c',
       './unused/dim/dim_src/src/sll.c',
       './unused/dim/dim_src/src/dll.c',
       './unused/dim/dim_src/src/swap.c',
       './unused/dim/dim_src/src/dim_thr.c',
      ]
    )

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
              ],
    package_data={'': ['resources/*']},
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib>=1.4',
        'python-dateutil',
    ],
    ext_modules=[dimc_module],
    scripts=[],
    zip_safe=False
)
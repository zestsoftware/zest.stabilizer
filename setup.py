from setuptools import setup, find_packages
import os

version = '1.2.2'

setup(
    name='zest.stabilizer',
    version=version,
    description="Script to help move a buildout from unstable to stable",
    long_description=(open(os.path.join('zest',
                                        'stabilizer',
                                        'README.txt')).read() +
                      '\n\n' +
                      open(os.path.join('zest',
                                        'stabilizer',
                                        'HISTORY.txt')).read() +
                      '\n\n' +
                      open(os.path.join('zest',
                                        'stabilizer',
                                        'CREDITS.txt')).read() +
                      '\n\n' +
                      open(os.path.join('zest',
                                        'stabilizer',
                                        'TODO.txt')).read()),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='',
    author='Reinout and Maurits van Rees',
    author_email='reinout@vanrees.org',
    url='http://pypi.python.org/pypi/zest.stabilizer',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['zest'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'zest.releaser >= 1.5',
        ],
    entry_points={
        'console_scripts': ['stabilize = zest.stabilizer.stabilize:main',
                            'needrelease = zest.stabilizer.needrelease:main',
                            'unstable_fixup = zest.stabilizer.unstable:main'],
        },
    )

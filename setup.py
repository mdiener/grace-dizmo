from glob import glob
import os
from setuptools import setup


def gather_files(folder):
    previous = ''
    data = []

    for root, dirs, files in os.walk(os.path.join('grace-dizmo', folder)):
        for filename in files:
            if previous != root:
                filelist = glob(root + '/*.*')
                for f in filelist:
                    data.append(f[12:])
                    previous = root

    return data


setup(
    name='grace_dizmo',
    description='A plugin for grace',
    author='Michael Diener',
    author_email='michael@webdiener.ch',
    url='https://github.com/mdiener/grace-dizmo',
    version='0.4.6',
    license='LICENSE.txt',
    packages=['grace-dizmo'],
    install_requires=['grace>=0.5.7', 'setuptools', 'requests'],
    package_data={
        'grace-dizmo': gather_files('py27')
    },
    keywords='toolchain javascript dizmo js buildtool',
    long_description=open('README.txt').read(),
    classifiers=[
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: JavaScript',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Intended Audience :: Developers',
        'Environment :: Console'
    ]
)

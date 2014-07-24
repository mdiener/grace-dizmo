from glob import glob
from distutils.core import setup
import sys
import py2exe
import os

sys.path.append('C:\\Program Files (x86)\\Microsoft Visual Studio 11.0\\VC\\redist\\x86\\Microsoft.VC110.CRT')
data_files = [
    ('Microsoft.VC110.CRT', glob(r'C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\redist\x86\Microsoft.VC110.CRT\*.*'))
]

previous = ''
for root, dirs, files in os.walk(os.path.join('grace-dizmo', 'skeleton')):
    for filename in files:
        if previous != root:
            data_files.append((root[6:], glob(root + '\*.*')))
            previous = root

setup(
    name='grace_dizmo',
    description='A plugin for grace',
    author='Michael Diener',
    author_email='michael@webdiener.ch',
    url='https://github.com/mdiener/grace-dizmo',
    version='0.2.0',
    license='LICENSE.txt',
    packages=['grace-dizmo'],
    install_requires=['grace'],
    data_files=data_files,
    console=['../grace/bin/grace'],
    keywords='toolchain javascript dizmo js buildtool',
    long_description=open('README.txt').read(),
    options={
        'py2exe': {
            'packages': ['grace-dizmo'],
            'bundle_files': True
        }
    }
)

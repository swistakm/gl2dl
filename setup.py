# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return '.'.join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))


try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')

except ImportError:
    print(
        "warning: pypandoc module not found, could not convert Markdown to RST"
    )

    def read_md(f):
        return open(f, 'r').read()  # noqa

init = os.path.join(os.path.dirname(__file__), 'gl2dl', '__init__.py')
version_line = list(filter(lambda l: l.startswith('VERSION'), open(init)))[0]
VERSION = get_version(eval(version_line.split('=')[-1]))

PACKAGES = find_packages('src')
PACKAGE_DIR = {'': 'src'}

setup(
    name='gl2dl',
    version=VERSION,
    author='Michał Jaworski',
    author_email='swistakm@gmail.com',
    description='Minimalistic Python OpenGL game framework',
    long_description=read_md('README.md'),

    packages=['gl2dl'],

    url='https://github.com/swistakm/gl2dl',
    include_package_data=True,
    install_requires=[
        'PyOpenGL',
        'numpy',
        'pillow',
    ],
    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
)

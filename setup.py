import os
from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), 'rb') as f:
        return f.read().decode('utf-8')


setup(
    name='collectd_systemd',
    description='Collectd plugin to monitor systemd services',
    license='MIT',
    url='https://github.com/mbachry/collectd-systemd/',
    version='0.0.1',
    author='Marcin Bachry',
    author_email='hegel666@gmail.com',
    long_description=read("README.rst"),
    py_modules=['collectd_systemd'],
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as file_handle:
    README = file_handle.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-speedbar',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Provides a break down of page loading time',
    long_description=README,
    url='http://github.com/theospears/django-speedbar',
    author='Theo Spears',
    author_email='theo@mixcloud.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'ProxyTypes>=0.9',
        'Django >=1.5, <1.7',
    ],
)

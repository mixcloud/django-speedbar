from setuptools import setup, find_packages

tests_require = [
    'Django>=1.4,<1.9',
]

install_requires = [
    'ProxyTypes>=0.9',
]

setup(
    name='django-speedbar',
    version='0.2.2',
    author='Mat Clayton',
    author_email='mat@mixcloud.com',
    url='http://github.com/mixcloud/django-speedbar',
    description='Provides a break down of page loading time',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=["tests",]),
    install_requires=install_requires,
    license='MIT License',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite="testrunner.runtests",
    include_package_data=True,
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
)

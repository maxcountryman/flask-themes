"""
Fleem
------------
Fleem provides infrastructure for theming support in Flask
applications. It takes care of:

- Loading themes
- Rendering templates from themes
- Serving static files like CSS and images from themes


Links
`````
* `documentation <http://packages.python.org/>`_
* `development version
  <http://>`_


"""
from flask_fleem import __version__
from setuptools import setup
import sys
requires = ['Flask>=0.9',
            'Flask-Assets>=0.8']
if sys.version_info < (2, 6):
    requires.append('simplejson')

setup(
    name='Flask-Fleem',
    version=__version__,
    url='http://',
    license='MIT',
    author='thrisp/hurrata',
    author_email='blueblank@gmail.com',
    description='Provides infrastructure for theming Flask applications',
    long_description=__doc__,
    packages=['flask_fleem'],
    zip_safe=False,
    platforms='any',
    install_requires=requires,
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

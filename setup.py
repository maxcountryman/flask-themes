"""
Flask-Themes
------------
Flask-Themes provides infrastructure for theming support in Flask
applications. It takes care of:

- Loading themes
- Rendering templates from themes
- Serving static files like CSS and images from themes


Links
`````
* `documentation <http://packages.python.org/Flask-Themes>`_
* `development version
  <http://bitbucket.org/leafstorm/flask-themes/get/tip.gz#egg=Flask-Themes-dev>`_


"""
from setuptools import setup
import sys
requires = ['Flask>=0.6']
if sys.version_info < (2, 6):
    requires.append('simplejson')

setup(
    name='Flask-Themes',
    version='0.1.4',
    url='http://bitbucket.org/leafstorm/flask-themes/',
    license='MIT',
    author='Matthew "LeafStorm" Frazier',
    author_email='leafstormrush@gmail.com',
    description='Provides infrastructure for theming Flask applications',
    long_description=__doc__,
    packages=['flask_themes'],
    zip_safe=False,
    platforms='any',
    install_requires=requires,
    tests_require='nose',
    test_suite='nose.collector',
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

#!/usr/bin/env python

import os

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.md')) as readme_file, \
        open(os.path.join(HERE, 'CHANGES.md')) as changes_file, \
        open(os.path.join(HERE, 'terra_geocrud', 'VERSION.md')) as version_file:
    README = readme_file.read()
    CHANGES = changes_file.read()
    VERSION = version_file.read().strip()

tests_require = [
    'factory-boy',
    'flake8',
    'coverage',
]

setup(
    name='django-terra-geocrud',
    version=VERSION,
    include_package_data=True,
    author="Makina Corpus",
    author_email="terralego-pypi@makina-corpus.com",
    description='Geographic CRUD for django-geostore',
    long_description=README + '\n\n' + CHANGES,
    description_content_type="text/markdown",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url='https://github.com/Terralego/django-terra-geocrud.git',
    python_requires='>=3.6',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
    ],
    install_requires=[
        'django>=2.2',
        'django-reversion>=3.0.4',
        'django-template-model>=1.0.1',
        'django-template-engines>=1.3.8',
        'django-mapbox-baselayer>=0.0.3',
        'django-geostore>=0.5.0',
        'django-terra-accounts>=1.0.1',
        'djangorestframework-gis',
        'djangorestframework',
        'requests[security]',
        'pillow',
        'sorl-thumbnail>=12.6.2',
        # improve configuration with django admin
        'django-admin-thumbnails',
        'django-json-widget>=1.0.1',
        'django-admin-ordering',
        'django-object-actions',
        'django-nested-admin',
    ],
    tests_require=tests_require,
    extras_require={
        'routing': ['django-geostore-routing'],
        'dev': tests_require + [
            'django-debug-toolbar<3.3',  # 3.3.0 is not compatible with Django < 3.2,
        ]
    }
)

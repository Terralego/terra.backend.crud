[![](https://img.shields.io/static/v1?logo=python&label=Python&message=3.6%20|%203.7%20|%203.8%20|%203.9&color=306998&logoColor=white)](https://www.djangoproject.com/)
[![](https://img.shields.io/static/v1?logo=django&label=Django&message=2.2%20|%203.0%20|%203.1%20|%203.2&color=0C4B33&logoColor=white)](https://www.djangoproject.com/)

[![](https://codecov.io/gh/Terralego/django-terra-geocrud/branch/master/graph/badge.svg)](https://codecov.io/gh/Terralego/django-terra-geocrud)
[![](https://api.codeclimate.com/v1/badges/633c620b6dcfc0e18df2/maintainability)](https://codeclimate.com/github/Terralego/django-terra-geocrud/maintainability)
[![](https://travis-ci.org/Terralego/django-terra-geocrud.svg?branch=master)](https://travis-ci.org/Terralego/django-terra-geocrud)

https://django-terra-geocrud.readthedocs.io/

Backend API configurator for Geographic CRUD. Based on **django-geostore**

* Customize Menu entries, geographic layers and features
* Customized endpoints to manage layers and features
* Group feature properties, order them, define layout and style to render forms and geometries with mapbox


## Requirements

* django 2.2+
* geodjango enabled with postgres 10+ / postgis 2.4+ (pgrouting optionnal)

## DEVELOPMENT

### with docker :
```bash
$ docker-compose build
$ docker-compose up
....
$ docker-compose run web /code/venv/bin/python ./manage.py shell
$ docker-compose run web coverage run ./manage.py test
```

### with pip :
```bash
$ python3 -m venv venv
$ source activate venv/bin/activate
pip install -e .[dev]
```

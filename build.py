#!/usr/bin/python
# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('static-website-generator-with-jinja2-example', 'templates'))
index_template = env.get_template('index.html')


# video_list_template = env.get_template('video_list.html')



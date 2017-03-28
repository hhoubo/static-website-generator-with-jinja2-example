#!/usr/bin/python
# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader
import yaml
import logging

logger = logging.getLogger(__name__)
env = Environment(loader=PackageLoader('static-website-generator-with-jinja2-example', 'templates'))
index_template = env.get_template('index.html')
branch_template = env.get_template('video_list.html')
video_template = env.get_template('video.html')


def load_config():
    with open('variable/website_config.yml') as config_file:
        config = yaml.load(config_file)
    return config


def _make_index_var(config):
    return {'website_title': '',
            'shops': [{'page': '',
                       'name': '',
                       'latest_video_page': '',
                       'latest_video_image': '',
                       'video_info': {'title': '', 'date': '', 'description': ''}
                       }
                      ]
            }


def _make_branch_var(config):
    return [
        {'website_title': '',
         'branch_page': '',
         'tabs': [{'page': '', 'title': '', 'active': True},
                  {'page': '', 'title': '', 'active': False}
                  ],
         'video_list': [{'video_page': '',
                         'image_source': '',
                         'video_info': {'title': '', 'date': '', 'description': ''}
                         }
                        ]
         }]


def _make_video_var(config):
    return [{'website_title': '',
             'video_page': '',
             'video_info': {'title': '', 'date': '', 'description': '', 'source': '', 'volume': ''},
             'tab': {'title': ''},
             'guess_you_like_list': [{'video_page': '',
                                      'image_source': '',
                                      'video_info': {'title': '', 'date': '', 'description': ''}
                                      }
                                     ]
             }]


def build_website():
    config = load_config()
    rendered_index = index_template.render(_make_index_var(config))
    write('index.html', rendered_index)

    branches = _make_branch_var(config)
    for branch in branches:
        rendered_branch = branch_template.render(branch)
        write(branch.branch_page, rendered_branch)

    videos = _make_video_var(config)
    for video in videos:
        rendered_video = video_template.render(video)
        write(video.video_page, rendered_video)


def write(file_name, rendered_template):
    with open(file_name, 'wb') as html:
        html.write(rendered_template)


if __name__ == "__main__":
    FORMAT = '%(asctime)s  %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    build_website()

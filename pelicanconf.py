#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'R4nd0m 6uy'
SITENAME = "R4nd0m's Blog"
SITEURL = 'https://www.r4nd0m6uy.ch'
#SITEURL = 'http://localhost:8000'
FAVICON = SITEURL + '/images/favicon.ico'
PATH = 'content'
TIMEZONE = 'Europe/Zurich'
DEFAULT_LANG = 'en'
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
DEFAULT_PAGINATION = 5
LINKS = (
)
SOCIAL =  (
  ('rss', '//r4nd0m6uy.ch/feeds/all.atom.xml'),
  ('github', 'https://github.com/r4nd0m6uy'),
  ('linkedin', 'https://www.linkedin.com/in/guy-morand-6baa7223'),
  ('soundcloud', 'https://soundcloud.com/random-guy'),
)
STATIC_PATHS = [
  'images',
  'extra'
]

#RELATIVE_URLS = True

# Flex template configuration
THEME = 'themes/flex'
SITETITLE = 'R4nd0m\'s'
SITESUBTITLE = 'Software Engineer'
SITEDESCRIPTION = 'Description'
CC_LICENSE = True
COPYRIGHT_YEAR = 2016
SITELOGO = u'//en.gravatar.com/userimage/31970073/6fb72a3845a6aea9964b00bd864c29dc.png?size=200'
MAIN_MENU = True
MENUITEMS = (
  ('Archives', '/archives.html'),
  ('Categories', '/categories.html'),
  ('Tags', '/tags.html'),
)


"""
test-themes.py
==============
This tests the Flask-Themes extension.
"""
import os.path
from flask import Flask
from flaskext.themes import (setup_themes, Theme, load_themes_from,
    packaged_themes_loader, theme_paths_loader)
from jinja2 import FileSystemLoader
from operator import attrgetter

TESTS = os.path.dirname(__file__)
join = os.path.join


class TestThemeObject(object):
    def test_theme(self):
        path = join(TESTS, 'themes', 'cool')
        cool = Theme(path)
        assert cool.name == 'Cool Blue v1'
        assert cool.identifier == 'cool'
        assert cool.path == os.path.abspath(path)
        assert cool.static_path == join(cool.path, 'static')
        assert cool.templates_path == join(cool.path, 'templates')
        assert cool.license_text is None
        assert isinstance(cool.jinja_loader, FileSystemLoader)
    
    def test_license_text(self):
        path = join(TESTS, 'themes', 'plain')
        plain = Theme(path)
        assert plain.license_text.strip() == 'The license.'


class TestLoaders(object):
    def test_load_themes_from(self):
        path = join(TESTS, 'themes')
        themes_iter = load_themes_from(path)
        themes = list(sorted(themes_iter, key=attrgetter('identifier')))
        assert themes[0].identifier == 'cool'
        assert themes[1].identifier == 'notthis'
        assert themes[2].identifier == 'plain'
    
    def test_packaged_themes_loader(self):
        app = Flask(__name__)
        themes_iter = packaged_themes_loader(app)
        themes = list(sorted(themes_iter, key=attrgetter('identifier')))
        assert themes[0].identifier == 'cool'
        assert themes[1].identifier == 'notthis'
        assert themes[2].identifier == 'plain'
    
    def test_theme_paths_loader(self):
        app = Flask(__name__)
        app.config['THEME_PATHS'] = [join(TESTS, 'morethemes')]
        themes = list(theme_paths_loader(app))
        assert themes[0].identifier == 'cool'

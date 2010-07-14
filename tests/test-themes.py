"""
test-themes.py
==============
This tests the Flask-Themes extension.
"""
import os.path
from flask import Flask, url_for
from flaskext.themes import (setup_themes, Theme, load_themes_from,
    packaged_themes_loader, theme_paths_loader, ThemeManager, static_file_url,
    template_exists, themes_mod)
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


class TestSetup(object):
    def test_manager(self):
        app = Flask(__name__)
        manager = ThemeManager(app, 'testing')
        assert app.theme_manager is manager
        app.config['THEME_PATHS'] = [join(TESTS, 'morethemes')]
        manager.refresh()
        themeids = manager.themes.keys()
        themeids.sort()
        assert themeids == ['cool', 'plain']
        assert manager.themes['cool'].name == 'Cool Blue v2'
    
    def test_setup_themes(self):
        app = Flask(__name__)
        app.config['THEME_PATHS'] = [join(TESTS, 'morethemes')]
        setup_themes(app, app_identifier='testing')
        
        assert hasattr(app, 'theme_manager')
        assert '_themes' in app.modules
        assert 'theme' in app.jinja_env.globals
        assert 'theme_static' in app.jinja_env.globals


class TestStatic(object):
    def test_static_file_url(self):
        app = Flask(__name__)
        app.config['THEME_PATHS'] = [join(TESTS, 'morethemes')]
        setup_themes(app, app_identifier='testing')
        
        with app.test_request_context('/'):
            url = static_file_url('cool', 'style.css')
            genurl = url_for('_themes.static', themeid='cool',
                             filename='style.css')
            assert url == genurl


class TestTemplates(object):
    def test_template_exists(self):
        app = Flask(__name__)
        app.config['THEME_PATHS'] = [join(TESTS, 'morethemes')]
        setup_themes(app, app_identifier='testing')
        
        with app.test_request_context('/'):
            assert template_exists('hello.html')
            assert template_exists('_themes/cool/hello.html')
            assert not template_exists('_themes/plain/hello.html')
    
    def test_loader(self):
        app = Flask(__name__)
        app.config['THEME_PATHS'] = [join(TESTS, 'morethemes')]
        setup_themes(app, app_identifier='testing')
        
        with app.test_request_context('/'):
            src = themes_mod.jinja_loader.get_source(app.jinja_env,
                                                     'cool/hello.html')
            assert src[0].strip() == 'Hello from Cool Blue v2.'

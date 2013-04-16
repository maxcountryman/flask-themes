# -*- coding: utf-8 -*-
"""
flask.ext.fleem
===============
This provides infrastructure for theming support in your Flask applications.
It takes care of:

- Loading themes
- Rendering their templates
- Serving their static media
- Letting themes reference their templates and static media
"""
from __future__ import with_statement

from flask import (Blueprint, send_from_directory, render_template,
                   _app_ctx_stack, abort, url_for)
from jinja2 import contextfunction
from jinja2.loaders import TemplateNotFound

from theme import Theme, ThemeTemplateLoader
from theme_manager import ThemeManager


try:
    from flask.ext.assets import Environment, Bundle
except:
    pass

containable = lambda i: i if hasattr(i, '__contains__') else tuple(i)

def get_theme(ident):
    """
    This gets the theme with the given identifier from the current app's
    theme manager.

    :param ident: The theme identifier.
    """
    ctx = _app_ctx_stack.top
    return ctx.app.theme_manager.themes[ident]


def get_themes_list():
    """
    This returns a list of all the themes in the current app's theme manager,
    sorted by identifier.
    """
    ctx = _app_ctx_stack.top
    return list(ctx.app.theme_manager.list_themes)


def template_exists(templatename):
    ctx = _app_ctx_stack.top
    return templatename in containable(ctx.app.jinja_env.list_templates())


def active_theme(ctx):
    if '_theme' in ctx:
        return ctx['_theme']
    elif ctx.name.startswith('_themes/'):
        return ctx.name[8:].split('/', 1)[0]
    else:
        raise RuntimeError("Could not find the active theme")


def static_file_url(theme, filename, external=False):
    """
    This is a shortcut for getting the URL of a static file in a theme.

    :param theme: A `Theme` instance or identifier.
    :param filename: The name of the file.
    :param external: Whether the link should be external or not. Defaults to
                     `False`.
    """
    if isinstance(theme, Theme):
        theme = theme.identifier
    return url_for('_themes.static', themeid=theme, filename=filename,
                   _external=external)


@contextfunction
def global_theme_template(ctx, templatename, fallback=True):
    theme = active_theme(ctx)
    templatepath = '_themes/{}/{}'.format(theme, templatename)
    if (not fallback) or template_exists(templatepath):
        return templatepath
    else:
        return templatename


@contextfunction
def global_theme_static(ctx, filename, external=False):
    theme = active_theme(ctx)
    return static_file_url(theme, filename, external)


def render_theme_template(theme, template_name, _fallback=True, **context):
    """
    This renders a template from the given theme. For example::

        return render_theme_template(g.user.theme, 'index.html', posts=posts)

    If `_fallback` is True and the themplate does not exist within the theme,
    it will fall back on trying to render the template using the application's
    normal templates. (The "active theme" will still be set, though, so you
    can try to extend or include other templates from the theme.)

    :param theme: Either the identifier of the theme to use, or an actual
                  `Theme` instance.
    :param template_name: The name of the template to render.
    :param _fallback: Whether to fall back to the default
    """
    if isinstance(theme, Theme):
        theme = theme.identifier
    context['_theme'] = theme
    try:
        return render_template('_themes/{}/{}'.format(theme, template_name),
                               **context)
    except TemplateNotFound:
        if _fallback:
            return render_template(template_name, **context)
        else:
            raise

class Fleem(object):
    """
    :param app: The `~flask.Flask` instance to set up themes for.
    :param loaders: An iterable of loaders to use. It defaults to
                    `packaged_themes_loader` and `theme_paths_loader`.
    :param app_identifier: The application identifier to use. If not given,
                        it defaults to the app's import name.
    :param manager_cls: If you need a custom manager class, you can pass it
                        in here.
    :param theme_url_prefix: The prefix to use for the URLs on the themes
                            module. (Defaults to ``/_themes``.)
    """
    def __init__(self, app=None,
                       loaders=None,
                       app_identifier=None,
                       manager_cls=ThemeManager,
                       theme_manager=None,
                       theme_url_prefix="/_themes"):
        self.loaders = loaders
        self.app_identifier = app_identifier
        self.manager_cls = manager_cls
        self.theme_manager = theme_manager
        self.theme_url_prefix = theme_url_prefix

        if app is not None:
            self.app = app
            self.init_app(self.app,
                          self.app_identifier,
                          self.manager_cls,
                          self.loaders)
        else:
            self.app = None

        if Environment and Bundle:
            if self.app:
                self.packaging = True
                self.theming_assets = Environment(self.app)


    def init_app(self, app, app_identifier, manager_class, loaders):
        if app_identifier is None:
            self.app_identifier = app.import_name
        self.theme_manager = manager_class(app, self.app_identifier, loaders=loaders)
        app.jinja_env.globals['theme'] = global_theme_template
        app.jinja_env.globals['theme_static'] = global_theme_static
        app.register_blueprint(self._blueprint, url_prefix=self.theme_url_prefix)


    @property
    def _blueprint(self):
        themes_blueprint = Blueprint('_themes', __name__, url_prefix='/_themes')
        themes_blueprint.jinja_loader
        themes_blueprint.jinja_loader = ThemeTemplateLoader()
        def static(themeid, filename):
            try:
                ctx = _app_ctx_stack.top
                theme = ctx.app.theme_manager.themes[themeid]
            except KeyError:
                abort(404)
            return send_from_directory(theme.static_path, filename)
        themes_blueprint.add_url_rule('/<themeid>/<path:filename>', 'static', view_func=static)
        return themes_blueprint

    def register_theme_css(self, theme):
        pass#manifest, bundle = self.return_bundle('css', theme_name, 'cssmin')

    def register_theme_js(self, theme):
        pass#manifest, bundle = self.return_bundle('js', theme_name, 'rjsmin')

    def query_manager(self, query):
        return getattr(self.manager_cls, query)

    @property
    def themes(self):
        return self.query_manager('themes')

    @property
    def list_themes(self):
        return self.query_manager('list_themes')

    @property
    def list_loaders(self):
        return self.query_manager('loaders')

    @property
    def refresh_themes(self):
        return self.query_manager('refresh')()

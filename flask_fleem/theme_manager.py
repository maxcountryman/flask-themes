from itertools import chain
from operator import attrgetter
import os
import re
from time import time
from theme import Theme
from flask import current_app
from flask.ext.assets import Environment
from webassets.env import RegisterError

IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def starchain(i):
    return chain(*i)


def list_folders(path):
    """
    This is a helper function that only returns the directories in a given
    folder.

    :param path: The path to list directories in.
    """
    return (name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name)))


def load_themes_from(path):
    """
    This is used by the default loaders. You give it a path, and it will find
    valid themes and yield them one by one.

    :param path: The path to search for themes in.
    """
    for basename in (b for b in list_folders(path) if IDENTIFIER.match(b)):
        try:
            t = Theme(os.path.join(path, basename))
        except:
            pass
        else:
            if t.identifier == basename:
                yield t


def packaged_themes_loader(app):
    """
    This theme will find themes that are shipped with the application. It will
    look in the application's root path for a ``themes`` directory - for
    example, the ``someapp`` package can ship themes in the directory
    ``someapp/themes/``.
    """
    themes_path = os.path.join(app.root_path, 'themes')
    if os.path.exists(themes_path):
        return load_themes_from(themes_path)
    else:
        return ()


def theme_paths_loader(app):
    """
    This checks the app's `THEME_PATHS` configuration variable to find
    directories that contain themes. The theme's identifier must match the
    name of its directory.
    """
    theme_paths = app.config.get('THEME_PATHS', ())
    if isinstance(theme_paths, basestring):
        theme_paths = [p.strip() for p in theme_paths.split(';')]
    return starchain(
        load_themes_from(path) for path in theme_paths
    )


class ThemeManager(object):
    """
    This is responsible for loading and storing all the themes for an
    application. Calling `refresh` will cause it to invoke all of the theme
    loaders.

    A theme loader is simply a callable that takes an app and returns an
    iterable of `Theme` instances. You can implement your own loaders if your
    app has another way to load themes.

    :param app: The app to bind to. (Each instance is only usable for one
                app.)
    :param app_identifier: The value that the info.json's `application` key
                           is required to have. If you require a more complex
                           check, you can subclass and override the
                           `valid_app_id` method.
    :param loaders: An iterable of loaders to use. The defaults are
                    `packaged_themes_loader` and `theme_paths_loader`, in that
                    order.
    """
    def __init__(self, app, app_identifier, loaders=None):
        self.app = app
        self.app_identifier = app_identifier
        self._themes = None
        self.loaders = []
        if loaders:
            self.loaders.extend(loaders)
        else:
            self.loaders.extend((packaged_themes_loader, theme_paths_loader))
        self.asset_env = Environment(self.app)
        self.refresh()


    @property
    def themes(self):
        """
        This is a dictionary of all the themes that have been loaded. The keys
        are the identifiers and the values are `Theme` objects.
        """
        if self._themes is None:
            self.refresh()
        return self._themes


    @property
    def list_themes(self):
        """
        This yields all the `Theme` objects, in sorted order.
        """
        return sorted(self.themes.itervalues(), key=attrgetter('identifier'))


    def valid_app_id(self, app_identifier):
        """
        This checks whether the application identifier given will work with
        this application. The default implementation checks whether the given
        identifier matches the one given at initialization.

        :param app_identifier: The application identifier to check.
        """
        return self.app_identifier == app_identifier

    def register_theme_assets(self):
        f = open(os.path.join(self.app.static_folder, "{}.manifest".format(self.app_identifier)), 'a')
        extensions_filters = {'.css': 'cssmin', '.js': 'rjsmin'}
        for t in self.list_themes:
            for k,v in extensions_filters.iteritems():
                manifest_entry, bundle = t.return_bundle(k,v)
                f.write("{} :: {}\n".format(time(), str(manifest_entry)))
                if bundle:
                    try:
                       self.asset_env.register("{}_{}".format(t.identifier, k[1:]), bundle)
                    except RegisterError, e:
                        raise e

    def refresh(self):
        """
        This loads all of the themes into the `themes` dictionary. The loaders
        are invoked in the order they are given, so later themes will override
        earlier ones. Any invalid themes found (for example, if the
        application identifier is incorrect) will be skipped.
        """
        self._themes = {}
        for theme in starchain(ldr(self.app) for ldr in self.loaders):
            if self.valid_app_id(theme.application):
                self.themes[theme.identifier] = theme
        self.register_theme_assets()

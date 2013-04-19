import os
from flask import json, current_app, _app_ctx_stack
from jinja2.loaders import FileSystemLoader, BaseLoader, TemplateNotFound
from werkzeug import cached_property, LocalProxy
from flask.ext.assets import Bundle

_fleem = LocalProxy(lambda: current_app.extensions['fleem_manager'])

class Theme(object):
    """
    This contains a theme's metadata.

    :param path: The path to the theme directory.
    """
    def __init__(self, path):
        #: The theme's root path. All the files in the theme are under this
        #: path.
        self.path = os.path.abspath(path)

        with open(os.path.join(self.path, 'info.json')) as fd:
            self.info = i = json.load(fd)

        #: The theme's name, as given in info.json. This is the human
        #: readable name.
        self.name = i['name']

        #: The application identifier given in the theme's info.json. Your
        #: application will probably want to validate it.
        self.application = i['application']

        #: The theme's identifier. This is an actual Python identifier,
        #: and in most situations should match the name of the directory the
        #: theme is in.
        self.identifier = i['identifier']

        #: The human readable description. This is the default (English)
        #: version.
        self.description = i.get('description', "None")

        #: This is a dictionary of localized versions of the description.
        #: The language codes are all lowercase, and the ``en`` key is
        #: preloaded with the base description.
        self.localized_desc = dict(
            (k.split('_', 1)[1].lower(), v) for k, v in i.items()
            if k.startswith('description_')
        )
        self.localized_desc.setdefault('en', self.description)

        #: The author's name, as given in info.json. This may or may not
        #: include their email, so it's best just to display it as-is.
        self.author = i['author']

        #: A short phrase describing the license, like "GPL", "BSD", "Public
        #: Domain", or "Creative Commons BY-SA 3.0".
        self.license = i.get('license')

        #: A URL pointing to the license text online.
        self.license_url = i.get('license_url')

        #: The URL to the theme's or author's Web site.
        self.website = i.get('website')

        #: The theme's preview image, within the static folder.
        self.preview = i.get('preview')

        #: The theme's doctype. This can be ``html4``, ``html5``, or ``xhtml``
        #: with html5 being the default if not specified.
        self.doctype = i.get('doctype', 'html5')

        #: Any additional options. These are entirely application-specific,
        #: and may determine other aspects of the application's behavior.
        self.options = i.get('options', {})

    def theme_files_of(self, extension):
        lf = []
        extension_absolute = extension[1:]
        if os.path.exists(self.static_path):
            lf.extend([os.path.join(self.path, fname) for fname \
                       in os.listdir(self.static_path) \
                       if os.path.splitext(fname)[-1] == extension])
        if os.path.exists(os.path.join(self.static_path, extension_absolute)):
            lf.extend([os.path.join(self.path, fname) for fname \
                       in os.listdir(os.path.join(self.static_path, extension_absolute)) \
                       if os.path.splitext(fname)[-1] == extension])
        return lf

    def return_bundle(self, extension, resource_filter):
        resource_tag = "theme-{}-packed{}".format(self.identifier, extension)
        resources = self.theme_files_of(extension)
        if resources:
            manifest = "{} for theme {} == {}".format(extension, self.name, [r for r in resources])
            return manifest, Bundle(*resources, output=resource_tag, filters=resource_filter)
        else:
            return "No {} resources for {}".format(extension, self.name), None


    @cached_property
    def static_path(self):
        """
        The absolute path to the theme's static files directory.
        """
        return os.path.join(self.path, 'static')

    @cached_property
    def templates_path(self):
        """
        The absolute path to the theme's templates directory.
        """
        return os.path.join(self.path, 'templates')

    @cached_property
    def license_text(self):
        """
        The contents of the theme's license.txt file, if it exists. This is
        used to display the full license text if necessary. (It is `None` if
        there was not a license.txt.)
        """
        lt_path = os.path.join(self.path, 'license.txt')
        if os.path.exists(lt_path):
            with open(lt_path) as fd:
                return fd.read()
        else:
            return None

    @cached_property
    def jinja_loader(self):
        """
        This is a Jinja2 template loader that loads templates from the theme's
        ``templates`` directory.
        """
        return FileSystemLoader(self.templates_path)

    def __repr__(self):
        return "<Theme object | name: {} | application_identifier: {} | identifier: {} >".format(self.name, self.application, self.identifier)


class ThemeTemplateLoader(BaseLoader):
    """
    This is a template loader that loads templates from the current app's
    loaded themes.
    """
    def __init__(self):
        BaseLoader.__init__(self)

    def get_source(self, environment, template):
        template = template[8:]
        try:
            themename, templatename = template.split('/', 1)
            theme = _fleem.themes[themename]
        except (ValueError, KeyError):
            raise TemplateNotFound(template)
        try:
            return theme.jinja_loader.get_source(environment, templatename)
        except TemplateNotFound:
            raise TemplateNotFound(template)

    def list_templates(self):
        res = []
        for ident, theme in _fleem.themes.iteritems():
            res.extend(('_themes/{}/{}'.format(ident, t)).encode("utf8")
                       for t in theme.jinja_loader.list_templates())
        return res

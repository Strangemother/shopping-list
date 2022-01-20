

from jinja2 import (Environment, PackageLoader, ChoiceLoader, FileSystemLoader,
    select_autoescape, Template)

from pathlib import Path
import sys

HERE = Path(__file__).parent
sys.path.append(HERE.as_posix())

import markdown

class JinjaEnvLoaders(object):

    def get_loaders(self):
        names = self.config.get_template_locations()
        fls = tuple(FileSystemLoader(*x) for x in names)
        print('Generating', names)
        return fls

    def gen_env(self):
        fls = self.get_loaders()
        env = Environment(
            loader=ChoiceLoader(fls),
            autoescape=select_autoescape()
        )
        return env


class RenderBase(JinjaEnvLoaders):
    """Convert an expensive config dict into a html file."""
    def __init__(self, config=None):
        if config:
            self.setup(config)

    def setup(self, config):
        self.config = config
        self.env = self.gen_env()

    def get_template_filename(self, name):
        """Given a name, return the template from the existing environment
        and its template location.

            get_template('index.html')
        """
        return 'page.html'

    def render(self, filename, data_store=None, template=None):
        """Expecting the internal dictionaries to be resolved, render the final
        output HTML.
        """
        data_store = data_store or {'filename': filename}
        # first render, may include {{vars}}.
        md_html = self.render_markdown(filename, data_store)
        data_store.setdefault('rendered_content', md_html)

        self.stash_render_template_name(data_store, filename, template)
        html = self.render_html(filename, data_store, template=template)
        data_store.setdefault('rendered_html', html)
        return html

    def render_markdown(self, filename, data_store):
        return self.render_markdown_text(data_store['content'])

    def render_markdown_text(self, text):
        """

            Extension               Entry Point Dot Notation
            Extra   extra                       markdown.extensions.extra
                Abbreviations       abbr        markdown.extensions.abbr
                Attribute Lists     attr_list   markdown.extensions.attr_list
                Definition Lists    def_list    markdown.extensions.def_list
                Fenced Code Blocks  fenced_code markdown.extensions.fenced_code
                Footnotes           footnotes   markdown.extensions.footnotes
                Markdown in HTML    md_in_html  markdown.extensions.md_in_html
                Tables              tables      markdown.extensions.tables
            Admonition              admonition  markdown.extensions.admonition
            CodeHilite              codehilite  markdown.extensions.codehilite
            Legacy Attributes       legacy_attrs markdown.extensions.legacy_attrs
            Legacy Emphasis         legacy_em   markdown.extensions.legacy_em
            Meta-Data               meta        markdown.extensions.meta
            New Line to Break       nl2br       markdown.extensions.nl2br
            Sane Lists              sane_lists  markdown.extensions.sane_lists
            SmartyPants             smarty      markdown.extensions.smarty
            Table of Contents       toc         markdown.extensions.toc
            WikiLinks               wikilinks   markdown.extensions.wikilinks
        """
        extensions = [
            'extra',
            'admonition',
            'codehilite',
            'meta',
            'sane_lists',
            'smarty',
            'toc',
            'wikilinks',
        ]

        return markdown.markdown(text, extensions=extensions)

    def stash_render_template_name(self, data_store, filename=None, template=None):
        # Get and restore the base template name
        # (A loop through in case of reactive items.)
        filename = filename or data_store['filename']
        base_name = template or self.get_template_filename(filename)
        data_store.setdefault('base_template_name', base_name)
        # return data_store.get('base_template_name')
        return base_name

    def render_html(self, filename, data_store, template=None):
        bn = data_store.get('base_template_name')
        return self.env.get_template(bn).render(data_store)


class JinjaMarkdownEnvLoaders(object):
    """Provide methods to create a Jinja environment targeting the markdown file-set
    This is a replica of the standard site _(html)_ jinja env, but pointing to
    a special markdown/ template directory.
    """

    def gen_markdown_env(self):
        """Create a new jina Environment, with loaders specific to the markdown
        templates.
        """
        fls = self.get_markdown_loaders()
        env = Environment(
            loader=ChoiceLoader(fls),
            autoescape=select_autoescape()
        )
        return env

    def get_markdown_loaders(self):
        names = self.config.get_markdown_template_locations()
        fls = tuple(FileSystemLoader(*x) for x in names)
        print('Generating', names)
        return fls


class RecursiveMarkdownTemplate(RenderBase, JinjaMarkdownEnvLoaders):
    def setup(self, config):
        super().setup(config)
        self.markdown_env = self.gen_markdown_env()

    def get_markdown_template_filename(self, filename):
        """Return the target markdown template, found within one of the asset
        directories [assets]/markdown/default.mdt

        Generally the library will utilise the ".mdt" (markdown template)
        extension. The content of this file may be as little as:

            {{ content }}

        being the `data_store['content']` value,
        """
        return 'default.mdt'

    def render_markdown(self, filename, data_store):
        """Called by the parent execution, extend the markdown renderer
        to _template_ a given markdown. Override The default to inject a
        template syntax

        The default functionality accepts the content and returns the HTML:

            return markdown.markdown(data_store['content'])

        However this is replaced with:

        1. Set the base_markdown_template_name,
        2. render the markdown file, into a _rendered markdown file_
        3. store into 'content' for later.

        This markdown file will proceed through a _last stage variable renderer_
        before injection to the site HTML as an include variable.
        """
        # Get base file
        base_name = self.get_markdown_template_filename(filename)
        data_store.setdefault('base_markdown_template_name', base_name)

        base_md_name = data_store.get('base_markdown_template_name')
        # the result is a markdown file, with any template parts injecting
        # markdown or _next render_ statements.
        new_md = self.markdown_env.get_template(base_md_name).render(data_store)

        # The new markdown (as finished html) is applied as a variable to
        # the templating lib but is not _templated_, still containing {{vars}}
        # They should be replaced with the same data_store used for the HTML.
        ## Currently, retemplate here given the _new md_, and returning
        # _finished md_.

        ## For now, pollute the original location, but this should change
        #to a seperate key and some flag to present which key is the final.
        data_store['content'] = new_md

        # Call to the original function, yielding HTML but with the _above_
        # changes in-place
        # html = super().render_markdown(filename, data_store)
        # return html

        # As the above will be altered before the final render,
        # we don't return the `render_content` result here -
        return None
        # return markdown.markdown(data_store['content'])

    def render_html(self, filename, data_store, template=None):

        ## The 'content' represents the _above_ `render_markdown` result.
        # Generate a new template given the _old_ markdown text
        # and render the markdown with the same data_store.
        # Apply this back into the `rendered_content`, knowing the html bound for
        # the {{ rendered_content }} attribute does not have any untemplated
        # {{vars}}

        content_md = data_store['content']
        # re-render the content through the last-stage MD templating env
        new_templ = Template(content_md)
        new_md = new_templ.render(data_store)
        # Render back into the data store
        md_html = self.render_markdown_text(new_md)
        data_store['rendered_content'] = md_html

        # Call back to the original, of which will render the `render_content`
        # in the normal manner.
        return super().render_html(filename, data_store, template)


class RenderUnit(RecursiveMarkdownTemplate):
    pass

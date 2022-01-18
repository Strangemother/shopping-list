

from jinja2 import (Environment, PackageLoader, ChoiceLoader, FileSystemLoader,
    select_autoescape, Template)

from pathlib import Path
import sys

HERE = Path(__file__).parent
sys.path.append(HERE.as_posix())

import markdown

class RenderBase(object):
    """Convert an expensive config dict into a html file."""
    def __init__(self, config=None):

        if config:
            self.setup(config)

    def setup(self, config):
        self.config = config
        self.env = self.gen_env()

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

        md_html = self.render_markdown(filename, data_store)
        data_store.setdefault('rendered_content', md_html)

        self.stash_render_template_name(data_store, filename, template)
        html = self.render_html(filename, data_store, template=template)
        data_store.setdefault('rendered_html', html)
        return html

    def render_markdown(self, filename, data_store):
        return self.render_markdown_text(data_store['content'])

    def render_markdown_text(self, text):
        return markdown.markdown(text)

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


class RecursiveMarkdownTemplate(RenderBase):
    def setup(self, config):
        super().setup(config)
        self.markdown_env = self.gen_markdown_env()

    def gen_markdown_env(self):
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
        """Extend the markdown renderer to _template_ a given markdown.

        The default functionality accepts the content and returns the HTML:

            return markdown.markdown(data_store['content'])

        Override this to inject a template syntax
        """
        # Get base file
        base_name = self.get_markdown_template_filename(filename)
        data_store.setdefault('base_markdown_template_name', base_name)

        bn = data_store.get('base_markdown_template_name')
        # the result is a markdown file, with any template parts injecting
        # markdown or _next render_ statements.
        new_md = self.markdown_env.get_template(bn).render(data_store)

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

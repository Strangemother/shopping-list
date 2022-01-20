import markdown
import unicodedata, re
from pathlib import Path


class Utility(object):
    name = None

    def __init__(self, config):
        self.config = config
        print('New util', self)

    def prepare(self):
        """Collect phase runs before other function
        """
        pass

    def preprocess(self):
        for fullpath in self.config.all_files:
            self.preprocess_path(fullpath)


    def postprocess(self, depth=-1):
        for fullpath in self.config.all_files:
            self.postprocess_path(fullpath)

    def preprocess_path(self, path):
        """Called by preprocess upon each full path within the all_files list"""
        pass

    def postprocess_path(self, path):
        pass

    def finalize_content(self):
        """Last stage of any changes before the system produces indexes.
        """
        pass

    def plug_holes(self):
        """All Changes are done, the references are frozen. Create any additional
        files and write to the data_store and index.
        """
        pass

    def build_indexes(self):
        """read the (now frozen) file cache for all referenable units and
        write the index files such as the sitemap list of all references.

        Noting and "index.html" files will have been generated during the
        _plug_holes_ phase but may need a finished references of these indexes
        of files.
        """
        pass

    def render_out(self, renderer):
        """Called by the Config unit as the last stage rendering after
        all indexing is complete. Given a renderer class, generate output
        content and push into the data_store.
        """
        pass

    def write_all(self, writer):
        """Write data out to the given Writer unit.
        """
        pass


class Printer(Utility):
    """An example utility to _print_ the outbound file during iteration.
    """
    name = 'printer'

    def prepare(self):
        self.root_path = self.config.get_root_path()

    def _preprocess_path(self, path):
        p = path
        if self.config.docs.printer.relative is not False:
            p = p.relative_to(self.root_path)
        print('   ', p)


class RenderFilesUtility(Utility):
    """A Generic "file handler" utility, providing the function method
    `render_file` - called when the `render` phase.
    """
    def get_root_output_dirs(self):
        """Return a list of root directories the output file should be applied.
        """
        return [self.config.get_output_dir()]

    def get_destination_paths(self, file):
        """Multiple output destination directories are allowed. In the top of
        the markdown, add an array of destination_dirs.
        This may be coupled with a separate destination_filename. The output
        directory cannot change and is collected from the self.config.

            title: another
            destination_dirs: other/foo/
                              egg/butter
            ---
            # Hello
        """
        data_store = self.config.get_store(file)

        dest_fn = data_store.get('destination_filename', None)
        if dest_fn is None:
            dest_fn = file.name

        meta = data_store.get('meta') or {}
        dest_dirs = meta.get('destination_dirs', None)

        if dest_dirs is None:
            dest_dirs = (Path(''),)
            rp = self.config.get_root_path()
            dest_dirs = (file.relative_to(rp).parent, )

        destinations = ()
        rel_destinations = ()

        # Iterate all outbound root sites, all directories.
        # and the filename
        output_dirs = self.get_root_output_dirs()
        for output_dir in output_dirs:
            for d_dir in dest_dirs:
                out_path = output_dir / d_dir / dest_fn
                rel_out_path =  d_dir / dest_fn
                destinations += (out_path, )
                rel_destinations += (rel_out_path, )

        return (rel_destinations, destinations,)

    def render_out(self, renderer):
        self.render_files(renderer)

    def get_files(self):
        return self.config.all_files
        # return self.files

    def render_files(self, renderer):
        print('Render out', self)
        for filename in self.get_files():
            # for filename, data in self.config._parent.storage.items():
            data = self.config.get_store(filename)
            is_file = data.get('is_file', False) is True
            if is_file:
                self.render_file(filename, data, renderer)

    def render_file(self, filename, data_store, renderer):
        pass


class General(RenderFilesUtility):
    """The _General_ free tool incorporating most of the markdown parsing.
    """
    name = 'general'

    def preprocess(self):
        self.root_path = self.config.get_root_path()
        self.files = ()
        super().preprocess()

    def get_files(self):
        return self.files

    def preprocess_path(self, path):
        if path.is_file():
            fp = self.preprocess_file(path)
            if fp is None:
                return
            self.files += (fp,)

    def preprocess_file(self, path):

        if path.suffix not in ('.md',):
            return

        try:
            content = path.read_text()
        except ValueError:
            print('Error Reading', path)
            return

        meta = self.extract_meta(content)
        data_store = self.config.get_store(path)
        data_store['is_file'] = True
        data_store['content'] = content
        data_store['meta'] = meta
        data_store['rel_filename'] = path.relative_to(self.root_path)

        return path

    def extract_meta(self, content):
        """<markdown.core.Markdown object at 0x0000000003783C50>
        >>> dd=md.Markdown(extensions=['meta'])
        >>> dd.convert
        <bound method Markdown.convert of <markdown.core.Markdown object at 0x0000000003783400>>
        >>> dd.convert(content)
        '<h1>Hello</h1>\n<p>This is another file, with "another" as the title.</p>'
        >>> dd.Meta
        {'title': ['another']}
        >>>"""

        ## Pretty wasteful but is required to pre-render the name etc...
        mdr = markdown.Markdown(extensions=['meta'])
        d = mdr.convert(content)
        return mdr.Meta

    def render_file(self, filename, data_store, renderer):
        # data == data_store = self.config.get_store(filename)
        # p = filename
        # if self.config.docs.printer.relative is not False:
        #     p = p.relative_to(self.root_path)
        data_store['filename'] = filename
        data_store['rendered_content'] = renderer.render(filename, data_store)

    def postprocess_path(self, path):
        self.push_title(path)

    def push_title(self, path):
        """Discover the "title" of this page and push into the data store.
        used for index names and page <title/> attributes.

        The title may come from:

        + file meta data
        + the filename
        + some external index.
        """
        data_store = self.config.get_store(path)
        filename = data_store.get('filename', None) or path
        meta = data_store.get('meta', {})
        title = meta.get('title', None) or Path(filename).stem

        if isinstance(title, (list, tuple)):
            title = ' '.join(title)
        data_store['title'] = title


class Writer(RenderFilesUtility):
    """The Writer class acts as a last-stage utility, converting the in-memory
    file content to a directory of html files; a "site".

    This hooks the `write_all` api method
    """

    def get_files(self):
        general = self.config.get_utils().get('general')
        if general is None:
            print('Writer utility cannot locate the "general" utility')
            return tuple(x for x in self.config.all_files if x.is_file())

        return general.files

    def postprocess_path(self, path):
        """Store the destination after the and cross referencing
        but before the _render_.
        """
        data_store = self.config.get_store(path)
        if data_store.get('is_file', False) is False:
            return

        destination = self.get_destination_filname(path, data_store)
        data_store.setdefault('destination_filename', destination)

    def render_file(self, filename, data_store, renderer):
        """Called by the parent during the 'render_files' loop, during the
        render out phase.

        Use the 'destination_filename', previously applied in the 'post_process'
        phase - and likely amended before this step.

        """
        destination = data_store['destination_filename']
        fn = str(data_store['rel_filename'])
        print(f"{fn:<50}, {destination}")

    def get_destination_filname(self, path, data_store):
        """Return the relative output filepath of the file."""

        meta = data_store['meta']
        # From the top of the file.
        meta_dest_name = meta.get('destination_filename')

        # from the generic conf
        dest_name = meta.get('destination_filename')
        # the real filename.
        rel_name = data_store['rel_filename']
        rel_path = dest_name or rel_name

        # convert to a HTML name.
        # "my filename.md" -> "my_filename.html"
        out_path = rel_path.with_name(slugify(rel_path.stem)).with_suffix('.html')

        return out_path

    def write_all(self, writer):
        """given a ready writer class generate all the finished files."""
        # self.output_dir = self.config.get_output_dir()
        files = self.get_files()
        print(f'Writing {len(files)} files')
        for file in files:
            self.write_file(file, writer, files)

    def finalize_content(self,):
        """Store the 'destination_paths' within the datastore.

        This is done at the last stage before automation.
        """
        files = self.get_files()
        for file in files:
            data_store = self.config.get_store(file)
            data_store['destination_paths'] = self.get_destination_paths(file)

    def write_file(self, file, writer, files):
        print(  'write_file', file)
        data_store = self.config.get_store(file)
        rel_dests, destinations = self.get_destination_paths(file)
        text = data_store.get('rendered_content', file.as_posix())
        return self.write_text_to_destinations(destinations, text)

    def write_text_to_destinations(self, destinations, text):
        for out_path in destinations:
            if out_path.suffix != '':
                self.write_text_to_path(text, out_path)

    def write_text_to_path(self, text, out_path, make_parents=True):
        print('Write:', out_path)
        if make_parents is True and (out_path.parent.exists() is False):
            out_path.parent.mkdir(parents=True)
        try:
            out_path.write_text(text)
        except Exception as exc:
            import pdb; pdb.set_trace()  # breakpoint 0bd088c2x //
            print(exc)

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
    # return mark_safe(re.sub('[-\s]+', '-', value))
    #slugify = allow_lazy(slugify, six.text_type)

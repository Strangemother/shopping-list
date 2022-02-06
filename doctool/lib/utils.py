import markdown
import unicodedata, re
from pathlib import Path
from collections import defaultdict


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

        dest_fn = self.get_dest_filename(file)

        meta = data_store.get('meta') or {}
        dest_dirs = self.get_dest_dirs(file)

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

    def get_dest_dirs(self, file):
        """Get from

        1. meta
            destination_dirs
        2. else, path relative to the config root
        """
        data_store = self.config.get_store(file)
        meta = data_store.get('meta') or {}
        dest_dirs = meta.get('destination_dirs', None)

        if dest_dirs is None:
            dest_dirs = (Path(''),)
            rp = self.config.get_root_path()
            dest_dirs = (file.relative_to(rp).parent, )

        return dest_dirs

    def get_dest_filename(self, file):
        '''Return the filename for this file given all config options available.
        This occurs before the indexes changes (before finalising file tree)

        1. from the datastore
        2. The .md file name
        3. the meta:
            destination_filename
        '''
        data_store = self.config.get_store(file)

        dest_fn = data_store.get('destination_filename', None)
        if dest_fn is None:
            dest_fn = file.name

        meta = data_store.get('meta') or {}
        destination_filenames = meta.get('destination_filename', None)
        destination_filename = None

        if destination_filenames is not None:
            destination_filename = destination_filenames[0]

        # meta data first, then filename, then datastore
        return destination_filename or dest_fn

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
        data_store['name'] = meta.get('name',[path.name])[0]

        words = ()
        for line in meta.get('tags', ()):
            _t = line.split(',')
            words += tuple(map(str.strip, _t))

        data_store['tags'] = data_store.get('tags', ()) + words

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
        """given a ready writer class generate all the finished files.

        A list of all files from the config:
            files = self.get_files()

        All files in the tree:
            tree = self.out_tree

        """
        # self.output_dir = self.config.get_output_dir()

        ## Instead of the original files, use the new out_tree.
        tree = self.out_tree
        files = self.get_files()

        for key_path, tree_item in tree.items():
            # Merge the tree entity with the
            # file unit.
            if tree_item.is_file:
                self.write_file(tree_item.filepath, writer, files)

        # print(f'Writing {len(files)} files')
        # for file in files:
        #     self.write_file(file, writer, files)

    def finalize_content(self,):
        """Store the 'destination_paths' within the datastore.

        This is done at the last stage before automation.
        """
        files = self.get_files()
        for file in files:
            data_store = self.config.get_store(file)
            rel_dests, destinations = self.get_destination_paths(file)
            # data_store['destination_abs_paths'] = destinations
            # data_store['destination_rel_paths'] = rel_dests

    def build_indexes(self):

        tree = self.recurse_tree(self.config)
        self.plug_file_tree(tree)
        self.file_tree = tree
        self.out_tree = self.generate_out_tree()

    def plug_file_tree(self,tree):
        """Alter the internal file tree to include generated files and renames.

        To do so, the file writer will iterate the out_tree and write
        every file in the index, taggedd against the target object

        Change README
        (root) index file
        sitemap index
        inject 'index' to empty directories

        if "folder mode" all files change to /[filename]/index.html
            testing for collisions.
        """
        # first do any renames,
        # README -> index etc
        #
        # if no index or readme, (and not folder mode)
        #   a new index file.
        # Apply missing index files.
        # add sitemap contents; master doc
        for key_path, item in tree.items():
            file = item.filepath
            data_store = self.config.get_store(file)
            if item.is_dir:
                # Produce a clean lower version
                flat_names = ()
                for name in item.files:
                    flat_names += ( str(Path(name).with_suffix('')).lower(), )

                print('Is dir - check for index.')
                # Ensure it has an index.
                if ('index' in flat_names) is False:
                    # rename the README
                    if 'readme' in flat_names:
                        # move
                        print('move existing readme')

                    else:
                        # create new
                        print('inject new file')

            if item.is_file:
                print('is file.')

        print('plug_file_tree')

    def generate_out_tree(self):
        """Build the output index for the writer, utilising the generated file tree.

        At this point the files are plugged. Injecy any data to the renderable
        object - ready for the final html generation.
        """
        print('generate_out_tree')
        return self.file_tree

    def recurse_tree(self, config):
        """Loop all files,
        ensure a directory structure for final leaves."""
        ## TODO!
        refs = defaultdict(dict)
        self.file_flats = defaultdict(set)
        self.dir_flats = defaultdict(set)

        self.r_tree = {}#defaultdict(TreeItem)

        self.r_tree[()] = TreeItem(**{
            'root': True,
            'depth': -1,
            # 'child_count':0,
            'type': 'dir',
            'filepath': Path('.'),
            'item': '.',
            'name': 'root',
        })

        for i, file in enumerate(self.get_files()):
            # Write a reference 'dir structure'
            self.grab_file(file, i)
        self.print_tree()
        return self.r_tree

    def print_tree(self):
        for k, v in self.r_tree.items():
            l = f'{str(k):<70} {v}'
            print(l)

    def grab_file(self, file, index):
        g = self.r_tree
        ref_id = index

        # host = self.config.get_host_path()
        root_path = self.config.get_root_path()
        rel_path = file.relative_to(root_path)
        parts = rel_path.parts
        tl = len(parts)
        counter = 0

        for i, current_node in enumerate(parts):
            # From top down, create the content required.
            path = parts[0:i+1]
            # if len(path) == 0:
            # the very _root_ of the work, likely a dir..
            node = g.get(path, None)
            is_file = tl == len(path)
            if node is None:
                node = {
                    'type': 'file' if is_file else 'dir',
                    'depth': len(path),
                    # 'child_count': -1,
                    'filepath': Path(*path),
                    'item': path,
                    'name': path[-1],
                    # 'children': set()
                }
                g[path] = TreeItem(**node)

            ppath = tuple(Path(*path).parent.parts)
            parent = g.get(ppath, None)
            if parent is None:
                # build.
                parent = TreeItem(
                                type='dir',
                                depth=len(ppath),
                                item=ppath,
                                name=ppath[-1],
                            )
                g[ppath] = parent
                print('created', ppath, parent)

            parent.children.add(current_node)
            if is_file:
                parent.files.add(current_node)

            # parent.child_count += 1

    def grab_file_leaf_up(self, file, index):
        """
        introduce a file into the graph reference, starting at the _end_ (leaf)
        of a given path and stepping _up_ to the root.

        Note. This isn't the best; It's better to walk top-down
        """
        g = self.r_tree
        ref_id = index
        # host = self.config.get_host_path()
        root_path = self.config.get_root_path()
        rel_path = file.relative_to(root_path)
        parts = rel_path.parts
        tl = len(parts)
        counter = 0

        g[rel_path.parts] = {
                'out_path': rel_path,
                'parent_path': rel_path.parent,
                'type': 'file',
                'child_count': -1,
                'ref_id': ref_id,
                'write': True,
            }

        upstack = parts
        # Stack backward from the file to root
        while len(upstack) > 1:
            counter+=1
            upstack = parts[:tl-counter]
            print('upstack', upstack)
            parent = g.get(upstack, None)
            if parent is None:
                parent = {
                    'type': 'directory',
                    'child_count': 0,
                    'children': set()
                }
            # if counter == 1:
            parent['child_count'] += 1
            parent['children'].add(upstack[-1])
            g[upstack] = parent
        # Add a count of the name
        self.file_flats[file.name].add(ref_id)
        # add a count of the parent (children.)
        self.dir_flats[rel_path.parent.parts].add(ref_id)

    def write_file(self, file, writer, files):
        print(  'write_file', file)
        data_store = self.config.get_store(file)
        # rel_dests, destinations = self.get_destination_paths(file)
        # destinations = data_store['destination_abs_paths']
        text = data_store.get('rendered_content', file.as_posix())
        import pdb; pdb.set_trace()  # breakpoint 2ce118d3 //

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


class TreeItem(object):
    depth = 0
    type = 'unknown'
    child_count = None
    name = None

    def __init__(self, **kw):
        self.children = set()
        self.files = set()
        self.__dict__.update(kw)

    @property
    def is_dir(self):
        return self.type == 'dir'

    @property
    def is_file(self):
        return self.type == 'file'

    def __repr__(self):
        is_file = self.type == 'file'
        v =  '' if is_file else f'children={len(self.children)} '
        _f = '' if is_file else f'files={len(self.files)} '

        return (
                # f'<{self.__class__.__name__}'
                f'<T({self.type.upper()} '
                f'"{self.name}" '
                f'depth={self.depth} '
                f'{_f}'
                f'{v}'
                f'{"" if is_file else Path(*self.item)}'
                ')>')


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

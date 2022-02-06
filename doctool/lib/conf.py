from pathlib import Path
import renderer
import writer
import sys

HERE = Path(__file__).parent
sys.path.append(HERE.as_posix())


class UtilBase(object):

    def setup_utilities(self):
        if self.utilities is None:
            self.utilities = ()

        r = {}
        for Util in self.utilities:
            util = Util(self)
            r[util.name] = util
        self._utils = r

    def get_utils(self):
        return self._utils

    def run_utility(self, name, *a, **kw):

        r = ()
        for _, utility in self.get_utils().items():
            v = getattr(utility, name)(*a, **kw)
            r +=(v,)
        print('')
        return r


class Config(UtilBase):
    """A config accepts the 'pack' create by a generator; unpacked into the
    __dict__ of this class.
    """
    others = None
    utilities = None

    def __init__(self, parent, pack):
        self._utils = {}
        self._parent = parent
        self.__dict__.update(pack)
        self.setup_utilities()

    def get_everything_list(self):
        """Return all target files and folders within the root directory.
        This should return "everything" the generator should see, including
        asset directories.
        """
        path = self.get_root_path()
        print('  Getting files at:', path)
        all_files = path.glob(self.get_file_discovery_pattern())
        return tuple(all_files)

    def get_root_path(self):
        """Return the base dir of the config files.

        return config "docs_dir" or the original path of the config file.
        """
        return Path(self.base_data.get('docs_dir', self.original_path))

    def get_output_dir(self):
        """The output dir should be explicit, with an absolute 'output_dir'
        If not absolute, the relative is made from the partial
        """

        site_name = self.get_rel_site_dir()
        true_output_dir = self.base_data.get('output_dir', None)
        root = self.get_output_root_dir()

        if true_output_dir is not None:
            if Path(true_output_dir).is_absolute():
                return true_output_dir

            # apply the root and return.
            # the root should be the [config location]/[true_output_dir]
            return root / true_output_dir

            # invent one from all the parts.
        rev = root or self.original_path
        out_path = Path(self.base_data.get('output_dir', rev)) / site_name

        if out_path.is_absolute():
            return out_path

        # Decide the root of the 'site/**'
        # This should be the local of config file: "[conf_path]/site/**"
        return rev / out_path

    def get_output_root_dir(self):
        """return the _output root directory_; the absolute folder path to
        store the generated _site_ folder.

        This is not the _output dir_, which may be the _partial_ to store
        within this directory

        this is the absolute location of config file, or the initial root location.
        """
        output_root = self.base_data.get('output_root_dir', None)

        if output_root is not None:
            if Path(output_root).is_absolute():
                return output_root
            # the root directory to store content is relative;
            # return the default store location, likely the config location.
            return self.original_path / output_root

        # root dir is empty. return a default, which is likely the
        # config location
        return self.original_path

    def get_rel_site_dir(self):
        """The sub directory of all finished files within the target output
        directory.
        This should be relative
        """
        site_dir_name = self.base_data.get('site_dir_name', None) or 'site'
        return site_dir_name

    def get_host_path(self):
        """Return the _parent directory of the root directory.
        Or redefined; return the absolute directory of the given config path.
        """
        aa = self.original_given_path
        bb = self.original_path
        print('  GIVEN: ', bb)
        print('  Found: ', aa)
        found_root = Path(str(bb).rsplit(str(aa))[0])
        return found_root

    def get_file_discovery_pattern(self):
        return '**/*'

    def prepare(self):
        return self.run_utility('prepare')

    def render_out(self):
        """Called after all processing is complete, create a new render unit
        and call all utiliies "render_out.".

        After render is complete, the data_store content is written to disk.
        """
        _renderer = renderer.RenderUnit(self)
        return self.run_utility('render_out', _renderer)

    def preprocess(self):
        """Run the internal systems from the _root_ of the work.
        """
        self.all_files = self.get_everything_list()
        return self.run_utility('preprocess')

    def postprocess(self):
        """Ran after preprocessing and cross referencing is done, build the
        final dict objects for each file. ready for render.
        """
        return self.run_utility('postprocess', depth=0)

    def finalize_content(self):
        """The last step before all content is frozen for rendering.
        Change any data before the next step plug and index.

        Noting the data structure shouldn't change _after_ this step as
        _plug_ checks for empty references through destination paths and
        path data_stores.
        The _index_ needs the last list output, else the _render_ phase will
        print references to file indexes.
        """
        return self.run_utility('finalize_content')

    def plug_holes(self):
        """inject any missing files as pseudo assets in the
        file store.
        """
        return self.run_utility('plug_holes')

    def build_indexes(self):
        """After 'plug_holes' has complete the final changes, the
        indexed may be built.
        """
        return self.run_utility('build_indexes')

    def write_all(self):
        _writer = writer.WriterUnit(self)
        return self.run_utility('write_all', _writer)

    def get_store(self, name):
        return self._parent.get_named_store(name)

    def get_render_package_name(self, asset_path='assets/templates'):
        """
        """
        ap = (HERE / asset_path).as_posix()
        return (ap,)# (ap, 'templates')

    def get_template_locations(self, default='assets/templates'):
        """
        (Pdb) self.original_path
        'C:/Users/jay/Documents/projects/shopping-list/doctool/examples/three'

        (Pdb) self.original_given_path
        'examples/three'

        (Pdb) self.get_root_path()
        'C:/Users/jay/Documents/projects/desktop/docs'

        (Pdb) self.get_host_path()
        'C:/Users/jay/Documents/projects/shopping-list/doctool'
        """

        return [
            self.get_render_package_name(default),
            (self.original_path / default,),
            (self.get_root_path() /  default,),
            (self.get_host_path() /  'templates',),
        ]

    def get_markdown_template_locations(self):
        return self.get_template_locations(default='assets/markdown')


    def __getattr__(self, k):
        v = self.base_data.get(k)
        if isinstance(v, dict):
            return Struct(v)
        if v is None:
            return StructNone(k)
        return v

    def __repr__(self):
        s = f'<Config {self.original_path}>'
        return s


class Enumeration(type):
    def __instancecheck__(self, other):
        return other == None


class Struct(object):
    _data = None

    def __init__(self, v):
        self._data = v

    def __getattr__(self, k):
        v = self._data.get(k)
        if isinstance(v, dict):
            return self.__class__(v)
        if v is None:
            return StructNone(k)
        return v

    def __repr__(self):
        return f'<..{str(self.__dict__["_data"])}>'


class StructNone(object):

    _k = None

    def __hash__(self):
        return id(None)

    def __init__(self, k=None):
        self._k = k

    def __getattr__(self, k):

        return StructNone(k)

    def __eq__(self, other):
        return other == None

    def __repr__(self):
        return f'None({self._k})'

    __metaclass__ = Enumeration

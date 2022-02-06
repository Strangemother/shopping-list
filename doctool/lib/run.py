"""Given a path, product some docs.
"""


"""A path may come from:
+ the command line
+ The settings
+ default _current location_
"""
import os
import sys
from pathlib import Path
import argparse

from storage import DataStore
from reader import *
import utils# import Printer
from conf import Config
from collections import ChainMap


parser = argparse.ArgumentParser(description='Processor')
# parser.add_argument('integers',
#                     metavar='N',
#                     type=int,
#                     nargs='+',
#                     help='an integer for the accumulator')

parser.add_argument('targets',
                    metavar='PATH',
                    type=Path,
                    # action='extend',
                    default=tuple(),
                    nargs='*',
                    help='an integer for the accumulator')


parser.add_argument('-c', '--config',
                    # metavar='N',
                    type=Path,
                    # nargs='+',
                    default=None,
                    help='A config file')

paths = sys.argv[1:]


BASE_UTILS =  (
    utils.Printer,
    utils.General,
    utils.Writer,
)

def main():
    args = parser.parse_args(paths)
    gen = Generator(args)
    gen.run_process()
    return gen


from pydoc import locate


def merge(source, destination):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


class Generator(object):
    namespace = None
    paths = None

    def __init__(self, namespace=None):
        if namespace is not None:
            self.load_namespace(namespace)
        self.reset()

    def reset(self):
        """Initialise the internal data; not including the paths or namespace.
        """
        self.storage = {}
        self.finalized = False
        self.root_directory = None # os.getcwd()
        self._utils_cache = None
        print('new generator for', paths)

    def load_namespace(self, namespace):
        self.namespace = namespace
        self.paths = namespace.targets
        # self.early_setting = [namespace.config]

    def run_process(self, namespace=None):
        """Run the entire process"""
        if namespace is not None:
            self.load_namespace(namespace)

        self.collect()
        self.preprocess()

        self.postprocess()
        self.finalize_content()
        self.plug_and_index()
        self.render_out()
        self.write_all()

    def collect(self):
        """Read each target path and generate a list
        of absolute paths of all target assets
        """
        packs = self.gather_packs()
        configs = self.make_configs(packs)
        self.confs = configs

        for c in configs:
            c.prepare()
            # self.run_chains('prepare')

    def make_configs(self, packs):
        configs = ()
        for pack in packs:
            config = Config(self, packs[pack])
            configs += (config,)
        for c in configs:
            c.others = configs
        return configs

    def gather_packs(self):
        paths = self.resolve_paths()
        lp = len(paths)
        s = 's' if lp != 1 else ''
        print(f'  {lp} path{s}')
        packs = {}

        for given_path, resolved_path in paths:
            packs[given_path] = self.create_build_pack(given_path, resolved_path)
        self.packs = packs
        return packs

    def preprocess(self):
        """The generating and binding of all cross reference tools and renamers.
        """
        for conf in self.confs:
            conf.preprocess()

    def postprocess(self):
        """The generating and binding of all cross reference tools and renamers.
        """
        for conf in self.confs:
            conf.postprocess()

    def create_build_pack(self, given_path, resolved_path):
        """Given a resolved path, iterate and build the
        pack for the path.
        """
        path = resolved_path
        # Discover config.
        #   Through arg.
        paths = (
            '**/pyproject.toml',
            '**/docs.yaml',
        )

        conf_path = None

        # Look at all possible paths.
        # also ff the given path is the name
        for rel_p in paths:
            p = Path(rel_p)

            match = path.name == p.name
            if match:
                print(f'Given path is a config path: "{path.name}"')
                conf_path = path
                break

            found = tuple(path.glob(rel_p))
            if len(found) > 0:
                conf_path = found[0]
                break

        base_data = {}

        if conf_path is not None:
            reader = get_reader_class(conf_path)
            base_data = reader().load_and_repoint(conf_path)

        print('Config:', base_data)
        # all_files = path.glob('**/*')

        return dict(
            run_cwd=os.getcwd(),
            original_path=path,
            original_given_path=given_path,
            config_path=conf_path,
            base_data=base_data,
            utilities=self.get_base_utilities(base_data)
            # all_files=all_files,
        )

    def get_base_utilities(self, *merge_dicts):

        # Grab and load from the config or return the base_urils.
        conf = self.get_master_config()

        if conf is None:
            print('Bad master config')
            conf = {}

        chain_conf = ChainMap(*merge_dicts, conf)
        # Iterate the base utils and resolve any remote references.
        try:
            utils = chain_conf['docs']['base']['utils']
        except (TypeError, KeyError) as e:
            utils = chain_conf.get('base_utils') or BASE_UTILS

        r = ()
        existing = self._utils_cache or ()

        for util_or_name in utils:
            if isinstance(util_or_name, str):
                # resolve.
                if util_or_name == '__existing__':
                    r += existing
                    continue
                util = locate(util_or_name)
                if util is None:
                    raise Exception(f'doc.utility was not located: "{util_or_name}"')
                util_or_name = util
            r += (util_or_name, )


        self._utils_cache = r
        return self._utils_cache

    def get_master_config(self):
        """Return the config dict given from the parent loadout.
        If undefined, the default is returned.
        """
        conf_path = self.namespace.config
        conf = None
        if conf_path is not None:
            conf = grab(conf_path)

        if conf is not None:
            return conf

        print(' returning default cache')
        default_conf = {
            'docs': {
                'base': {
                    'utils': BASE_UTILS
                }
            }
        }

        return default_conf



    def get_named_store(self, name):
        """Return a dictionary for the storage of the incoming
        content relative to the name.
        """
        store = self.storage.get(name, None)
        if store is None:
            store = DataStore(name)
            self.storage[name] = store

        return store

    def resolve_paths(self):
        fulls = ()

        for path in self.paths:
            lp = Path(path)

            if not lp.is_absolute():
                # push the correct start directory
                # likely _current directory_
                new_full = lp.absolute()
                if self.root_directory is not None:
                    pre_path = Path(self.root_directory)
                    new_full = pre_path / path
                lp = new_full
            fulls += ((path, lp),)
        return fulls

    def finalize_content(self):
        """The last step before plugging in automated tooling and rendering
        the content into output form.

        Change any paths, content, tags and cross refere information here.
        Next step will plug the gaps and index.
        """

        for conf in self.confs:
            conf.finalize_content()
        self.finalized = True

    def plug_and_index(self, force=False):
        """Populating any required gaps in file structure and requirements,
        Build pseudo outputs for index files, later written.

        Called after 'finalize'
        """

        if (not self.finalized) and (force is False):
            raise Exception("Config should be finalized or force=True")

        self.plug_holes()
        self.build_indexes()

    def plug_holes(self):
        """Inject any simulated files, expecting 'finalize' to have been called.
        Rebrand any output filepaths here, the next step is _build indexes_,
        at which point a render occurs.
        """
        for conf in self.confs:
            conf.plug_holes()

    def build_indexes(self):
        """After 'plug_holes' has complete the final changes, the
        indexed may be built.
        This may produce additional files but those files should
        inject into the file cache and index.

        The next and last step after building the indexes will be 'render'
        of all files to the output."""
        for conf in self.confs:
            conf.build_indexes()

    def render_out(self):
        """The last step to run after all the files are parsed, processed,
        plugged and indexed.
        At this point all the data is complete, and a ready dict is
        prepared within the data store for any outbound files.
        """
        for conf in self.confs:
            conf.render_out()

    def write_all(self):
        """All rendering is done - write the files to disk using a writer
        unit.

        For builtin this should produce a directory of html files, with
        the markdown parsed through the default site template.
        """
        for conf in self.confs:
            conf.write_all()

if __name__ == '__main__':
    main()

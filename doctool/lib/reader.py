import yaml
import json
import toml
from pathlib import Path

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Reader(object):
    path = None
    data = None

    def load_and_repoint(self, path=None):
        print('Loading', path)
        path = path or self.path

        content = self.load(path)
        if 'config_path' in content:
            cp = content['config_path']
            print('repointing to', cp)
            return self.load_and_repoint(cp)

        self.data = content
        return self.data

    def load(self, path):
        # Return a dict of the given path content.
        return {}


class JSONReader(Reader):

    def load(self, path):
        # Return a dict of the given path content.
        return json.loads(path.read_text())


class YamlReader(Reader):

    def load(self, path):
        # Return a dict of the given path content.
        return yaml.load(path.read_text(), Loader=Loader)


class TomlReader(Reader):

    def load(self, path):
        # Return a dict of the given path content.
        return toml.load(path)


def get_reader_class(path):
    openers = {
        '.yaml': YamlReader,
        '.toml': TomlReader,
        '.json': JSONReader,
    }

    suffix = Path(path).suffix
    er = openers.get(suffix)
    return er
    # reader = opener()
    # return reader.load_and_repoint(_path)

def grab(path):
    ReaderClass = get_reader_class(path)
    if ReaderClass:
        return ReaderClass().load_and_repoint(path)
    raise Exception(f'No config found: {path}')

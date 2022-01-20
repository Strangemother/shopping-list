from collections import UserDict


class DataStore(UserDict):
    """A dictionary type unit to replace the in memory reference, and apply
    shortcuts (and validation) in one location.
    """
    # meta = None
    def __init__(self, owner_name, **kw):
        self._owner_name = owner_name
        super().__init__(**kw)

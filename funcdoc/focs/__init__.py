import inspect


def func_reader(*funcs):
    ref_tree = {}
    dsr = DocStringParser(ref_tree)
    l = len(funcs)
    for i, func in enumerate(funcs):
        print(f'Reading {i+1}/{l}')
        fr = FuncReader(func)
        dsr.add_parser(fr)

    # for i, fr in enumerate(dsr.refs):
    #     print(f'Build Tree {i+1}/{l}')
    #     fr.build_word_list()

    return dsr


def class_reader(*classes):
    ref_tree = {}
    dsr = DocStringParser(ref_tree)
    l = len(classes)
    for i, class_ in enumerate(classes):
        print(f'Reading {i+1}/{l}')
        cr = ClassReader(class_)
        dsr.add_parser(cr)

    return dsr



from collections import ChainMap


class DocStringParser(object):

    def __init__(self, tree):
        self.ref_tree = tree
        self.entity_refs = {}

    def add_parser(self, reader, ref_tree=None):
        """Given a reader unit render the string content within the docs
        and pollute the func reader with read stats.
        """
        uid = id(reader)
        reader.uuid = uid
        self.entity_refs[uid] = reader
        print('  DocStringParser add_parser', reader)

        # Return value
        # args
        # kwargs
        # tags for all cross references

    @property
    def refs(self):
        return tuple(self.entity_refs.values())


class ClassReader(object):
    """Read a live (functime) function or method - extracting the docs,
    vars and signature.
    """

    specs = None
    ivars = None
    src = None
    sig = None
    doc = None
    name = None
    comments = None
    file = None
    line_no = None
    uuid = None

    def __init__(self, func):
        self.read_func(func)

    def read_func(self, func):
        self.specs = self.get_args_spec(func)
        self.src, self.line_no = self.get_source_lines(func)
        self.sig = self.get_signature(func)
        self.doc = self.get_doc(func)
        self.comments = self.get_comments(func)
        self.name = self.get_name(func)
        self.file = self.get_file(func)
        self.read_params()

    def read_params(self):
        words = (
            self.name,
            )
        self.words = words
        self.params = self.parse_sig_params()
        self.sig_str = str(self.sig)
        self.return_value = self.sig.return_annotation

    def parse_sig_params(self, sig=None):
        sig = sig or self.sig
        params = sig.parameters
        r = {}
        for k, v in params.items():
            r[k] = self.read_parameter(v)
        return r

    def read_parameter(self, param):

        empty = param.empty
        # initially 'required' is a boolean of the _empty_.
        # If empty, it's required.
        required = param.default is empty
        _type = type(param.default)
        int_kind = int(param.kind)
        annotation = param.annotation

        if int_kind in [2, 4]:
            # *arg or **kwarg.
            # these are naturally empty.
            required = False
            types ={ 2: tuple, 4: dict}
            _type = types.get(int_kind, _type)


        if (_type is type(None)) and (annotation is not empty):
            # double check the annotation for a type.
            # log override here...
            _type = annotation

        return dict(
            name=param.name,
            default=param.default,
            type=_type,
            # kind=param.kind,
            required=required,
            kind_str=str(param.kind),
            kind_int=int_kind,
            dict_pack=int_kind == 4,
            args_pack=int_kind == 2,
            annotation=annotation,
            )

    def get_params(self):
        return self.sig.parameters

    def get_args_spec(self, func):
        return inspect.getfullargspec(func)

    def get_source_lines(self, func):
        return inspect.getsourcelines(func)

    def get_signature(self, func):
        return inspect.signature(func)

    def get_doc(self, func):
        return inspect.getdoc(func)

    def get_name(self, func):
        return func.__name__

    def get_comments(self, func):
        return inspect.getcomments(func)

    def get_file(self, func):
        return inspect.getfile(func)

    def __repr__(self):
        args = ', '.join(self.specs.args)
        s = f'<{self.__class__.__name__}({self.uuid}) {self.name}>'
        return s


class FuncReader(ClassReader):

    def read_func(self, func):
        super().read_func(func)
        self.ivars = self.get_closure_vars(func)

    def get_closure_vars(self, func):
        return inspect.getclosurevars(func)

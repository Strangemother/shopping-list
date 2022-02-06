from focs import func_reader, class_reader


class Foo(object):
    """A Class...
    """
    firstvar = None

    def __init__(self, firstvar:str=None):
        self.firstvar = firstvar

    def coconut(self, food=1):
        print('Use coconut', food)


def history_classes(target_name=None, model_class=None, models=None, class_module_name=None,
                    module_needles=None, **base_definition) -> tuple:
    """Generate a range of "history" class-based-views for the given `model_class`
    list. This is synonymous to calling `short.views.history` repeatedly.

    Given a `model_class` as a `models.Model`, `list` or `tuple` type, build a
    set of Archive based views into the `target_name`.

    Arguments:
        **base_definition {dict} -- attributtes given to all classes as base
                                    class properties and methods

    Keyword Arguments:
        target_name {str} -- Name of the target module to insert the newly generated
            classes. If `None` the `__name__` of the calling method module
            is applied. (default: {None})
        model_class {models.Model, tuple, list} -- The target model or models
            to generate views. If `None` dicover the models using
            `short.views.discover_models` (default: {None})
        models {list, tuple} -- Use an explicit list of `models` over `model_class`.
            If `None` the model_class is used (default: {None})
        class_module_name {str} -- The string name of the module to insert the
            newly generated classes, such as `"products.views"`.
            If `None` attempt to capture the _last frame_ caller module name,
            defaulting to the calling module name. (default: {None})
        module_needles {list, tuple} -- A list of module names to focus upon
            if model discovery is used. If a dicovered model originated from
            a module name within the needles, history views will be created
            (default: {None}).

    Returns:
        {tuple} -- A tuple of generated classes. The class-based-views already
                 exist within the `target_name`
    """

    if target_name is None:
        target_name = inspect.currentframe().f_back.f_globals['__name__']

    if model_class is None:
        model_class = discover_models(target_name, models, module_needles)

    model_class = ensure_tuple(model_class)

    r = ()
    for m in model_class:
        v = history(m, class_module_name=class_module_name or target_name,
                 **base_definition)
        r += (v,)
    return r


def defaults(args, params, nil_sub=True, nil_key='nil', **kw):
    """A short description of this function

    A large description of this function complete with call info such as:
    defaults(entity, apples='one', cheese=2), and `blank_null` without the need
     to build cross-reference or worry about indentation. Consider this:

    Example implementation:

        def filepath(*a, **kw):
            kw = defaults(a, kw, nil=True)
            return models.FilePathField(*a, **kw)

    We note here some indented doc - This should become a 'code block'

    Arguments:
        args {[type]} -- [description]
        params {[type]} -- [description]
        **kw {[type]} -- [description]

    Keyword Arguments:
        nil_sub {bool} -- [description] (default: {True})
        nil_key {str} -- [description] (default: {'nil'})

    Returns:
        [type] -- [description]
    """
    if nil_sub:
        # nil subtract, or substitution
        #  Nil. being blank+null - where nil=True
        if 'nil' in kw:
            val = kw.get('nil', None)

            if isinstance(val, bool):
                val = [val] * 2

                kw.update(**blank_null(*val))

    for k,v in kw.items():
        if k == nil_key:
            continue

        params.setdefault(k, v)
    return params


def blank_null(b=True, n=True):
    return {'blank':b, 'null': n}


def watch(self, path, func=None, delay=0, ignore=None):
    """Add a task to watcher -with an example of :colon param: params.

    :param path: a filepath or directory path or glob pattern
    :param func: the function to be executed when file changed
    :param delay: Delay sending the reload message. Use 'forever' to
                  not send it. This is useful to compile sass files to
                  css, but reload on changed css files then only.
    :param ignore: A function return True to ignore a certain pattern of
                   filepath.
    """
    self._tasks[path] = {
        'func': func,
        'delay': delay,
        'ignore': ignore,
        'mtimes': {},
    }


def complex_pack(first, *items, unrequired=True, nully=None, **packed) -> bool:
    """An example of a function with all signature keyword types.
    """
    val = True
    return val

from pprint import pprint as pp

r = func_reader(Foo().coconut, defaults, history_classes, watch, complex_pack)
r = class_reader(Foo)#().coconut, defaults, history_classes, watch, complex_pack)
d = r.refs[0]
pp(d.params)

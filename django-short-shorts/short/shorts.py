from django.db import models

def defaults(args, params, nil_sub=True, nil_key='nil', **kw):

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


def url(*a, **kw):
    """A django `models.URLField` passing any arguments and keyword arguments

    provide as a standard field:

        class MyModel(models.Model):
            url = shorts.url(max_length=2000)

    """
    # kw.setdefault('max_length', 200)
    # defaults(kw, **blank_null())
    defaults(a, kw, nil=True, max_length=200)
    return models.URLField(**kw)


def text(*a, **kw):
    """
    """
    # defaults(kw, **blank_null())
    kw = defaults(a, kw, nil=True)
    return models.TextField(*a, **kw)


def chars(first_var=None, *a, **kw):
    """
    """

    # Rearrange the params, if the first var is callable, it's the default func,
    # if an int, it's the max_length
    # If the default= exists, raise an error
    default_max_length = 255
    max_length = default_max_length

    if callable(first_var):
        # Set as default
        max_length = kw.get('max_length', None)
        if kw.get('default', None) is not None:
            s = ('shorts.chars(*default_or_max_length, **params) accepts a'
                ' "default" keyword argument or a function as the first'
                ' argument. Not both.')
            # chars(255)
            # chars(max_length=255)
            # chars(255, default=default_func)
            # chars(default_func)
            # chars(default=default_func)
            # chars(max_length=255, default=default_func)
            # not:
            # chars(func, default=default_func)

            raise Exception(s)

        kw.setdefault('default', first_var)

    if max_length is None:
        max_length = default_max_length

    kw = defaults(a, kw, max_length=max_length, nil=True)
    return models.CharField(*a,**kw)


def text(*args, **kw):
    """
    """
    kw = defaults(args, kw, nil=True)
    return models.TextField(*args, **kw)

def boolean(*a, **kw):
    return models.BooleanField(*a, **kw)


def null_bool(*a, **kw):
    """
    """
    kw = defaults(a, kw, nil=True)
    return boolean(*a, **kw)


def true_bool(*a, **kw):
    """
    """
    kw = defaults(a, kw, default=True)
    return boolean(*a, **kw)


def false_bool(*a, **kw):
    """
    """
    kw = defaults(a, kw, default=False)
    return boolean(*a, **kw)


def blank_dt(*a, **kw):
    kw = defaults(a, kw, nil=True)
    return datetime(*a, **kw)


def datetime(*a, **kw):
    return models.DateField(*a, **kw)

dt_blank = blank_dt


def dt_created(*a, **kw):
    """
    """
    kw.setdefault('auto_now_add', True)
    return datetime(*a, **kw)


def dt_updated(*a, **kw):
    """
    """
    kw.setdefault('auto_now', True)
    return datetime(*a, **kw)


def integer(*a, **kw):
    """
    """
    value = None
    if len(a) > 0:
        value = a[0]
        a = a[1:]

    if value is not None:
        kw.setdefault('default', value)
    return models.IntegerField(*a, **kw)


def get_user_model():
    return settings.AUTH_USER_MODEL


def fk(other, *a, on_delete=None, **kw):
    kw = defaults(a, kw, on_delete=on_delete or models.CASCADE)
    return models.ForeignKey(other, *a, on_delete=on_delete, **kw)


def user_o2o(*a,**kw):
    return fk(get_user_model(), *a, nil=True, **kw)


def m2m(other, *a, **kw):
    """
    """
    kw = defaults(a, kw, blank=True)
    return models.ManyToManyField(other, *a, **kw)


def o2o(other, *a, on_delete=None, **kw):
    kw = defaults(a, kw, on_delete=on_delete or models.CASCADE)
    return models.OneToOneField(other, *a, on_delete=on_delete, **kw)


def user_o2o(*a, **kw):
    return o2o(get_user_model(), *a, **kw)


o2o_user = user_o2o

def image(*a, **kw):
    """
    """
    kw = defaults(a, kw, blank=True)
    return models.ImageField(*a, **kw)


"""
Short URL to help lighten the load for dev urls

    default:

        from django.urls import path

        urlpatterns = [
            path('', views.ProductListView.as_view(), name='list'),
            path('new/', views.ProductCreateView.as_view(), name='create'),
            path('change/<str:pk>/', views.ProductUpdateView.as_view(), name='update'),
            path('delete/<str:pk>/', views.ProductDeleteView.as_view(), name='delete'),
            path('<str:pk>/', views.ProductDetailView.as_view(), name='detail'),
        ]


    to this:

        from . import models
        from short.models import grab_models

        urlpatterns = shorts.paths_default(views, grab_models(models),
            views=('list', 'create', 'update', 'delete', 'detail',),
        )


    or this:

        from . import models
        from short.models import grab_models

        urlpatterns = shorts.paths_less(views, grab_models(models),
            ignore_missing_views=True,
            list='',
            create='new/',
            update='change/<str:pk>/',
            delete='delete/<str:pk>/',
            detail='<str:pk>/',
        )


"""
from django.contrib import admin
from django.urls import path, include as django_include
from  django.views.generic import View

import inspect

from short.names import *
from . import names as short_names


urlpatterns = [
    # path('admin/', admin.site.urls),
]


def clean_str(variant):

    if variant in (False, None,):
        return ''
    return variant


def path_includes(*names):

    flat_names = ()
    r = {}

    for name in names:
        if isinstance(name, (list,tuple)) is False:
            name = (name, )
        flat_names += name

    for fln in flat_names:
        print('Making', fln)
        r[fln] = f'{fln}/', django_include(f'{fln}.urls')

    return paths(**r)


def path_include(url_name, url_module, path_name=None):
    """
        path_include('products/',)
        path_include('mythings/', 'products.urls', ) # name=mythings
        path_include('mythings/', 'products.urls', 'items') # name=items
        path_include('products/', 'products.urls', 'products')
    """
    r = {}
    url = url_name
    if not url.endswith('/'):
        url = f'{url}/'

    name = path_name or url_name
    if name.endswith('/'):
        name = name[1:]

    r[name] = (url, django_include(f'{name}.urls'), )

    return paths(**r)


def paths_default(views_module, model_list, ignore_missing_views=True, views=None, **options):
    """
        from . import models
        from short.models import grab_models

        urlpatterns = shorts.paths_default(views, grab_models(models),
            ignore_missing_views=True,
            views=('list', 'create', 'update', 'delete', 'detail',),
        )
    """
    patterns = {}

    for name in views:
        url = short_names.get_url(name)
        patterns[name] = url

    return paths_less(
            views=views_module,
            model_list=model_list,
            ignore_missing_views=ignore_missing_views,
            **patterns)


def paths_less(views, model_list, ignore_missing_views=False, **patterns):
    """
        from . import models
        from short.models import grab_models

        urlpatterns = shorts.paths_less(views, grab_models(models),
            ignore_missing_views=True,
            list='',
            create='new/',
            update='change/<str:pk>/',
            delete='delete/<str:pk>/',
            detail='<str:pk>/',
        )

    """
    if isinstance(model_list, (list, tuple,)) is False:
        model_list = (model_list,)

    r = []
    for m in model_list:
        name = m.__name__
        unp = name.lower()
        url_pattern_prefix=f'{unp}/'
        r += paths_named(views, name,
            url_pattern_prefix=url_pattern_prefix,
            ignore_missing_views=ignore_missing_views,
            url_name_prefix=f'{unp}-',
            **patterns)
    return r


def paths_named(views, view_prefix=None, ignore_missing_views=False, url_pattern_prefix=None,
        url_name_prefix=None, **patterns):
    """
        urlpatterns = shorts.paths_named(views,
            view_prefix='Product',

            list=('ListView',''),
            create=('CreateView','new/'),
            update=('UpdateView','change/<str:pk>/'),
            delete=('DeleteView','delete/<str:pk>/'),
            detail=('DetailView','<str:pk>/'),
        )

    or less:

        urlpatterns = shorts.paths_named(views,
            view_prefix='Product',
            # name_genfix="{view_prefix}{mapped_name}View",
            list='',
            create='new/',
            update='change/<str:pk>/',
            delete='delete/<str:pk>/',
            detail='<str:pk>/',
        )
    """
    new_patterns = {}
    for app_name, solution in patterns.items():
        if isinstance(solution, (list, tuple,)) is False:
            # only a URL given.
            # convert the 'list' to 'ListView'
            solution = (MAPPED_NAMES.get(app_name), solution)

        class_name, url = solution
        new_patterns[class_name] = (app_name, url)

    return paths_dict(views, new_patterns, view_prefix,
        url_pattern_prefix=url_pattern_prefix,
        url_name_prefix=url_name_prefix,
        ignore_missing_views=ignore_missing_views)


def paths_dict(views, patterns, view_prefix=None,
    ignore_missing_views=False,
    url_pattern_prefix=None,
    url_name_prefix=None,
    ):
    """Given the views module and the patterns,
    generate a shjort path list.

        short_patterns = {
            'ProductListView': '',
            'ProductCreateView': ('create', 'new/'),
            'ProductUpdateView': ('update', 'change/<str:pk>/'),
            'ProductDeleteView': 'delete/<str:pk>/',
            'ProductDetailView': '<str:pk>/',
        }

        urlpatterns = shorts.paths_dict(views, short_patterns)


        short_patterns = dict(
            ListView='',
            CreateView=('create', 'new/'),
            UpdateView=('update', 'change/<str:pk>/'),
            DeleteView='delete/<str:pk>/',
            DetailView='<str:pk>/',
        )

        urlpatterns = shorts.paths_dict(views, short_patterns, view_prefix='Product')
        urlpatterns = shorts.paths_dict(views, short_patterns, view_prefix='People')

    """
    flag_class = View
    # r = ()
    d = {}

    view_prefix = clean_str(view_prefix)
    url_pattern_prefix = clean_str(url_pattern_prefix)
    url_name_prefix = clean_str(url_name_prefix)

    for part_name, solution in patterns.items():
        class_name = f"{view_prefix}{part_name}"
        try:
            view = getattr(views, class_name)
        except AttributeError as e:
            if ignore_missing_views is False:
                raise e
            continue

        if isinstance(solution, (list, tuple,)) is False:
            current_name = class_name.lower()
            last_name = inspect.getmro(view)[1].__name__
            app_name = MAPPED_CLASS.get(last_name, current_name)
            solution = (app_name, solution,)

        path_name, url = solution

        furl = f'{url_pattern_prefix}{url}'
        fname = f'{url_name_prefix}{path_name}'
        d[fname] = (furl, view)

    return paths(**d)


def paths(**path_dict):
    """
        urlpatterns = shorts.paths(
            list=('', views.ProductListView,),
            create=('new/', views.ProductCreateView,),
            update=('change/<str:pk>/', views.ProductUpdateView,),
            delete=('delete/<str:pk>/', views.ProductDeleteView,),
            detail=('<str:pk>/', views.ProductDetailView,),
        )

        urlpatterns = [
            path('', views.ProductListView.as_view(), name='list'),
            path('new/', views.ProductCreateView.as_view(), name='create'),
            path('change/<str:pk>/', views.ProductUpdateView.as_view(), name='update'),
            path('delete/<str:pk>/', views.ProductDeleteView.as_view(), name='delete'),
            path('<str:pk>/', views.ProductDetailView.as_view(), name='detail'),
        ]

    """
    flag_class = View
    r = ()
    for name, params in path_dict.items():
        (url, unit) = params
        func = unit
        if isinstance(func, tuple) is False:

            mros = inspect.getmro(unit)
            if flag_class in mros:
                func = unit.as_view()

        p = path(url, func, name=name)
        r += (p,)

    return list(r)

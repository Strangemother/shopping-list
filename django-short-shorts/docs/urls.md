# URL's and Paths

Django Short Shorts provides a range of url `path` setup functions for setting up your `urls.py` with less typing.


Firstly lets look at a few `path` urls using the standard method:

```py
from django.urls import path

from . import views

urlpatterns += [
    path('', views.NoteIndexView.as_view(), name='index'),
    path('<str:pk>/json/', views.EntryDetailView.as_view(), name='entry-detail-json'),
    path('entry/list/json/', views.EntryJsonList.as_view(), name='entry-list-json'),
]
```

Let's use the `short.urls.paths_dict` function to build the same thing with less typing:

```py
short_patterns = {
    'NoteIndexView': ('index', ''),
    'EntryJsonList': ('entity-list-json', 'entry/list/json/',),
    'EntryDetailView':('entry-detail-json', '<str:pk>/json/', ),
}

urlpatterns += shorts.paths_dict(views, short_patterns)
```

Personally I think a `dict` definition looks nice:

```py
short_patterns = dict(
    NoteIndexView=('index', ''),
    EntryJsonList=('entity-list-json', 'entry/list/json/',),
    EntryDetailView=('entry-detail-json', '<str:pk>/json/', ),
)

urlpatterns += shorts.paths_dict(views, short_patterns)
```

Anything iterable is usable such as a tuple of tuples in place of a dict:

```py
short_patterns = (
    ('NoteIndexView', ('index', '')),
    ('EntryJsonList', ('entity-list-json', 'entry/list/json/',)),
    ('EntryDetailView', ('entry-detail-json', '<str:pk>/json/', )),
)

urlpatterns += shorts.paths_dict(views, short_patterns)
```

However that's a lot of brackets, consider the `short.urls.paths_tuple` to provide flat tuples as your setup.

```py
short_patterns = (
    ('NoteIndexView', 'index', '' ),
    ('EntryJsonList', 'entity-list-json', 'entry/list/json/' ),
    ('EntryDetailView', 'entry-detail-json', '<str:pk>/json/' ),
)

urlpatterns += shorts.paths_tuple(views, short_patterns)
```

---

In all cases the _short.shorts_ library implements a standard `django.urls.path` list,

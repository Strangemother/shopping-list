"""shoppinglist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from short import grab_models, urls as shorts, names
# from short.urls import path_include, path_includes, error_handlers
from . import views, models

app_name = 'products'

urlpatterns = shorts.paths_default(views, grab_models(models),
    views=names.crud() + names.history(),
)

# urlpatterns += shorts.path_urls(views, {
#         '/': shorts.template_view(name='home')
#     })

# urlpatterns += shorts.paths_redirect({
#     '/': ('/home', True,),
#     'out/': 'https://google.com',
#     })


# error_handlers(__name__)

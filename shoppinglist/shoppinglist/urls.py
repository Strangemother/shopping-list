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
from django.contrib import admin
from django.urls import path, include

from short.urls import path_include, path_includes, error_handlers

app_name = 'shoppinglist'

urlpatterns = [
    path('admin/', admin.site.urls),
] + path_includes('products')


error_handlers(__name__)
# error_handlers(__name__, {
#         400: 'shorts.views.errors.handler400',
#         403: 'shorts.views.errors.handler403',
#         404: 'shorts.views.errors.handler404',
#         500: 'shorts.views.errors.handler500',
#     }, template_dir='short/errors/'
# )

# handler404 = 'my_app_name.views.custom_page_not_found_view'
# handler500 = 'my_app_name.views.custom_error_view'
# handler403 = 'my_app_name.views.custom_permission_denied_view'
# handler400 = 'my_app_name.views.custom_bad_request_view'

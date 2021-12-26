from django.shortcuts import render

from short import views as shorts

# from . import models
# from short.models import grab_models

# shorts.crud_classes(__name__, models.Product)
# shorts.crud_classes(__name__, grab_models(models))
# shorts.guess_classes(models=grab_models(models))
shorts.crud_classes()
shorts.history_classes()
# shorts.history(models.Product)
# shorts.history(models.Product, __name__, date_field='created')

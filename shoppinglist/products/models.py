from django.db import models
import string
import random

from short import shorts

def rand_str(length=6):
    choices = random.choices(string.ascii_uppercase + string.digits, k=length)
    return ''.join(choices)


class Hyperlink(models.Model):
    _short_props = ('name', 'url',)
    _short_props_label = True
    _short_props_format = '%(prop)s="{self.%(prop)s}"'

    name = shorts.chars()
    url = shorts.url()
    description = shorts.text()



class Location(models.Model):
    _short_props = 'name'
    # _short_props = ('name',)
    # _short_string = '{self.name}'

    name = shorts.chars()



class Product(models.Model):
    _short_string = '{self.name} x{self.count} - {self.location}'

    name = shorts.chars()
    unique_id = shorts.chars(default=rand_str)
    product_id = shorts.chars()
    description = shorts.text()
    urls = shorts.m2m(Hyperlink)
    damaged = shorts.false_bool()
    in_use = shorts.false_bool()
    created = shorts.dt_created()
    updated = shorts.dt_updated()
    count = shorts.integer(1)
    associated = shorts.m2m('self')
    location = shorts.m2m(Location)
    image = shorts.image()

    def get_short_string(self):
        s = '{self.name} - {self.location}' if self.count == 1 else self._short_string
        return s.format(self=self)

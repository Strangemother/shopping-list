# Django Short Shorts

Django Short Shorts (Or short-shorts for short.) helps you quickly build boilerplate work for very fast prototyping and dev jumpstarts. With 'short-shorts' minimal boilerplate code parts, build conventional urls, views, models without the hassle.

> Use Short Shorts for boilerplate, PoC, dev start (or just pure laziness) to quickly write common django components.

## Why build this

A lot of my work with django is hammering fast PoC or dev work - to hack out a new idea, research a small example. I spend a lot of time writing _yet another_ model TextField, or Boilerplating five more ArchiveViews for a throw-away app. Copy/pasting is fine but yields errors.

Django Short Shorts provides a set of methods to _write boilerplate fields, models, views, etc.._ - without forsaking clean code.

For example

    class Product(models.Model):
        name = models.TextField(max_length=255, blank=True, null=True)

Replaced with

    class Product(models.Model):
        name = shorts.text()

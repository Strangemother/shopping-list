# Generated by Django 3.2.10 on 2021-12-25 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20211225_0121'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='associated',
            field=models.ManyToManyField(blank=True, related_name='_products_product_associated_+', to='products.Product'),
        ),
        migrations.AddField(
            model_name='product',
            name='location',
            field=models.ManyToManyField(blank=True, to='products.Location'),
        ),
        migrations.AddField(
            model_name='product',
            name='urls',
            field=models.ManyToManyField(blank=True, to='products.Hyperlink'),
        ),
    ]
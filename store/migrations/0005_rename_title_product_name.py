# Generated by Django 5.1.4 on 2024-12-19 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_rename_name_product_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='title',
            new_name='name',
        ),
    ]

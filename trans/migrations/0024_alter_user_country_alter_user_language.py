# Generated by Django 5.0.6 on 2024-07-16 12:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans', '0023_auto_20220730_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trans.country'),
        ),
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trans.language'),
        ),
    ]

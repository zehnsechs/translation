# Generated by Django 4.2.15 on 2024-08-31 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trans', '0031_alter_country_options'),
        ('autotranslate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertranslationquota',
            name='used',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='UserGlassory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_id', models.CharField(blank=True, max_length=512, null=True)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trans.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
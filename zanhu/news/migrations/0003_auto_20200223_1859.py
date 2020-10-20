# Generated by Django 2.1.7 on 2020-02-23 10:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20200223_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='uuid_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='id_news'),
        ),
    ]

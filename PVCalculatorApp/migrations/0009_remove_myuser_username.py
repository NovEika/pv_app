# Generated by Django 5.1 on 2024-09-16 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PVCalculatorApp', '0008_alter_stringpair_result'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='username',
        ),
    ]

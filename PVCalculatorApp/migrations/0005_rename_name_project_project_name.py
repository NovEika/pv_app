# Generated by Django 5.1 on 2024-09-15 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PVCalculatorApp', '0004_remove_stringpair_solution_resultlowmppt'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='name',
            new_name='project_name',
        ),
    ]
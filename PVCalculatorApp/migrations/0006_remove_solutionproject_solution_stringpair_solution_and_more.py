# Generated by Django 5.1 on 2024-09-16 13:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PVCalculatorApp', '0005_rename_name_project_project_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solutionproject',
            name='solution',
        ),
        migrations.AddField(
            model_name='stringpair',
            name='solution',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='string_pairs', to='PVCalculatorApp.solution'),
        ),
        migrations.RemoveField(
            model_name='solutionproject',
            name='project',
        ),
        migrations.DeleteModel(
            name='ResultLowMppt',
        ),
        migrations.AddField(
            model_name='solutionproject',
            name='project',
            field=models.ManyToManyField(to='PVCalculatorApp.solution'),
        ),
    ]

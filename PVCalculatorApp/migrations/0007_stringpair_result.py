# Generated by Django 5.1 on 2024-09-16 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PVCalculatorApp', '0006_remove_solutionproject_solution_stringpair_solution_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stringpair',
            name='result',
            field=models.CharField(choices=[('low_mppt', 'low_mppt')], default='low_mppt', max_length=20),
        ),
    ]

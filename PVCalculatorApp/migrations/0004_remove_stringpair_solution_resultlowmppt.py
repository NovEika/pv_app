# Generated by Django 5.1 on 2024-09-15 14:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PVCalculatorApp', '0003_remove_solution_name_stringpair'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stringpair',
            name='solution',
        ),
        migrations.CreateModel(
            name='ResultLowMppt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='result_low_mppt', to='PVCalculatorApp.stringpair')),
                ('solution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='string_pairs', to='PVCalculatorApp.solution')),
            ],
        ),
    ]
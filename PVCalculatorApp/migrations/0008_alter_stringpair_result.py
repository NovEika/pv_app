# Generated by Django 5.1 on 2024-09-16 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PVCalculatorApp', '0007_stringpair_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stringpair',
            name='result',
            field=models.CharField(choices=[('low_mppt', 'low_mppt')], default='low_mppt', max_length=50),
        ),
    ]

# Generated by Django 3.0.2 on 2020-02-05 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20200204_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='vehicle',
            field=models.CharField(blank=True, default='Car', max_length=50),
        ),
    ]

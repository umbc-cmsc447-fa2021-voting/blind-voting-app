# Generated by Django 3.2.8 on 2021-11-23 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0002_auto_20211122_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='castvote',
            name='voter_signature',
            field=models.CharField(max_length=50),
        ),
    ]

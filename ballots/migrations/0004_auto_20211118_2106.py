# Generated by Django 3.2.8 on 2021-11-19 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ballots', '0003_alter_ballot_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='choice_text',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='choice',
            name='votes',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
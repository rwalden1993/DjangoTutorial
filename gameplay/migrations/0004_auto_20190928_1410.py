# Generated by Django 2.2.3 on 2019-09-28 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gameplay', '0003_auto_20190926_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='by_first_player',
            field=models.BooleanField(editable=False),
        ),
        migrations.AlterField(
            model_name='move',
            name='game',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='gameplay.Game'),
        ),
    ]
# Generated by Django 5.1.6 on 2025-02-24 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='quantity',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.SmallIntegerField(default=0),
        ),
    ]

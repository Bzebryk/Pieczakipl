# Generated by Django 4.2.5 on 2023-09-27 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0003_purchase_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='purchase_date',
            field=models.DateTimeField(),
        ),
    ]

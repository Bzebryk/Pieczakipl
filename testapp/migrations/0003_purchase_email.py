# Generated by Django 4.2.5 on 2023-09-27 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0002_alter_purchase_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]

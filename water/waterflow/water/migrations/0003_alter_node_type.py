# Generated by Django 5.0.4 on 2024-06-04 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('water', '0002_networkcomponent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='type',
            field=models.CharField(choices=[('tank', 'Tank'), ('valve', 'Valve'), ('outlet', 'Outlet')], default='tap', max_length=10),
        ),
    ]

# Generated by Django 3.0.3 on 2020-02-04 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.IntegerField()),
                ('title', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('neighbors', models.CharField(max_length=250)),
            ],
        ),
    ]

# Generated by Django 2.2.13 on 2020-07-22 20:38

from django.db import migrations, models
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EolSenceCourseSetup',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('course',
                 opaque_keys.edx.django.models.CourseKeyField(
                     max_length=50,
                     unique=True)),
                ('sense_code',
                 models.CharField(
                     max_length=10)),
                ('sense_line',
                 models.IntegerField(
                     choices=[
                         (1,
                          'Sistema Integrado de Capacitacion'),
                         (3,
                          'Impulsa Personas')])),
            ],
        ),
    ]

# Generated by Django 2.2.13 on 2020-07-27 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sence', '0004_auto_20200724_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='eolsencecoursesetup',
            name='sence_course_code',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]

# Generated by Django 2.2.13 on 2020-07-29 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sence', '0007_auto_20200729_1609'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='eolsencestudentsetup',
            unique_together={('user_run', 'course')},
        ),
        migrations.AlterIndexTogether(
            name='eolsencestudentsetup',
            index_together={('user_run', 'course')},
        ),
    ]
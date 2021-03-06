# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-17 10:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0043_auto_20190905_1126'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='source',
            options={'ordering': ('date', 'titre', 'numero', 'parent__date', 'parent__titre', 'parent__numero', 'position', 'page', 'lieu_conservation', 'cote'), 'permissions': (('can_change_status', 'Peut changer l’état'),), 'verbose_name': 'source', 'verbose_name_plural': 'sources'},
        ),
        migrations.AlterField(
            model_name='auteur',
            name='profession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='auteurs', to='libretto.Profession', verbose_name='profession'),
        ),
    ]

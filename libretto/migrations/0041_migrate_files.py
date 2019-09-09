# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-30 13:39
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Prefetch
from tqdm import tqdm


OTHER = 0
IMAGE = 1
AUDIO = 2
VIDEO = 3


def migrate_files(apps, schema_editor):
    Fichier = apps.get_model('libretto.Fichier')
    Source = apps.get_model('libretto.Source')
    Audio = apps.get_model('libretto.Audio')
    Video = apps.get_model('libretto.Video')
    Etat = apps.get_model('libretto.Etat')

    nouveau = Etat.objects.get_or_create(nom='nouveau')[0]

    for source in tqdm(Source.objects.filter(
        fichiers__isnull=False
    ).prefetch_related(
        Prefetch('fichiers', Fichier.objects.order_by('position'))
    ).order_by().distinct()):
        fichiers = list(source.fichiers.all())
        types = list({fichier.type for fichier in fichiers})
        assert len(types) == 1, f'Source {source.pk} has types {types}.'
        type = types[0]

        if type == OTHER:
            assert len(fichiers) == 1, (
                f'Source {source.pk} has more than 1 other files.'
            )
            source.fichier = fichiers[0].fichier
            source.type_fichier = OTHER
            source.save()
        elif type == IMAGE:
            if len(fichiers) == 1:
                source.fichier = fichiers[0].fichier
                source.type_fichier = IMAGE
                source.save()
            else:
                Source.objects.bulk_create([
                    Source(
                        parent=source, position=position, type=source.type,
                        folio=fichier.folio, page=fichier.page or position,
                        fichier=fichier.fichier, type_fichier=IMAGE,
                        etat=nouveau,
                    )
                    for position, fichier in enumerate(fichiers, start=1)
                ])
        elif type in (AUDIO, VIDEO):
            fichiers_ogg = [fichier for fichier in fichiers
                            if fichier.format == 'ogg']
            fichiers_mpeg = [fichier for fichier in fichiers
                             if fichier.format in ('mp3', 'mp4')]
            kwargs = {'source_ptr': source}
            if len(fichiers) == 2:
                assert len(fichiers_ogg) == 1, (
                    f'Source {source.pk} should have 1 OGG file.'
                )
                fichier_ogg = fichiers_ogg[0]
                assert len(fichiers_mpeg) == 1, (
                    f'Source {source.pk} should have 1 MPEG file.'
                )
                fichier_mpeg = fichiers_mpeg[0]
            elif len(fichiers) == 4:
                assert len(fichiers_ogg) == 2, (
                    f'Source {source.pk} should have 2 OGG file.'
                )
                fichier_ogg = [fichier for fichier in fichiers_ogg
                               if fichier.extract_id is not None][0]
                extrait_ogg = [fichier for fichier in fichiers_ogg
                               if fichier.extract_id is None][0]
                assert len(fichiers_mpeg) == 2, (
                    f'Source {source.pk} should have 2 MPEG file.'
                )
                fichier_mpeg = [fichier for fichier in fichiers_mpeg
                                if fichier.extract_id is not None][0]
                extrait_mpeg = [fichier for fichier in fichiers_mpeg
                                if fichier.extract_id is None][0]
                kwargs.update(
                    extrait_ogg=extrait_ogg.fichier,
                    extrait_mpeg=extrait_mpeg.fichier,
                    duree_extrait=extrait_ogg.duration,
                )
                if type == VIDEO:
                    kwargs.update(
                        largeur_extrait=extrait_ogg.width,
                        hauteur_extrait=extrait_ogg.height,
                    )
            else:
                raise ValueError(
                    f'Source {source.pk} has an unexpected number '
                    f'of files: {len(fichiers)}'
                )

            kwargs.update(
                fichier_ogg=fichier_ogg.fichier,
                fichier_mpeg=fichier_mpeg.fichier,
                duree=fichier_ogg.duration,
            )
            if type == VIDEO:
                kwargs.update(
                    largeur=fichier_ogg.width,
                    hauteur=fichier_ogg.height,
                )

            model = Video if type == VIDEO else Audio
            instance = model(**kwargs)
            # Workaround to https://code.djangoproject.com/ticket/7623
            instance.save_base(raw=True)
            source.type_fichier = VIDEO if type == VIDEO else AUDIO
            source.save()
        else:
            raise ValueError(f'Unexpected type {type}.')


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0040_auto_20190830_1727'),
    ]

    operations = [
        migrations.RunPython(migrate_files),
    ]
# Generated by Django 4.1.3 on 2022-11-22 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_remove_card_face_primary_remove_card_face_secondary_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='card',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='cardownership',
            name='printing_type',
            field=models.CharField(choices=[('NORMAL', 'normal'), ('FOIL', 'foil'), ('ETCHED', 'etched')], default='normal', max_length=10),
        ),
        migrations.AddField(
            model_name='cardprice',
            name='printing_type',
            field=models.CharField(choices=[('NORMAL', 'normal'), ('FOIL', 'foil'), ('ETCHED', 'etched')], default='normal', max_length=10),
        ),
        migrations.RemoveField(
            model_name='card',
            name='printing_type',
        ),
    ]

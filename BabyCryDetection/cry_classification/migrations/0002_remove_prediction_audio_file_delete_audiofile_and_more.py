# Generated by Django 5.0 on 2024-12-15 19:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cry_classification', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prediction',
            name='audio_file',
        ),
        migrations.DeleteModel(
            name='AudioFile',
        ),
        migrations.DeleteModel(
            name='Prediction',
        ),
    ]
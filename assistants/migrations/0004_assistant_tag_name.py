# Generated by Django 5.2.2 on 2025-06-12 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistants', '0003_remove_knowledgebaseentry_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='tag_name',
            field=models.CharField(default='Neura', max_length=50, unique=True),
        ),
    ]

# Generated by Django 3.0.3 on 2020-04-04 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0013_meetingtime_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingtime',
            name='hasVoted',
            field=models.BooleanField(default=False),
        ),
    ]

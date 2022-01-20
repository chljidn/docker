# Generated by Django 3.2.7 on 2022-01-15 11:48

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='qa',
            old_name='user_id',
            new_name='qa_user',
        ),
        migrations.AddField(
            model_name='qa',
            name='qaDate',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 15, 11, 48, 36, 227784, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='QaReple',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('repleDate', models.DateTimeField(default=datetime.datetime(2022, 1, 15, 11, 48, 36, 228407, tzinfo=utc))),
                ('qa', models.ForeignKey(db_column='qa', on_delete=django.db.models.deletion.CASCADE, to='common.qa')),
                ('repleUser', models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

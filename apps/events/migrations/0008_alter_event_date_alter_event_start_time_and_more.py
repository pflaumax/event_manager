# Generated by Django 5.2.1 on 2025-06-05 12:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_alter_event_date_alter_event_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateField(help_text='Enter the date in YYYY-MM-DD format.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.TimeField(help_text='Enter the time in HH:MM format 24-hour.'),
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('registered', 'Registered'), ('cancelled', 'Cancelled')], default='registered', max_length=10)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-registered_at'],
            },
        ),
        migrations.DeleteModel(
            name='Registration',
        ),
        migrations.AddIndex(
            model_name='eventregistration',
            index=models.Index(fields=['user', 'status'], name='events_even_user_id_642524_idx'),
        ),
        migrations.AddIndex(
            model_name='eventregistration',
            index=models.Index(fields=['event', 'status'], name='events_even_event_i_cdd3f8_idx'),
        ),
        migrations.AddConstraint(
            model_name='eventregistration',
            constraint=models.UniqueConstraint(fields=('user', 'event'), name='unique_user_event_registration'),
        ),
    ]

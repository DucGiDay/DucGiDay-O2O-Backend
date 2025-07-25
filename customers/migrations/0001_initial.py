# Generated by Django 4.2.20 on 2025-06-25 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.CharField(max_length=20, unique=True)),
                ('customer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('points', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
    ]

# Generated by Django 4.1 on 2023-06-13 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wps", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="permit",
            name="remark",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="permit",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("denied", "Denied"),
                    ("approved", "Approved"),
                    ("archived", "Archived"),
                ],
                default="pending",
                max_length=128,
            ),
        ),
    ]
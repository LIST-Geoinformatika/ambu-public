# Generated by Django 4.1 on 2023-06-19 11:02

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("wps", "0012_nodeflowmeasurement_delete_waterflowmeasurement"),
    ]

    operations = [
        migrations.AddField(
            model_name="waterbodynode",
            name="geom",
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]

# Generated by Django 4.1 on 2023-06-19 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("wps", "0010_rename_watercourse_surfacewaterbody_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="WaterBodyNode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("node_id", models.PositiveBigIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name="waterflowmeasurement",
            name="gauging_station",
        ),
        migrations.AddField(
            model_name="surfacewaterbody",
            name="node1",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="swb_nodes1",
                to="wps.waterbodynode",
            ),
        ),
        migrations.AddField(
            model_name="surfacewaterbody",
            name="node2",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="swb_nodes2",
                to="wps.waterbodynode",
            ),
        ),
        migrations.AddField(
            model_name="waterflowmeasurement",
            name="node",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="water_flow_values",
                to="wps.waterbodynode",
            ),
        ),
    ]

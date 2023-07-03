import os
import random
import string
import uuid

from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos import GeometryCollection
from django.db import models

from wps.utils.storage import DataStorage
from wps.validators import (validate_monthly_json_values,
                            validate_point_within_water_body)

PERMIT_DATA_FS = DataStorage()


class NaceCode(models.Model):
    code = models.CharField(max_length=32)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class WaterUseSector(models.Model):
    name = models.CharField(max_length=128)
    geom = geomodels.PolygonField(srid=4326)

    def __str__(self):
        return self.name


class Basin(models.Model):
    name = models.CharField(max_length=128)
    geom = geomodels.PolygonField(srid=4326)

    def __str__(self):
        return self.name


class SubBasin(models.Model):
    name = models.CharField(max_length=128)
    geom = geomodels.PolygonField(srid=4326)
    basin = models.ForeignKey(Basin, null=True, on_delete=models.SET_NULL)

    @property
    def centroid(self):
        return self.geom.centroid.coords

    def __str__(self):
        return self.name


class WaterBodyNode(models.Model):
    node_id = models.PositiveBigIntegerField()
    geom = geomodels.PointField(srid=4326, null=True)

    def __str__(self):
        return 'Node - {}'.format(self.node_id)


class SurfaceWaterBody(models.Model):
    name = models.CharField(max_length=128)
    wb_code = models.CharField(max_length=128, blank=True)
    geom = geomodels.MultiLineStringField()
    buffer200 = geomodels.MultiPolygonField(srid=4326)
    node1 = models.ForeignKey(WaterBodyNode, related_name='swb_nodes1', on_delete=models.SET_NULL, blank=True, null=True)
    node2 = models.ForeignKey(WaterBodyNode, related_name='swb_nodes2', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class WaterCourseNetwork(models.Model):
    name = models.CharField(max_length=128)
    geom = geomodels.MultiLineStringField()

    def __str__(self):
        return self.name


class Wetland(models.Model):
    name = models.CharField(max_length=128)
    geom = geomodels.MultiPolygonField(srid=4326)

    def __str__(self):
        return self.name


class BaseWaterPoint(models.Model):
    identifier = models.CharField(max_length=50, unique=True, null=True, editable=False)
    geom = geomodels.PointField(srid=4326)
    subbasin = models.ForeignKey(SubBasin, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class AssessmentPoint(BaseWaterPoint):
    pass


class AbstractionPoint(BaseWaterPoint):
    approved = models.BooleanField(default=False)
    water_body = models.ForeignKey(
        SurfaceWaterBody, related_name='course_abstraction_points', on_delete=models.SET_NULL, null=True)

    @property
    def wb_code(self):
        if not self.water_body:
            return None
        return self.water_body.wb_code

    @property
    def closest_node(self):
        if not self.water_body:
            return None

        node1 = self.water_body.node1
        node2 = self.water_body.node2

        if node1 and node2:
            # Calculate the distance between the current SurfaceWaterBody and each node
            distance_node1 = self.geom.distance(node1.geom)
            distance_node2 = self.geom.distance(node2.geom)

            # Return the closer node based on distance
            if distance_node1 < distance_node2:
                return {'id': node1.id, 'node_id': node1.node_id}
            else:
                return {'id': node2.id, 'node_id': node2.node_id}

        # If only one node is present, return it
        if node1:
            return {'id': node1.id, 'node_id': node1.node_id}
        if node2:
            return {'id': node2.id, 'node_id': node2.node_id}

        # If no nodes are present, return None
        return None

    def generate_identifier(self):
        random_number = str(random.randint(10000, 99999))
        random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
        return 'AP-{}-{}'.format(random_string, random_number)

    def clean(self):
        super().clean()
        validate_point_within_water_body(self)

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.generate_identifier()
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Abstraction - {}'.format(self.id)


class DischargePoint(BaseWaterPoint):
    approved = models.BooleanField(default=False)
    water_body = models.ForeignKey(
        SurfaceWaterBody, related_name='course_discharge_points', on_delete=models.SET_NULL, null=True)

    def generate_identifier(self):
        random_number = str(random.randint(10000, 99999))
        random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
        return 'DP-{}-{}'.format(random_string, random_number)

    def clean(self):
        super().clean()
        validate_point_within_water_body(self)

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.generate_identifier()
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Discharge - {}'.format(self.id)


class WaterUse(models.Model):
    month = models.DateField()
    total_m3 = models.FloatField()
    avg_m3s = models.FloatField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.month.strftime('%Y-%m')

    class Meta:
        abstract = True


class AbstractionPointWaterUse(WaterUse):
    abstraction_point = models.ForeignKey(AbstractionPoint, related_name='ap_water_use', on_delete=models.CASCADE)


class DischargePointWaterUse(WaterUse):
    discharge_point = models.ForeignKey(DischargePoint, related_name='ap_water_use', on_delete=models.CASCADE)


def get_permit_dir(instance, filename):
    return os.path.join(str(instance.uid), filename)


class Permit(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('denied', 'Denied'),
        ('approved', 'Approved'),
        ('archived', 'Archived')
    )
    WATER_TYPE_CHOICES = (
        ('ground', 'Ground water'),
        ('surface', 'Surface water')
    )
    POINTS_TYPE_CHOICES = (
        ('abstraction', 'Abstraction'),
        ('discharge', 'Discharge'),
        ('combined', 'Combined'),
    )

    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    submitted_by = models.ForeignKey("user.User", related_name='submitted_permits', on_delete=models.CASCADE)
    submitted_on = models.DateTimeField(auto_now_add=True)
    validated_by = models.ForeignKey(
        "user.User", related_name='validated_permits', blank=True, null=True, on_delete=models.SET_NULL)
    validated_on = models.DateTimeField(blank=True, null=True)
    remark = models.TextField(blank=True)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default='pending')
    water_type = models.CharField(max_length=128, choices=WATER_TYPE_CHOICES, default='surface')
    abstraction_points = models.ManyToManyField(AbstractionPoint, blank=True, related_name='permit_abstraction_points')
    discharge_points = models.ManyToManyField(DischargePoint, blank=True, related_name='permit_discharge_points')
    points_type = models.CharField(max_length=128, choices=POINTS_TYPE_CHOICES, default='abstraction')
    operator_name = models.CharField(max_length=128)
    water_use_sector = models.ForeignKey(
        WaterUseSector, related_name='sector_permits', blank=True, null=True, on_delete=models.SET_NULL)
    nace_code = models.ForeignKey(
        NaceCode, related_name='code_permits', null=True, on_delete=models.SET_NULL)
    time_per_month = models.JSONField(blank=True, null=True)
    abstraction_m3_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    abstraction_m3s_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    discharge_m3_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    discharge_m3s_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    ev1_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    ev2_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    ev3_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    ev123_per_month = models.JSONField(blank=True, null=True, validators=[validate_monthly_json_values])
    pdf = models.FileField(max_length=255, upload_to=get_permit_dir, storage=PERMIT_DATA_FS, blank=True, null=True)

    @property
    def map_location(self):
        ap_points = [obj.geom for obj in self.abstraction_points.all()]
        dp_points = [obj.geom for obj in self.discharge_points.all()]
        all_points = ap_points + dp_points
        gc = GeometryCollection(all_points)
        return gc.centroid.coords

    def __str__(self):
        return '{} - {}'.format(self.submitted_on.strftime('%d.%m.%Y'), self.submitted_by.full_name)


class GaugingStation(models.Model):
    name = models.CharField(max_length=128)
    geom = geomodels.PointField(srid=4326)
    water_body = models.ForeignKey(
        SurfaceWaterBody, related_name='course_gauging_stations', on_delete=models.SET_NULL, null=True)
    altitude = models.FloatField(null=True)

    def __str__(self):
        return self.name


class WaterHeight(models.Model):
    gauging_station = models.ForeignKey(GaugingStation, related_name='water_height_values', on_delete=models.CASCADE)
    value = models.FloatField()
    measured_on = models.DateTimeField()

    def __str__(self):
        return '{} - {}'.format(self.measured_on.isoformat(), self.value)


class NodeFlowMeasurement(models.Model):
    node = models.ForeignKey(WaterBodyNode, related_name='water_flow_values', on_delete=models.CASCADE)
    month = models.DateField()
    q50_value = models.FloatField()
    ef_value = models.FloatField()
    wafu_value = models.FloatField()

    def __str__(self):
        return '{} - {}'.format(self.node.node_id, self.month.strftime('%Y-%m'))

from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from wps import models


@admin.register(models.NaceCode)
class NaceCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')


@admin.register(models.WaterUseSector)
class WaterUseSectorAdmin(LeafletGeoAdmin):
    list_display = ('name', )


@admin.register(models.Basin)
class BasinAdmin(LeafletGeoAdmin):
    list_display = ('name', )


@admin.register(models.SubBasin)
class SubBasinAdmin(LeafletGeoAdmin):
    list_display = ('name', 'basin')
    list_filter = ('basin', )


@admin.register(models.WaterBodyNode)
class WaterBodyNodeAdmin(LeafletGeoAdmin):
    list_display = ('node_id', )


class BaseWaterPointAdmin(LeafletGeoAdmin):
    list_display = ('identifier', 'subbasin')


@admin.register(models.AssessmentPoint)
class AssessmentPointAdmin(BaseWaterPointAdmin):
    pass


@admin.register(models.AbstractionPoint)
class AbstractionPointAdmin(BaseWaterPointAdmin):
    list_display = BaseWaterPointAdmin.list_display + ('approved', )
    list_filter = ('approved', 'water_body')


@admin.register(models.DischargePoint)
class DischargePointAdmin(BaseWaterPointAdmin):
    list_display = BaseWaterPointAdmin.list_display + ('approved', )
    list_filter = ('approved', 'water_body')


class WaterUseAdmin(admin.ModelAdmin):
    list_display = ('month', 'total_m3', 'avg_m3s', 'added_on')


@admin.register(models.AbstractionPointWaterUse)
class AbstractionPointWaterUseAdmin(WaterUseAdmin):
    list_display = ('abstraction_point', ) + WaterUseAdmin.list_display


@admin.register(models.DischargePointWaterUse)
class DischargePointWaterUseAdmin(WaterUseAdmin):
    list_display = ('discharge_point', ) + WaterUseAdmin.list_display


@admin.register(models.Permit)
class PermitAdmin(LeafletGeoAdmin):
    list_display = ('submitted_on', 'submitted_by', 'validated_on', 'validated_by', 'status')
    list_filter = ('status', 'submitted_on', 'validated_on')
    read_only_fields = ('uid', )


@admin.register(models.SurfaceWaterBody)
class SurfaceWaterBodyAdmin(LeafletGeoAdmin):
    list_display = ('name', 'node1', 'node2')


@admin.register(models.WaterCourseNetwork)
class WaterCourseNetworkAdmin(LeafletGeoAdmin):
    list_display = ('name', )


@admin.register(models.GaugingStation)
class GaugingStationAdmin(LeafletGeoAdmin):
    list_display = ('name', 'water_body')


@admin.register(models.NodeFlowMeasurement)
class NodeFlowMeasurementAdmin(LeafletGeoAdmin):
    list_display = ('node', 'month', 'q50_value', 'ef_value', 'wafu_value')
    list_filter = ('node', 'month')


@admin.register(models.Wetland)
class WetlandAdmin(LeafletGeoAdmin):
    list_display = ('name', )

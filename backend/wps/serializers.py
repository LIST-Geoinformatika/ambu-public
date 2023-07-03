from rest_framework import serializers
from user.serializers import UserSimpleSerializer

from .models import (AbstractionPoint, AbstractionPointWaterUse, Basin,
                     DischargePoint, DischargePointWaterUse, GaugingStation, WaterBodyNode,
                     NaceCode, Permit, SubBasin, SurfaceWaterBody,
                     NodeFlowMeasurement, WaterUseSector)


class NaceCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = NaceCode
        fields = ('id', 'code', 'description')


class WaterUseSectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaterUseSector
        fields = ('id', 'name', 'geom')


class BasinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basin
        fields = ('id', 'name')


class SubBasinSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubBasin
        fields = ('id', 'name', 'centroid')


class SubBasinMapSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubBasin
        fields = ('id', 'name', 'geom')


class AbstractionPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = AbstractionPoint
        fields = ('id', 'identifier', 'geom', 'water_body', 'subbasin', 'approved', 'closest_node')
        read_only_fields = ('approved', 'identifier')


class DischargePointSerializer(serializers.ModelSerializer):

    class Meta:
        model = DischargePoint
        fields = ('id', 'identifier', 'geom', 'water_body', 'subbasin', 'approved')
        read_only_fields = ('approved', 'identifier')


class AbstractionPointWaterUseSerializer(serializers.ModelSerializer):

    class Meta:
        model = AbstractionPointWaterUse
        fields = ('id', 'abstraction_point', 'month', 'total_m3', 'avg_m3s')
        read_only_fields = ('abstraction_point', )


class DischargePointWaterUseSerializer(serializers.ModelSerializer):

    class Meta:
        model = DischargePointWaterUse
        fields = ('id', 'discharge_point', 'month', 'total_m3', 'avg_m3s')
        read_only_fields = ('discharge_point', )


class PermitSerializer(serializers.ModelSerializer):

    abstraction_points = AbstractionPointSerializer(many=True)
    discharge_points = DischargePointSerializer(many=True)

    class Meta:
        model = Permit
        fields = (
            'abstraction_points', 'discharge_points', 'operator_name',
            'water_use_sector', 'water_type', 'nace_code', 'time_per_month', 'points_type',
            'abstraction_m3_per_month', 'abstraction_m3s_per_month',
            'discharge_m3_per_month', 'discharge_m3s_per_month',
            'ev1_per_month', 'ev2_per_month', 'ev3_per_month', 'ev123_per_month'
        )

    def create(self, validated_data):
        abstraction_points_data = validated_data.pop('abstraction_points')
        discharge_points_data = validated_data.pop('discharge_points')
        permit = Permit.objects.create(**validated_data)

        for ap in abstraction_points_data:
            ap_obj, _ = AbstractionPoint.objects.get_or_create(**ap)
            permit.abstraction_points.add(ap_obj)
        for dp in discharge_points_data:
            dp_obj, _ = DischargePoint.objects.get_or_create(**dp)
            permit.discharge_points.add(dp_obj)

        return permit


class PermitReadOnlySerializer(serializers.ModelSerializer):

    submitted_by = UserSimpleSerializer()
    validated_by = UserSimpleSerializer()
    water_use_sector_name = serializers.ReadOnlyField(source='water_use_sector.name')
    nace_code = NaceCodeSerializer()
    abstraction_points = AbstractionPointSerializer(many=True)
    discharge_points = DischargePointSerializer(many=True)

    class Meta:
        model = Permit
        fields = (
            'id', 'uid', 'submitted_by', 'submitted_on', 'validated_by', 'validated_on', 'map_location',
            'status', 'pdf', 'operator_name', 'points_type', 'water_use_sector', 'water_use_sector_name',
            'water_type', 'nace_code', 'pdf', 'abstraction_points', 'discharge_points'
        )


class PermitValidationSerializer(serializers.Serializer):
    status = serializers.CharField()
    remark = serializers.CharField()

    def validate(self, attrs):
        status_choices = ['approved', 'denied', 'pending', 'archived']
        if attrs['status'] not in status_choices:
            raise serializers.ValidationError({
                'status': "Allowed options are: {}".format(', '.join(status_choices))
            })

        return super(PermitValidationSerializer, self).validate(attrs)


class SurfaceWaterBodySimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SurfaceWaterBody
        fields = ('id', 'wb_code', 'name')


class GaugingStationSerializer(serializers.ModelSerializer):

    water_body = SurfaceWaterBodySimpleSerializer()

    class Meta:
        model = GaugingStation
        fields = ('id', 'name', 'geom', 'water_body', 'altitude')


class WaterBodyNodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaterBodyNode
        fields = ('id', 'node_id', 'geom')


class NodeFlowMeasurementSerializer(serializers.ModelSerializer):

    class Meta:
        model = NodeFlowMeasurement
        fields = ('id', 'node', 'month', 'q50_value', 'ef_value', 'wafu_value')
        read_only_fields = ('node', )

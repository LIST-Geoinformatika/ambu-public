
import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (AbstractionPoint, AbstractionPointWaterUse, Basin,
                     DischargePoint, DischargePointWaterUse, GaugingStation,
                     NaceCode, NodeFlowMeasurement, Permit, SubBasin,
                     SurfaceWaterBody, WaterBodyNode, WaterUseSector)
from .permissions import PermitObjectPermission, PermitValidationPermission
from .serializers import (AbstractionPointSerializer,
                          AbstractionPointWaterUseSerializer, BasinSerializer,
                          DischargePointSerializer,
                          DischargePointWaterUseSerializer,
                          GaugingStationSerializer, NaceCodeSerializer,
                          NodeFlowMeasurementSerializer,
                          PermitReadOnlySerializer, PermitSerializer,
                          PermitValidationSerializer, SubBasinMapSerializer,
                          SubBasinSerializer, SurfaceWaterBodySimpleSerializer,
                          WaterBodyNodeSerializer, WaterUseSectorSerializer)
from .utils.export import export_permit_to_xlsx


class NaceCodeList(generics.ListAPIView):
    queryset = NaceCode.objects.all()
    serializer_class = NaceCodeSerializer


class WaterUseSectorList(generics.ListAPIView):
    queryset = WaterUseSector.objects.all()
    serializer_class = WaterUseSectorSerializer


class BasinList(generics.ListAPIView):
    queryset = Basin.objects.all()
    serializer_class = BasinSerializer


class SubBasinList(generics.ListAPIView):
    serializer_class = SubBasinSerializer

    def get_queryset(self):
        basin = get_object_or_404(Basin, pk=self.kwargs['pk'])
        return SubBasin.objects.filter(basin=basin)


class SubBasinMapList(generics.ListAPIView):
    queryset = SubBasin.objects.all()
    serializer_class = SubBasinMapSerializer


class PermitList(generics.ListCreateAPIView):
    serializer_class = PermitSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ('status', 'water_type')
    search_fields = ('status', 'uid', 'nace_code__code',)
    ordering_fields = ('submitted_on', )
    ordering = ('submitted_on', )

    def get_queryset(self):
        if self.request.user.app_role_name == 'Admin':
            return Permit.objects.all()
        return Permit.objects.filter(submitted_by=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PermitReadOnlySerializer
        return self.serializer_class

    def perform_create(self, serializer):
        operator_name = serializer.validated_data.get('operator_name', self.request.user.full_name)
        serializer.save(submitted_by=self.request.user, operator_name=operator_name, status='pending')


class PermitDetail(generics.RetrieveAPIView):
    permission_class = [PermitObjectPermission]
    serializer_class = PermitSerializer
    queryset = Permit.objects.all()


class PermitXlsxExport(APIView):

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='PermitXlsxExport',
        operation_description='Export permit to xslx file.'
    )
    def get(self, request, *args, **kwargs):
        """
            Retrieve xlsx file with permit details
        """

        try:
            uid = uuid.UUID(kwargs['uid'])
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'UID is not valid'})

        obj = get_object_or_404(Permit, uid=uid)

        if not request.user.app_role_id and not obj.submitted_by == request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        output = export_permit_to_xlsx(obj)

        # Generate the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=permit_{}.xlsx'.format(uid)
        response.write(output.getvalue())

        # Return the response
        return response


class AbstractionPointList(generics.ListCreateAPIView):
    serializer_class = AbstractionPointSerializer

    def get_queryset(self):
        if self.request.user.app_role_name == 'Admin':
            return AbstractionPoint.objects.all()
        return AbstractionPoint.objects.none()


class DischargePointList(generics.ListCreateAPIView):
    serializer_class = DischargePointSerializer

    def get_queryset(self):
        if self.request.user.app_role_name == 'Admin':
            return DischargePoint.objects.all()
        return DischargePoint.objects.none()


class AbstractionPointWaterUseList(generics.ListCreateAPIView):
    serializer_class = AbstractionPointWaterUseSerializer
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ('month', )
    ordering_fields = ('month', )
    ordering = ('month', )

    def get_queryset(self):
        ap = get_object_or_404(AbstractionPoint, pk=self.kwargs['pk'])
        return AbstractionPointWaterUse.objects.filter(abstraction_point=ap)

    def perform_create(self, serializer):
        ap = get_object_or_404(AbstractionPoint, pk=self.kwargs['pk'])
        serializer.save(abstraction_point=ap)


class AbstractionPointWaterUseDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AbstractionPointWaterUseSerializer

    def get_queryset(self):
        ap = get_object_or_404(AbstractionPoint, pk=self.kwargs['ap_pk'])
        return AbstractionPointWaterUse.objects.filter(abstraction_point=ap)

    def perform_update(self, serializer):
        ap = get_object_or_404(AbstractionPoint, pk=self.kwargs['ap_pk'])
        serializer.save(abstraction_point=ap)


class DischargePointWaterUseList(generics.ListCreateAPIView):
    serializer_class = DischargePointWaterUseSerializer
    filter_backends = (filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ('month', )
    ordering_fields = ('month', )
    ordering = ('month', )

    def get_queryset(self):
        dp = get_object_or_404(DischargePoint, pk=self.kwargs['pk'])
        return DischargePointWaterUse.objects.filter(discharge_point=dp)

    def perform_create(self, serializer):
        dp = get_object_or_404(DischargePoint, pk=self.kwargs['pk'])
        serializer.save(discharge_point=dp)


class DischargePointWaterUseDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DischargePointWaterUseSerializer

    def get_queryset(self):
        dp = get_object_or_404(DischargePoint, pk=self.kwargs['dp_pk'])
        return DischargePointWaterUse.objects.filter(discharge_point=dp)

    def perform_update(self, serializer):
        dp = get_object_or_404(DischargePoint, pk=self.kwargs['dp_pk'])
        serializer.save(discharge_point=dp)


class PermitValidationView(APIView):

    renderer_classes = [JSONRenderer]
    permission_classes = [PermitValidationPermission]

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='PermitValidationView',
        operation_description='Validate the permit.',
        request_body=PermitValidationSerializer
    )
    def post(self, request, *args, **kwargs):
        try:
            uid = uuid.UUID(self.kwargs['uid'])
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'UID is not valid'})

        permit = get_object_or_404(Permit, uid=uid)
        data = request.data

        # Update permit status
        permit_status = data.get('status')
        permit.status = permit_status
        permit.remark = data.get('remark')
        permit.validated_on = timezone.now()
        permit.validated_by = request.user
        permit.save()

        # Update related APs and DPs (approved=True if permit confirmed)
        approved = True if permit_status == 'approved' else False
        for ap in permit.abstraction_points.all():
            ap.approved = approved
            ap.save()
        for dp in permit.discharge_points.all():
            dp.approved = approved
            dp.save()

        # Send email
        send_email = data.get('send_email', True)
        if send_email:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(
                settings.CHANNEL_NAME_PERMITS, {'type': 'email_permit_status_update', 'data': {'obj_id': permit.id}})

        return Response(status=status.HTTP_200_OK)


class WaterCourseList(generics.ListAPIView):
    serializer_class = SurfaceWaterBodySimpleSerializer
    queryset = SurfaceWaterBody.objects.all()


class WaterBodyLocation(APIView):

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='WaterBodyLocation',
        operation_description='Get available net flow for waterbody'
    )
    def get(self, request, *args, **kwargs):
        """
            Get matching waterbody based on lat/long
            Required params:
                - lat
                - long
        """

        params = self.request.query_params

        lon = params.get('lon')
        lat = params.get('lat')

        if not lon or not lat:
            error_msg = "'lat' and 'lon' are required as query params!"
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": error_msg})

        point = Point(float(lon), float(lat))

        water_body = SurfaceWaterBody.objects.filter(buffer200__intersects=point).first()

        if not water_body:
            res = None
        else:
            res = {'id': water_body.id, 'wb_code': water_body.wb_code, 'name': water_body.name}

        return Response(status=status.HTTP_200_OK, data=res)


class GaugingStationList(generics.ListAPIView):
    serializer_class = GaugingStationSerializer
    queryset = GaugingStation.objects.all()
    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    filterset_fields = ('water_body',)
    search_fields = ('name',)
    ordering_fields = ('name', 'water_body')
    ordering = ('name', 'water_body')


class WaterBodyNodeList(generics.ListAPIView):
    serializer_class = WaterBodyNodeSerializer
    queryset = WaterBodyNode.objects.all()


class WaterBodyNodeFlowMeasurements(generics.ListAPIView):
    serializer_class = NodeFlowMeasurementSerializer

    def get_queryset(self):
        node_obj = get_object_or_404(WaterBodyNode, pk=self.kwargs['pk'])
        return NodeFlowMeasurement.objects.filter(node=node_obj)


class WaterBodyOtherLicenses(APIView):

    @swagger_auto_schema(
        responses={'200': 'OK', '400': 'Bad Request'},
        operation_id='WaterBodyOtherLicenses',
        operation_description='Get available net flow for waterbody'
    )
    def get(self, request, *args, **kwargs):
        """
            Get available net flow for waterbody defined by <id> portion of the url.
            Required params:
                - permit_id
        """

        waterbody_obj = get_object_or_404(SurfaceWaterBody, pk=self.kwargs['pk'])
        permit_id = self.request.query_params.get('permit_id')

        if not permit_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Permit ID is required."})

        try:
            permit = Permit.objects.get(pk=permit_id)
        except AbstractionPoint.DoesNotExist:
            error_msg = "Permit with that ID doesn't exist."
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": error_msg})

        ap = permit.abstraction_points.all().first()

        # get other approved abstraction points for this waterbody
        other_aps = AbstractionPoint.objects.filter(approved=True, water_body=waterbody_obj).exclude(pk=ap.id)

        # # # get other permits based on those other abstraction points # # #

        other_permits = []

        for obj in other_aps:
            # get permits that uses this abstraction point (but exclude ref permit)
            permits = obj.permit_abstraction_points.all().exclude(pk=permit_id)
            for permit in permits:
                other_permits.append(permit)

        total_m3 = {
            '1': 0,
            '2': 0,
            '3': 0,
            '4': 0,
            '5': 0,
            '6': 0,
            '7': 0,
            '8': 0,
            '9': 0,
            '10': 0,
            '11': 0,
            '12': 0
        }

        for obj in other_permits:
            values = obj.abstraction_m3_per_month
            for k, v in values.items():
                total_m3[k] += v

        return Response(status=status.HTTP_200_OK, data=total_m3)

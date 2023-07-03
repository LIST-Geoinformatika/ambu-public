from django.urls import path

from wps import views

urlpatterns = [
    path('nace/', views.NaceCodeList.as_view(), name='nace-codes'),
    path('sectors/', views.WaterUseSectorList.as_view(), name='water-use-sectors'),
    path('basins/', views.BasinList.as_view(), name='basin-list'),
    path('basins/<int:pk>/sub-basins/', views.SubBasinList.as_view(), name='sub-basin-list'),
    path('sub-basins/', views.SubBasinMapList.as_view(), name='sub-basin-map-list'),
    path('permits/', views.PermitList.as_view(), name='permit-list'),
    path('permits/<int:pk>/', views.PermitDetail.as_view(), name='permit-detail'),
    path('permits/<str:uid>/xlsx-export/', views.PermitXlsxExport.as_view(), name='permit-xlsx-export'),
    path('permits/<str:uid>/validate/', views.PermitValidationView.as_view(), name='permit-validate'),
    path('abstraction-points/', views.AbstractionPointList.as_view(), name='abstraction-points'),
    path(
        'abstraction-points/<int:pk>/water-use/',
        views.AbstractionPointWaterUseList.as_view(),
        name='abstraction-point-water-use'),
    path(
        'abstraction-points/<int:ap_pk>/water-use/<int:pk>/',
        views.AbstractionPointWaterUseDetail.as_view(),
        name='abstraction-point-water-use-detail'),
    path(
        'discharge-points/<int:pk>/water-use/',
        views.DischargePointWaterUseList.as_view(),
        name='discharge-point-water-use'),
    path(
        'discharge-points/<int:dp_pk>/water-use/<int:pk>/',
        views.DischargePointWaterUseDetail.as_view(),
        name='discharge-point-water-use-detail'),
    path('discharge-points/', views.DischargePointList.as_view(), name='discharge-points'),
    path('water-courses/', views.WaterCourseList.as_view(), name='water-courses'),
    path('water-bodies/location/', views.WaterBodyLocation.as_view(), name='water-body-per-location'),
    path('gauging-stations/', views.GaugingStationList.as_view(), name='gauging-stations'),
    path('waterbody-nodes/', views.WaterBodyNodeList.as_view(), name='waterbody-nodes'),
    path(
        'waterbody-nodes/<int:pk>/flow-measurements/',
        views.WaterBodyNodeFlowMeasurements.as_view(),
        name='flow-measurements'),
    path(
        'waterbodies/<int:pk>/other-licenses/',
        views.WaterBodyOtherLicenses.as_view(),
        name='waterbody-other-licenses')
]

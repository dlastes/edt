from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, response, status

import roomreservation.models as rm
from api.roomreservation import serializers
from api.shared.params import week_param, year_param


@method_decorator(name='list',
                  decorator=swagger_auto_schema(
                      manual_parameters=[
                          # in the filterset
                          week_param(),
                          year_param()
                      ])
                  )
class RoomReservationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RoomReservationSerializer

    def get_queryset(self):
        all_res = rm.RoomReservation.objects.all()
        week = self.request.query_params.get('week', None)
        year = self.request.query_params.get('year', None)

        if week is not None:
            all_res = all_res.filter(date__week=week)
        if year is not None:
            all_res = all_res.filter(date__year=year)

        return all_res

    def destroy(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        data = serializer.data
        super().destroy(*args, **kwargs)
        return response.Response(data, status=status.HTTP_200_OK)

    filterset_fields = '__all__'


class RoomReservationTypeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RoomReservationTypeSerializer
    queryset = rm.RoomReservationType.objects.all()
    filterset_fields = '__all__'

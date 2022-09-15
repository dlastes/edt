from rest_framework import serializers

import api.base.rooms.serializers
import roomreservation.models as rm


class RoomReservationSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    id = serializers.IntegerField()
    responsible = serializers.CharField()
    room = serializers.IntegerField(source='room.id')
    type = serializers.IntegerField(source='reservation_type.id')
    title = serializers.CharField()
    description = serializers.CharField()
    with_key = serializers.BooleanField()
    email = serializers.BooleanField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    periodicity = serializers.IntegerField(source='periodicity.id')

    class Meta:
        model = rm.RoomReservation
        fields = '__all__'


class RoomReservationTypeSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    id = serializers.IntegerField()
    name = serializers.CharField()
    bg_color = serializers.CharField()

    class Meta:
        model = rm.RoomReservationType
        fields = '__all__'

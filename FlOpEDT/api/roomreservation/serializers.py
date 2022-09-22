from rest_framework import serializers

import roomreservation.models as rm
from base.models import Room
from people.models import User


class RoomReservationSerializer(serializers.Serializer):
    def create(self, validated_data):
        return rm.RoomReservation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.responsible = validated_data.get('responsible', instance.responsible)
        instance.room = validated_data.get('room', instance.room)
        instance.reservation_type = validated_data.get('reservation_type', instance.reservation_type)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.email = validated_data.get('email', instance.email)
        instance.date = validated_data.get('date', instance.date)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.periodicity = validated_data.get('periodicity', instance.periodicity)
        instance.save()
        return instance

    id = serializers.IntegerField(read_only=True)
    responsible = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=False)
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), many=False)
    reservation_type = serializers.PrimaryKeyRelatedField(queryset=rm.RoomReservationType.objects.all(), many=False)
    title = serializers.CharField()
    description = serializers.CharField()
    email = serializers.BooleanField()
    date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    periodicity = serializers.PrimaryKeyRelatedField(queryset=rm.ReservationPeriodicity.objects.all(), many=False)

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

from rest_framework import serializers

import roomreservation.models as rm


class RoomReservationSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        print(validated_data)
        # TODO: if 1 reservation : check if ok then create
        # TODO: if multiple reservations : check if all ok then create otherwise ask if create only ok
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

    class Meta:
        model = rm.RoomReservation
        fields = '__all__'


class RoomReservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = rm.RoomReservationType
        fields = '__all__'


class ReservationPeriodicitySerializer(serializers.Serializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = rm.ReservationPeriodicity
        fields = '__all__'

    @staticmethod
    def get_model(obj):
        if obj.periodicity_type == 'BW':
            return rm.ReservationPeriodicityByWeek
        if obj.periodicity_type == 'BM':
            return rm.ReservationPeriodicityByMonth
        if obj.periodicity_type == 'EM':
            return rm.ReservationPeriodicityEachMonthSameDate

    @staticmethod
    def get_serializer(obj):
        if obj.periodicity_type == 'BW':
            return ReservationPeriodicityByWeekSerializer
        if obj.periodicity_type == 'BM':
            return ReservationPeriodicityByMonthSerializer
        if obj.periodicity_type == 'EM':
            return ReservationPeriodicityEachMonthSameDateSerializer

    def get_data(self, obj):
        values = self.get_model(obj).objects.filter(id=obj.id)
        if len(values) == 0:
            return {}
        return self.get_serializer(obj)(values[0]).data


class ReservationPeriodicityByWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = rm.ReservationPeriodicityByWeek
        fields = '__all__'
        read_only_fields = ['periodicity_type']


class ReservationPeriodicityEachMonthSameDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = rm.ReservationPeriodicityEachMonthSameDate
        fields = '__all__'
        read_only_fields = ['periodicity_type']


class ReservationPeriodicityByMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = rm.ReservationPeriodicityByMonth
        fields = '__all__'
        read_only_fields = ['periodicity_type']

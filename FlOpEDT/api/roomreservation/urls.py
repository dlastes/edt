from rest_framework import routers
from api.roomreservation import views

routerRoomReservation = routers.SimpleRouter()

routerRoomReservation.register(r'reservation', views.RoomReservationViewSet, basename='reservation')
routerRoomReservation.register(r'reservationtype', views.RoomReservationTypeViewSet, basename='reservationtype')

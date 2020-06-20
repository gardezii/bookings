from rest_framework import serializers

from .models import Booking

class BookingSerializer(serializers.HyperlinkedModelSerializer):
		class Meta:
			model = Booking
			fields = (
				'id', 
				'name',
				'location',
				'slotKey',
				'bookingKey',
				'date',
				'duration',
				'pitch',
				'rate',
				'start',
				'end',
				'status',
				'sumittedDate'
			)

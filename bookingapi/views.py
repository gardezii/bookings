from rest_framework import viewsets
from rest_framework import status
from dateutil.parser import parse
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from rest_framework_api_key.permissions import HasAPIKey

import pytz

from .serializers import BookingSerializer
from .models import Booking

from mysite.scheduler.scheduler_jobs import TurnlightOnTask, TurnlightOffTask

class BookingViewSet(viewsets.ModelViewSet):
	queryset = Booking.objects.all().order_by('name')
	serializer_class = BookingSerializer
	scheduler = BackgroundScheduler()
	scheduler.add_jobstore(DjangoJobStore(), "default")
	scheduler.start()
	permission_classes = [HasAPIKey]


	def create(self, request, *args, **kwargs):
		booking_key = request.data["bookingKey"]

		start_date = self.formatDateAccordingToHour(request.data["date"], request.data["start"])
		end_date = self.formatDateAccordingToHour(request.data["date"], request.data["end"])

		data = self.scheduler.add_job(TurnlightOnTask, "interval", start_date=start_date, end_date=start_date, id=booking_key+"_start")
		data = self.scheduler.add_job(TurnlightOffTask, "interval", start_date=end_date, end_date=end_date, id=booking_key+"_end")
		
		return super(BookingViewSet, self).create(request, *args, **kwargs)

	def update(self, request, *args, **kwargs):
		booking_key = request.data["bookingKey"]
		
		start_date = self.formatDateAccordingToHour(request.data["date"], request.data["start"])
		start_job = self.scheduler.get_job(booking_key+"_start")
		if start_job != None:
			# removing job becasue we cannot update the starte and end date due to which 
			# we need to remove the job and create a new one
			self.scheduler.remove_job(booking_key+"_start")
			self.scheduler.add_job(TurnlightOnTask, "interval", start_date=start_date, end_date=start_date, id=booking_key+"_start")
		
		end_date = self.formatDateAccordingToHour(request.data["date"], request.data["end"])
		end_job = self.scheduler.get_job(booking_key+"_end")
		if end_job != None:
			self.scheduler.remove_job(booking_key+"_end")
			self.scheduler.add_job(TurnlightOffTask, "interval", start_date=end_date, end_date=end_date, id=booking_key+"_end")

		return super(BookingViewSet, self).update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):

		booking_key = request.data["bookingKey"]

		self.scheduler.remove_job(booking_key+"_start")
		self.scheduler.remove_job(booking_key+"_end")

		instance = self.get_object()
		self.perform_destroy(instance)

		return Response(status=status.HTTP_204_NO_CONTENT)

	def formatDateAccordingToHour(self, date, hour):
		updated_date =  self.updateHourInDateTime(date, hour)
		updated_date = self.changeDateTimeToUTC(updated_date)
		updated_date = updated_date.strftime('%Y-%m-%d %H:%M:%S')
		return updated_date


	def changeDateTimeToUTC(self, datetime_string):
		datetime_object = parse(datetime_string)
		return datetime_object.astimezone(pytz.UTC)

	def updateHourInDateTime(self, datetime_string, hour):
		udpated_hour = self.convertHourToTwentyFourHour(hour)
		date, time = datetime_string.split("T",1)
		time = str(udpated_hour)+time[2:]
		return date+"T"+time

	def convertHourToTwentyFourHour(self, hour):
		updated_hour = int(''.join([n for n in hour if n.isdigit()]))
		AMorPM = (''.join([n for n in hour if n.isalpha()])).upper()

		if AMorPM == "AM" and updated_hour== 12:
			new_hour_value = 00
		elif AMorPM == "AM":
			new_hour_value = updated_hour
		elif AMorPM == "PM" and updated_hour == 12: 
			new_hour_value = 12
		elif AMorPM == "PM":
			new_hour_value = 12 + updated_hour
        
		return new_hour_value

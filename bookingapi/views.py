from rest_framework import viewsets
from rest_framework import status

from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey


from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.schedulers.background import BackgroundScheduler

from mysite.scheduler.scheduler_jobs import TurnlightOnTask, TurnlightOffTask
from mysite.utils.http_util import get_Authorization_token
from mysite.utils.date_util import formatDateAccordingToHour

from .serializers import BookingSerializer
from .models import Booking

class BookingViewSet(viewsets.ModelViewSet):
	queryset = Booking.objects.all().order_by('name')
	serializer_class = BookingSerializer
	scheduler = BackgroundScheduler()
	scheduler.add_jobstore(DjangoJobStore(), "default")

	scheduler.start()
	permission_classes = [HasAPIKey]


	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		booking_key = request.data.get("bookingKey")
		key = get_Authorization_token(request)

		ifttt_key = APIKey.objects.get_from_key(key)

		start_date = formatDateAccordingToHour(request.data.get("date"), request.data.get("start"))
		end_date = formatDateAccordingToHour(request.data.get("date"), request.data.get("end"))

		data = self.scheduler.add_job(TurnlightOnTask, "interval", { ifttt_key }, start_date=start_date, end_date=start_date, id=booking_key+"_start")
		data = self.scheduler.add_job(TurnlightOffTask, "interval", { ifttt_key }, start_date=end_date, end_date=end_date, id=booking_key+"_end")
		
		return super(BookingViewSet, self).create(request, *args, **kwargs)

	def update(self, request, *args, **kwargs):
		if Booking.objects.filter(id = kwargs['pk']).count() == 0: 
			return Response(data={"detail": "Not found."},status=status.HTTP_404_NOT_FOUND)

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		booking_key = request.data.get("bookingKey")
		key = get_Authorization_token(request)
		
		ifttt_key = APIKey.objects.get_from_key(key)
		
		start_date = formatDateAccordingToHour(request.data.get("date"), request.data.get("start"))
		start_job = self.scheduler.get_job(booking_key+"_start")
		if start_job != None:
			# removing job becasue we cannot update the starte and end date due to which 
			# we need to remove the job and create a new one
			self.scheduler.remove_job(booking_key+"_start")
			self.scheduler.add_job(TurnlightOnTask, "interval", { ifttt_key }, start_date=start_date, end_date=start_date, id=booking_key+"_start")
		
		end_date = formatDateAccordingToHour(request.data.get("date"), request.data.get("end"))
		end_job = self.scheduler.get_job(booking_key+"_end")
		if end_job != None:
			self.scheduler.remove_job(booking_key+"_end")
			self.scheduler.add_job(TurnlightOffTask, "interval", { ifttt_key }, start_date=end_date, end_date=end_date, id=booking_key+"_end")

		return super(BookingViewSet, self).update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		if Booking.objects.filter(id = kwargs['pk']).count() == 0: 
			return Response(data={"detail": "Not found."},status=status.HTTP_404_NOT_FOUND)

		booking_key = request.data.get("bookingKey")
		if booking_key is None: 
			return Response(data={"bookingKey": ["This field is required"]},status=status.HTTP_400_BAD_REQUEST)

		if  type(booking_key) != str:
			return Response(data={"bookingKey": ["A valid string is required"]},status=status.HTTP_400_BAD_REQUEST)

		start_job = self.scheduler.get_job(booking_key+"_start")
		if start_job != None:
			self.scheduler.remove_job(booking_key+"_start")

		end_job = self.scheduler.get_job(booking_key+"_end")
		if end_job != None:
			self.scheduler.remove_job(booking_key+"_end")

		instance = self.get_object()
		self.perform_destroy(instance)

		return Response(status=status.HTTP_204_NO_CONTENT)

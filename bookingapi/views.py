from rest_framework import viewsets
from rest_framework import status

from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey

from django.utils import timezone

from mysite.scheduler.scheduler_jobs import TurnlightOnTask, TurnlightOffTask
from mysite.utils.http_util import get_Authorization_token
from mysite.utils.date_util import formatDateAccordingToHour, getDateAccordingToHour, addDays, formatDate
from core.scheduler import scheduler

from .serializers import BookingSerializer
from .models import Booking

class BookingViewSet(viewsets.ModelViewSet):
	queryset = Booking.objects.all().order_by('name')
	serializer_class = BookingSerializer

	permission_classes = [HasAPIKey]

	@staticmethod
	def get_date(request):
		start_date = getDateAccordingToHour(request.data.get("date"), request.data.get("start"))
		end_date = getDateAccordingToHour(request.data.get("date"), request.data.get("end"))
		return start_date, end_date		


	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		slot_key = request.data.get("slotKey")
		key = get_Authorization_token(request)

		ifttt_key = APIKey.objects.get_from_key(key)

		start_date, end_date = self.get_date(request)

		if (start_date < timezone.now()):
			return Response(data={"start": ["start cannot be less then current time value"]},status=status.HTTP_400_BAD_REQUEST)

		if (end_date < start_date):
			return Response(data={"end": ["end cannot be less then start"]},status=status.HTTP_400_BAD_REQUEST)

		start_date = formatDate(start_date, '%Y-%m-%d %H:%M:%S')
		scheduler.add_job(TurnlightOnTask, "interval", { ifttt_key.name, slot_key }, start_date=start_date, end_date=start_date, id=slot_key+"_start")

		end_date = formatDate(end_date, '%Y-%m-%d %H:%M:%S')
		scheduler.add_job(TurnlightOffTask, "interval", { ifttt_key.name, slot_key }, start_date=end_date, end_date=end_date, id=slot_key+"_end")
		
		return super(BookingViewSet, self).create(request, *args, **kwargs) # move it up before scheduler 

	def update(self, request, *args, **kwargs):
		if Booking.objects.filter(id = kwargs['pk'], slotKey = request.data.get("slotKey")).count() == 0: 
			return Response(data={"detail": "Not found."},status=status.HTTP_404_NOT_FOUND)
		
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		start_date, end_date = self.get_date(request)

		if (end_date < start_date):
			return Response(data={"end": ["end cannot be less then start"]},status=status.HTTP_400_BAD_REQUEST)

		slot_key = request.data.get("slotKey")
		key = get_Authorization_token(request)
		
		ifttt_key = APIKey.objects.get_from_key(key)
		
		start_job = scheduler.get_job(slot_key+"_start")
		if start_job != None:
			# removing job becasue we cannot update the starte and end date due to which 
			# we need to remove the job and create a new one
			scheduler.remove_job(slot_key+"_start")
			if start_date >= timezone.now():
				start_date = formatDate(start_date, '%Y-%m-%d %H:%M:%S')
				scheduler.add_job(TurnlightOnTask, "interval", { ifttt_key.name, slot_key }, start_date=start_date, end_date=start_date, id=slot_key+"_start")
		
		end_date = formatDate(end_date, '%Y-%m-%d %H:%M:%S')
		end_job = scheduler.get_job(slot_key+"_end")
		if end_job != None:
			scheduler.remove_job(slot_key+"_end")
			scheduler.add_job(TurnlightOffTask, "interval", { ifttt_key.name, slot_key }, start_date=end_date, end_date=end_date, id=slot_key+"_end")

		return super(BookingViewSet, self).update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		if Booking.objects.filter(id = kwargs['pk'], slotKey = request.data.get("slotKey")).count() == 0: 
			return Response(data={"detail": "Not found."},status=status.HTTP_404_NOT_FOUND)

		slot_key = request.data.get("slotKey")
		if slot_key is None: 
			return Response(data={"slotKey": ["This field is required"]},status=status.HTTP_400_BAD_REQUEST)

		if  type(slot_key) != str:
			return Response(data={"slotKey": ["A valid string is required"]},status=status.HTTP_400_BAD_REQUEST)

		start_job = self.scheduler.get_job(slot_key+"_start")
		if start_job != None:
			self.scheduler.remove_job(slot_key+"_start")

		end_job = self.scheduler.get_job(slot_key+"_end")
		if end_job != None:
			self.scheduler.remove_job(slot_key+"_end")

		instance = self.get_object()
		self.perform_destroy(instance)

		return Response(status=status.HTTP_204_NO_CONTENT)

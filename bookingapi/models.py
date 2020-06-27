from django.db import models

class Booking(models.Model): 
	name = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	slotKey = models.CharField(max_length=100)
	bookingKey = models.CharField(max_length=100)
	date = models.DateTimeField()
	duration = models.IntegerField()
	pitch = models.IntegerField()
	rate = models.IntegerField()
	start = models.CharField(max_length=30)
	end = models.CharField(max_length=30)
	status = models.CharField(max_length=30)
	sumittedDate = models.DateTimeField()

	def __str__(self):
		return self.name

class BookingSchedulerHistory(models.Model):
	job_name = models.CharField(max_length=100)
	job_type = models.CharField(max_length=100)
	slot_id = models.CharField(max_length=100)
	status = models.CharField(max_length=100)
	event_date = models.DateTimeField()

	def __str__(self):
		return self.job_name
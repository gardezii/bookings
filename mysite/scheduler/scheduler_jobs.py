import requests
from django.utils import timezone

from bookingapi.models import BookingSchedulerHistory

EVENT_TYPE = "booking_notification_trigger"

ON_EVENT =  "fibaro_on_event"
OFF_EVENT = "fibaro_off_event"

def TurnlightOffTask(ifttt_key, slot_id):
	try:
		print("Generating a turn off task notification")
		requests.post(
			'https://maker.ifttt.com/trigger/'+EVENT_TYPE+'/with/key/'+ ifttt_key, 
			params={"value1":"off_event"}
		)
		saveSchedulerHistory(ifttt_key=ifttt_key, job_type="off_event", slot_id=slot_id, status="success")
	except Exception as e: 
		print ("Something went wrong while running the off event scheduler")
		saveSchedulerHistory(ifttt_key=ifttt_key, job_type="off_event", slot_id=slot_id, status="fail")

def TurnlightOnTask(ifttt_key, slot_id):
	try: 
		print("Generating a turn on task notification")
		req = requests.post(
			'https://maker.ifttt.com/trigger/'+EVENT_TYPE+'/with/key/'+ ifttt_key, 
			params={"value1":"on_event"}
		)
		saveSchedulerHistory(ifttt_key=ifttt_key, job_type="on_event", slot_id=slot_id, status="success")
	except Exception as e:
		print ("Something went wrong while running the off event scheduler")
		saveSchedulerHistory(ifttt_key=ifttt_key, job_type="on_event", slot_id=slot_id, status="fail")


def saveSchedulerHistory(ifttt_key, job_type, slot_id, status):
	booking_history = BookingSchedulerHistory(
		job_name=ifttt_key,
		job_type=job_type,
		slot_id=slot_id,
		status="success",
		event_date=timezone.now()
	)
	booking_history.save()
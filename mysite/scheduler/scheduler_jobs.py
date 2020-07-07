import requests
from django.utils import timezone
from django.core.mail import EmailMessage

from bookingapi.models import BookingSchedulerHistory, Booking

from mysite.mail.send_mail import send_email

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

def sendLockCode(lock_id, start_date, end_date, email, slot_key): 
	print(lock_id)
	print(start_date)
	print(end_date)
	print(email)

	code = ""
	email_sent=False
	try:
		response = requests.post(
			"https://partnerapi.igloohome.co/v1/locks/"+lock_id+"/lockcodes", 
			headers={"X-IGLOOHOME-APIKEY": "0PAwT5JCJJe6KLbmJrzyLkmrA9mQDVukBcYEye", "Content-Type": "application/json"},
			json={"startDate": start_date, "endDate": end_date, "durationCode": 3, description: "lock code"}
		)
		code = response.json().code
	except Exception as e: 
		print ("Something went wrong while generating the code")
		return

	try: 
		sendEmail(email, code)
		email_sent=True
	except Exception as e:
		print("Something went wrong while sending the email")
	
		booking = Booking.object.get("slotKey", slot_key);
		booking.lock_code = code
		booking.email_sent = email_sent
		booking.save()

def sendEmail(email, code): 
	try:
		email = EmailMessage(
			"Lock Code",
			"Your lock code is: " + str(code),
			to = [email]
 		)
		email.send()
	except Exception as e:
		print (e)

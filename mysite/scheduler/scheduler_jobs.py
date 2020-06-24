import requests

EVENT_TYPE = "booking_trigger"

def TurnlightOffTask(ifttt_key):
	print("Generating a turn off task notification")
	requests.post(
		'https://maker.ifttt.com/trigger/'+EVENT_TYPE+'/with/key/'+ ifttt_key.name, 
		params={"value1":"off_event"}
	)

def TurnlightOnTask(ifttt_key):
	print("Generating a turn on task notification")
	req = requests.post(
		'https://maker.ifttt.com/trigger/'+EVENT_TYPE+'/with/key/'+ ifttt_key.name, 
		params={"value1":"on_event"}
	)
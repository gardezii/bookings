import requests

#Figure out the best way to store keys
IFTTT_KEY = "f0XkP53CR1TKOAmCbkiTCiIlekH5HpKikm3W1TEScpz"
EVENT_TYPE = "booking_trigger"

def TurnlightOffTask():
	requests.post(
		'https://maker.ifttt.com/trigger/'+EVENT_TYPE+'/with/key/'+ IFTTT_KEY, 
		params={"value1":"off_event"}
	)

def TurnlightOnTask():
	requests.post(
		'https://maker.ifttt.com/trigger/'+EVENT_TYPE+'/with/key/'+ IFTTT_KEY, 
		params={"value1":"on_event"}
	)
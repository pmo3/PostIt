######
'''JSON-related functions for PostIt App'''

#####
import GUIClasses
import json

def convert_day_to_dict(obj):
	'''convert obj(instance to Day class) 
	to a dictionary of its representation'''
	d = {'day':obj.day, 'events':[], 'position':[obj.position.x(), obj.position.y()]}
	return d

def convert_event_to_dict(event):
	'''convert instance of Event class
	to a dictionary of its representation'''
	d = {'description':str(event.getDescription()), 'priority':str(event.getPriority()), 'time':str(event.time)}
	return d

def convert_all_events(day, listOfDays, listOfDaysJSON):
	'''listofDays is calendar.py.DaysOnDisplay,
	listOfDaysJSON is calendar.py.DaysOnDisplayJSON'''
	index = listOfDays.index(day)
	templist = []
	for event in day.events:
		eventJSON = convert_event_to_dict(event)
		templist.append(eventJSON)
	listOfDaysJSON[index]['events'] = templist

def update_pos(day, pos, listOfDays, listOfDaysJSON):
	index = listOfDays.index(day)
	listOfDaysJSON[index]['position'] = [day.position.x(), day.position.y()]

def initializeJSON(LODaysToDisplay, LODaysDisplayed):
	for item in LODaysToDisplay:
		new_day = GUIClasses.Day(item['day'])
		for event in item['events']:
			new_event = GUIClasses.Event(new_day, str(event['description']), str(event['time']), str(event['priority']))
			new_day.events.append(new_event)
			new_day.displayEvents()
		convert_all_events(new_day, GUIClasses.DaysOnDisplay, GUIClasses.DaysOnDisplayJSON)
		LODaysDisplayed.append(new_day)


def save(LODaysOnDisplayJSON, size):
	data = {'SIZE':size, 'days':[]}
	data['days'] = LODaysOnDisplayJSON
	with open('settings.txt', 'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4)

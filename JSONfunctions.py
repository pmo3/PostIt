######
'''JSON-related functions for PostIt App'''

#####
import GUIClasses
import json

def convert_note_to_dict(obj):
	'''convert obj(instance to Note class) 
	to a dictionary of its representation'''
	d = {'day':obj.date, 'events':[], 'position':[obj.position.x(), obj.position.y()], 'background':[obj.background.red(), obj.background.green(), obj.background.blue()]}
	return d

def convert_event_to_dict(event):
	'''convert instance of Event class
	to a dictionary of its representation'''
	d = {'description':str(event.getDescription()), 'priority':[event.priority.red(), event.priority.green(), event.priority.blue()]}
	return d

def convert_all_events(note, listOfNotes, listOfNotesJSON):
	'''listofNotess is calendar.py.NotesOnDisplay,
	listOfNotesJSON is calendar.py.NotesOnDisplayJSON'''
	index = listOfNotes.index(note)
	templist = []
	for event in note.events:
		eventJSON = convert_event_to_dict(event)
		templist.append(eventJSON)
	listOfNotesJSON[index]['events'] = templist

def convert_RGBList_to_Color(RGBList):
	from PyQt4 import QtGui
	return QtGui.QColor(RGBList[0], RGBList[1], RGBList[2])

def update_pos(note, pos, listOfNotes, listOfNotesJSON):
	index = listOfNotes.index(note)
	listOfNotesJSON[index]['position'] = [note.position.x(), note.position.y()]

def update_background(note, color, listOfNotes, listOfNotesJSON):
	index = listOfNotes.index(note)
	listOfNotesJSON[index]['background'] = [color.red(), color.green(), color.blue()]


def save(LONotesOnDisplayJSON, size, fontsize):
	data = {'SIZE':size, 'days':[], 'FONTSIZE':fontsize}
	data['days'] = LONotesOnDisplayJSON
	with open('settings.txt', 'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4)

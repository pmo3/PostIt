import GUIClasses
import startup
import JSONfunctions
from PyQt4 import QtGui
import json
import sys

first = True

def main():
	NotesDisplayed = []
	json_data = open('settings.txt')
	data = json.load(json_data)
	GUIClasses.SIZE = data['SIZE']
	GUIClasses.FONTSIZE = data['FONTSIZE']
	NotesToDisplay = data['days']
	app = QtGui.QApplication(sys.argv)
	splash = GUIClasses.QuoteScreen()
	if len(NotesToDisplay) == 0:
		first = GUIClasses.Note()
		first.hide()
	for item in NotesToDisplay:
		new_note = GUIClasses.Note(item['day'], item['position'], item['background'])
		for event in item['events']:
			new_event = GUIClasses.Event(new_note, str(event['description']), JSONfunctions.convert_RGBList_to_Color(event['priority']))
			new_note.events.append(new_event)
			new_note.displayEvents()
		new_note.hide()
		JSONfunctions.convert_all_events(new_note, GUIClasses.NotesOnDisplay, GUIClasses.NotesOnDisplayJSON)
		NotesDisplayed.append(new_note)
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
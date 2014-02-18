######### To Do:
'''
Splash screen with quote on open.

Google Calendar Integration

 '''


from PyQt4 import QtGui, QtCore
import datetime
import sys
import json
import JSONfunctions

#define constants
SIZE = 150
FONTSIZE = '8pt'
NotesOnDisplay = []
NotesOnDisplayJSON = []

KHAKI = QtGui.QColor(240, 230, 140)
PINK = QtGui.QColor(255, 0, 255)
GREEN = QtGui.QColor(85, 255, 127) 
ORANGE = QtGui.QColor(255, 170, 0)
PURPLE = QtGui.QColor(170, 170, 255)
RED = QtGui.QColor(255, 0, 0)
LABELORANGE = QtGui.QColor(255, 140, 0)
LABELGREEN = QtGui.QColor(124, 252, 0)


class Note(QtGui.QWidget):
	def __init__(self, date=datetime.date.today(), position=[50, 50], bgColor=[240,230,140]):
		super(Note, self).__init__()
		self.position = QtCore.QPoint(position[0], position[1])
		self.date = date
		self.parent = None
		self.events = []
		self.WIDTH = SIZE
		self.HEIGHT = SIZE
		self.selected = None
		self.background = QtGui.QColor(bgColor[0], bgColor[1], bgColor[2])
		self.initUI()

	def initUI(self):
		global NotesOnDisplay
		# manage widgets
		# self.setMinimumSize(SIZE, SIZE)
		self.setStyleSheet('QWidget { font-size: %s }' % FONTSIZE)

		self.todayLabel = QtGui.QLabel(self)
		self.dateLabel = QtGui.QLabel(self)

		if type(self.date) == datetime.date:
			self.dateLabel.setText(self.formatDate(self.date))
			self.date = self.formatDate(self.date)
		else:
			self.dateLabel.setText(self.date)

		self.dateLabel.setStyleSheet('QWidget {font-size:8pt }')

		self.menuLabel = ClickableQLabel(self)
		self.menuLabel.setPixmap(QtGui.QPixmap('media\menu.png'))

		self.deleteLabel = ClickableQLabel(self)
		self.deleteLabel.setText('Delete Event')
		self.addLabel = ClickableQLabel(self)
		self.addLabel.setText('Add')

		self.deleteLabel.setStyleSheet('QWidget {font-size:8pt }')
		self.addLabel.setStyleSheet('QWidget {font-size:8pt }')

		#manage signal/slot connections
		self.connect(self, QtCore.SIGNAL('clicked()'), self.focus)
		self.connect(self, QtCore.SIGNAL('doubleClicked()'), self.addEvent)
		self.connect(self.menuLabel, QtCore.SIGNAL('clicked()'), self.setupContextMenu)
		self.connect(self.deleteLabel, QtCore.SIGNAL('clicked()'), self.deleteEvent)
		self.connect(self.addLabel, QtCore.SIGNAL('clicked()'), self.addEvent)

		# manage layouts
		self.dateLayout = QtGui.QHBoxLayout()
		self.dateLayout.addWidget(self.todayLabel)
		self.dateLayout.addStretch(1)	
		self.dateLayout.addWidget(self.menuLabel)
		self.dateLayout.addStretch(1)
		self.dateLayout.addWidget(self.dateLabel)

		self.eventLayout = QtGui.QVBoxLayout()
		for item in self.events:
			self.eventLayout.addWidget(item.getDescription())
		self.eventLayout.addStretch(1)

		self.editLayout = QtGui.QHBoxLayout()
		self.editLayout.addWidget(self.deleteLabel)
		self.editLayout.addStretch(1)
		self.editLayout.addWidget(self.addLabel)

		self.mainLayout = QtGui.QVBoxLayout()
		self.mainLayout.addLayout(self.dateLayout)
		self.mainLayout.addLayout(self.eventLayout)
		self.mainLayout.addStretch(1)
		self.mainLayout.addLayout(self.editLayout)

		self.setLayout(self.mainLayout)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.resize(self.WIDTH, self.HEIGHT)
		self.move(self.position)
		self.show()

		#initialize actions and shortcuts
		self.createActions()
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+N'), self, self.openNewNote)
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+A'), self, self.addEvent)
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+W'), self, self.delete)
		QtGui.QShortcut(QtGui.QKeySequence('F1'), self, self.changeColor(KHAKI))
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self, self.exitApp)
		QtGui.QShortcut(QtGui.QKeySequence('F2'), self, self.changeColor(PINK))
		QtGui.QShortcut(QtGui.QKeySequence('F3'), self, self.changeColor(GREEN))
		QtGui.QShortcut(QtGui.QKeySequence('F4'), self, self.changeColor(ORANGE))
		QtGui.QShortcut(QtGui.QKeySequence('F5'), self, self.changeColor(PURPLE))
		QtGui.QShortcut(QtGui.QKeySequence('F6'), self, self.changeColor('Custom'))
		QtGui.QShortcut(QtGui.QKeySequence('Del'), self, self.deleteEvent)


		NotesOnDisplay.append(self)
		NotesOnDisplayJSON.append(JSONfunctions.convert_note_to_dict(self))
		JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)

	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.draw(qp, self.background)
		qp.end()

	def draw(self, qp, color):
		qp.setBrush(color)
		qp.drawRect(0, 0, SIZE, SIZE)


	def formatDate(self, date):
		return str(date.month) + '/' + str(date.day)

	def addEvent(self):
		self.addWindow = AddMenuPopUp(self)
		#grab screen location for popup placement
		point = self.rect().center()
		globalPoint = self.mapToGlobal(point)
		self.addWindow.move(globalPoint)
		self.addWindow.resize(400, 100)
		self.addWindow.setWindowTitle('Add Event')
		self.addWindow.exec_()

	def clearLayout(self, layout):
		for i in reversed(range(layout.count())):
			item = layout.itemAt(i)
			layout.removeItem(item)

	def displayEvents(self):
		self.clearLayout(self.eventLayout)
		for item in self.events:
			self.eventLayout.addWidget(item.getLabel())

	def deleteEvent(self):
		if len(self.events) == 0:
			self.warning = QtGui.QMessageBox.information(self, 'Warning', 'There are no events to delete', QtGui.QMessageBox.Close)
			return
		if self.selected == None:
			return
		self.selected.delete()

	def focus(self):
		self.setFocus(True)

	def createActions(self):
		self.exitAction = QtGui.QAction('&Exit', self.menuLabel, triggered=self.exitApp)
		self.exitAction.setShortcut('Ctrl+Q')
		self.closeAction = QtGui.QAction('&Delete this note', self.menuLabel, triggered=self.delete)
		self.closeAction.setShortcut('Ctrl+W')
		self.newNoteAction = QtGui.QAction('&New note', self.menuLabel, triggered=self.openNewNote)
		self.newNoteAction.setShortcut('Ctrl+N')
		self.addEventAction = QtGui.QAction('&Add event', self.menuLabel, triggered=self.addEvent)
		self.addEventAction.setShortcut('Ctrl+A')
		
		self.setPink = QtGui.QAction('&Pink', self, triggered=self.changeColor(PINK), checkable=True)
		self.setGreen = QtGui.QAction('&Green', self.menuLabel, triggered=self.changeColor(GREEN), checkable=True)
		self.setOrange = QtGui.QAction('&Orange', self.menuLabel, triggered=self.changeColor(ORANGE), checkable=True)
		self.setPurple = QtGui.QAction('&Purple', self.menuLabel, triggered=self.changeColor(PURPLE), checkable=True)
		self.setDefault = QtGui.QAction('&Default', self.menuLabel, triggered=self.changeColor(KHAKI), checkable=True)
		self.setCustom = QtGui.QAction('&Custom', self.menuLabel, triggered=self.changeColor('Custom'), checkable=True)
		self.setDefault.setShortcut('F1')
		self.setPink.setShortcut('F2')
		self.setGreen.setShortcut('F3')
		self.setOrange.setShortcut('F4')
		self.setPurple.setShortcut('F5')
		self.setCustom.setShortcut('F6')

		self.setColorChecked()

		self.fontMenu = QtGui.QMenu('&Change Font Size')
		self.setFontSmall = QtGui.QAction('&Small', self, triggered=self.changeFontSize('8pt'), checkable=True)
		self.setFontMed = QtGui.QAction('&Medium', self, triggered=self.changeFontSize('10pt'), checkable=True)
		self.setFontLarge = QtGui.QAction('&Large', self, triggered=self.changeFontSize('12pt'), checkable=True)
		self.fontMenu.addAction(self.setFontSmall)
		self.fontMenu.addAction(self.setFontMed)
		self.fontMenu.addAction(self.setFontLarge)

		self.setFontChecked()

		self.sizeMenu = QtGui.QMenu('Change Size')
		self.setSizeSmall = QtGui.QAction('&Small', self, triggered=self.changeSize(150), checkable=True)
		self.setSizeMed = QtGui.QAction('&Med', self, triggered=self.changeSize(250), checkable=True)
		self.setSizeLarge = QtGui.QAction('&Large', self, triggered=self.changeSize(320), checkable=True)
		self.sizeMenu.addAction(self.setSizeSmall)
		self.sizeMenu.addAction(self.setSizeMed)
		self.sizeMenu.addAction(self.setSizeLarge)

		self.setSizeChecked()

		self.colorMenu = QtGui.QMenu('&Change Background Color')
		self.colorMenu.addAction(self.setDefault)
		self.colorMenu.addAction(self.setPink)
		self.colorMenu.addAction(self.setGreen)
		self.colorMenu.addAction(self.setOrange)
		self.colorMenu.addAction(self.setPurple)
		self.colorMenu.addAction(self.setCustom)

		#set contextmenu policy for Note
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.setupMainContextMenu)	

	def setupMainContextMenu(self):
		mainMenu = QtGui.QMenu()
		mainMenu.addAction(self.newNoteAction)
		mainMenu.addAction(self.addEventAction)
		mainMenu.addMenu(self.colorMenu)
		mainMenu.addAction(self.closeAction)
		mainMenu.exec_(QtGui.QCursor.pos())	

	def setupContextMenu(self):
		menu = QtGui.QMenu()
		point = self.menuLabel.rect().topLeft()
		
		menu.addAction(self.newNoteAction)
		menu.addAction(self.addEventAction)
		menu.addMenu(self.colorMenu)
		menu.addMenu(self.fontMenu)
		menu.addMenu(self.sizeMenu)
		menu.addAction(self.closeAction)
		menu.addAction(self.exitAction)
		menu.exec_(self.menuLabel.mapToGlobal(point))

	def openNewNote(self):
		self.new = Note(datetime.date.today())
		self.new.resize(self.WIDTH, self.HEIGHT)
		self.new.show()


	def changeColor(self, col):
		def callback():
			color = col
			if color == "Custom":
				color = QtGui.QColorDialog.getColor()
			if color.isValid():
				for event in self.events:
					if self.background == event.priority:
						event.priority = color
						event.eventLabel.setStyleSheet("QWidget { background-color: % s }" % color.name())				
				self.background = color
				self.repaint()
				JSONfunctions.update_background(self, color, NotesOnDisplay, NotesOnDisplayJSON)
				JSONfunctions.convert_all_events(self, NotesOnDisplay, NotesOnDisplayJSON)
				JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)
				self.setColorChecked()
		return callback

	def setColorChecked(self):
		actions = [self.setPink, self.setGreen, self.setOrange, self.setPurple, self.setDefault, self.setCustom]
		for action in actions:
			action.setChecked(False)
		if self.background == PINK:
			self.setPink.setChecked(True)
		elif self.background == GREEN:
			self.setGreen.setChecked(True)
		elif self.background == ORANGE:
			self.setOrange.setChecked(True)
		elif self.background == PURPLE:
			self.setPurple.setChecked(True)
		elif self.background == KHAKI:
			self.setDefault.setChecked(True)
		else:
			self.setCustom.setChecked(True)

	def changeSize(self, size):
		def callback():
			global SIZE
			SIZE = size
			self.resize(SIZE, SIZE)
			self.repaint()
			self.setSizeChecked()
		return callback

	def setSizeChecked(self):
		actions = [self.setSizeSmall, self.setSizeMed, self.setSizeLarge]
		for action in actions:
			action.setChecked(False)
		if SIZE == 150:
			self.setSizeSmall.setChecked(True)
		elif SIZE == 250:
			self.setSizeMed.setChecked(True)
		elif SIZE == 320:
			self.setSizeLarge.setChecked(True)


	def changeFontSize(self, size):
		def callback():
			global FONTSIZE
			FONTSIZE = size
			self.setStyleSheet('QWidget {font-size: %s }' % FONTSIZE)
			JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)
			self.setFontChecked()
		return callback

	def setFontChecked(self):
		actions = [self.setFontLarge, self.setFontMed, self.setFontSmall]
		for action in actions:
			action.setChecked(False)
		if FONTSIZE == '8pt':
			self.setFontSmall.setChecked(True)
		elif FONTSIZE == '10pt':
			self.setFontMed.setChecked(True)
		elif FONTSIZE == '12pt':
			self.setFontLarge.setChecked(True)

	#emit mouse event signals
	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))
		if self.__mousePressPos is not None:
			moved = event.globalPos() - self.__mousePressPos
			self.position = QtGui.QCursor.pos()
			JSONfunctions.update_pos(self, self.position, NotesOnDisplay, NotesOnDisplayJSON)
			JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)
			if moved.manhattanLength() > 3:
				event.ignore()
				return
		

	def mouseDoubleClickEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('doubleClicked()'))

	def mousePressEvent(self, event):
		self.__mousePressPos = None
		self.__mouseMovePos = None
		if event.button() == QtCore.Qt.LeftButton:
			self.__mousePressPos = event.globalPos()
			self.__mouseMovePos = event.globalPos()

	def mouseMoveEvent(self, event):
		if event.buttons() == QtCore.Qt.LeftButton:
			#adjust offset from clicked point to origin of widget
			currPos = self.mapToGlobal(self.pos())
			globalPos = event.globalPos()
			diff = globalPos - self.__mouseMovePos
			newPos = self.mapFromGlobal(currPos + diff)
			self.move(newPos)

			self.__mouseMovePos = globalPos

	def delete(self):
		if len(NotesOnDisplay) == 1:
			index = NotesOnDisplay.index(self)
			del NotesOnDisplayJSON[index]
			del NotesOnDisplay[index]
			self.hide()
			self.deleteLater()
			JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)
			self.exitApp()
		else:
			index = NotesOnDisplay.index(self)
			del NotesOnDisplayJSON[index]
			del NotesOnDisplay[index]
			self.hide()
			self.deleteLater()
			JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)			

	def exitApp(self):
		JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)		
		sys.exit()

	def __repr__(self):
		return '<Day(%s)>' % self.date


# extend label class to overwrite certain events
class ClickableQLabel(QtGui.QLabel):
	def __init__(self, parent):
		QtGui.QLabel.__init__(self, parent)

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))

	def mouseDoubleClickEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('doubleClicked()'))

	def focusInEvent(self, event):
		self.emit(QtCore.SIGNAL('focusIn()'))

	def focusOutEvent(self, event):
		self.emit(QtCore.SIGNAL('focusOut()'))

class Event(QtGui.QWidget):
	def __init__(self, note, description, priority=None):
		super(Event, self).__init__()
		self.note = note
		self.description = description
		ColorDictionary = {'High':RED, "Medium":LABELORANGE,
				'Low':LABELGREEN, 'Choose a Priority':self.note.background}

		if type(priority) == QtGui.QColor:
			self.priority = priority
		else:
			self.priority = ColorDictionary[priority]
		self.col = self.note.background
		self.selected = False
		self.initUI()

	def initUI(self):
		self.setStyleSheet('QWidget { font-size: %s }' % FONTSIZE)
		self.initLabelUI(self.description)

		self.setPriority(self.priority)

		self.createActions()

# define methods
	def getDescription(self):
		return self.description

	def getPriority(self):
		return self.priority

	def getLabel(self):
		return self.eventLabel

	def initLabelUI(self, text):
		self.eventLabel = ClickableQLabel(self.note)
		self.eventLabel.setText(text)
		self.eventLabel.setToolTip('Double click to edit')
		self.eventLabel.setWordWrap(True)

		# connect signals and slots for events
		self.connect(self.eventLabel, QtCore.SIGNAL('doubleClicked()'), self.beginEditAct)
		self.connect(self.eventLabel, QtCore.SIGNAL('clicked()'), self.setFocus)
		self.connect(self.eventLabel, QtCore.SIGNAL('focusIn()'), self.outlineLabel)
		self.connect(self.eventLabel, QtCore.SIGNAL('focusOut()'), self.deleteOutline)
		self.eventLabel.setFocusPolicy(QtCore.Qt.StrongFocus)


	def setPriority(self, color):
		if color == 'Custom':
			self.priority = QtGui.QColorDialog.getColor()
		if color == 'None' or color == 'Choose a Priority':
			self.priority = self.note.background
		else:
			self.priority = color
		if self.priority.isValid():	
			self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.priority.name())
			JSONfunctions.convert_all_events(self.note, NotesOnDisplay, NotesOnDisplayJSON)
			JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)

	def beginEditAct(self):
		index = self.note.eventLayout.indexOf(self.eventLabel)
		self.eventLabel.deleteLater()
		self.eventLabel = QtGui.QLineEdit(self.eventLabel.text())
		self.eventLabel.returnPressed.connect(self.finishEditAct)
		self.note.events[index] = self
		self.note.displayEvents()

	def finishEditAct(self):
		index = self.note.eventLayout.indexOf(self.eventLabel)
		text = self.eventLabel.text()
		if text == '':
			self.delete()
			return
		self.eventLabel.deleteLater()
		self.initLabelUI(text)
		self.description = text
		self.setPriority(self.priority)
		self.note.events[index] = self
		self.createActions()
		self.note.displayEvents()
		JSONfunctions.convert_all_events(self.note, NotesOnDisplay, NotesOnDisplayJSON)
		JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)

	def createActions(self):
		self.eventLabel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.eventLabel.customContextMenuRequested.connect(self.setupContextMenu)
		self.setPriorityHighAct = QtGui.QAction('&High', self.eventLabel, triggered=self.resetPriority(RED))
		self.setPriorityMediumAct = QtGui.QAction('&Medium', self.eventLabel, triggered=self.resetPriority(LABELORANGE))
		self.setPriorityLowAct = QtGui.QAction('&Low', self.eventLabel, triggered=self.resetPriority(LABELGREEN))
		self.setPriorityCustomAct = QtGui.QAction('&Custom', self.eventLabel, triggered=self.resetPriority('Custom'))
		self.setPriorityNoneAct = QtGui.QAction('&None', self.eventLabel, triggered=self.resetPriority(self.note.background))
		self.deleteAction = QtGui.QAction('&Delete Event', self.eventLabel, triggered=self.delete)

	def setupContextMenu(self, point):
		menu = QtGui.QMenu()
		priorityMenu = QtGui.QMenu('&Edit Priority')
		priorityMenu.addAction(self.setPriorityHighAct)
		priorityMenu.addAction(self.setPriorityMediumAct)
		priorityMenu.addAction(self.setPriorityLowAct)
		priorityMenu.addAction(self.setPriorityCustomAct)
		priorityMenu.addAction(self.setPriorityNoneAct)

		menu.addAction(self.deleteAction)

		menu.addMenu(priorityMenu)
		menu.exec_(self.eventLabel.mapToGlobal(point))


	def resetPriority(self, priority):
		def callback():
			self.setPriority(priority)
		return callback

	def delete(self):
		self.eventLabel.deleteLater()
		self.note.events.remove(self)
		self.note.displayEvents()
		JSONfunctions.convert_all_events(self.note, NotesOnDisplay, NotesOnDisplayJSON)
		JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)
	def focus(self):
		self.eventLabel.setFocus(True)

	def outlineLabel(self):
			self.eventLabel.setStyleSheet("QWidget { border-style: dotted; border-width: 2px; background-color: %s }" % self.priority.name())
			self.selected = True
			self.note.selected = self


	def deleteOutline(self):
		self.eventLabel.setStyleSheet("QWidget { border-width: 0px }")
		self.selected = False
		self.note.selected = None
		self.setPriority(self.priority)

class AddMenuPopUp(QtGui.QDialog):
	def __init__(self, note):
		QtGui.QWidget.__init__(self)
		self.note = note
		self.initUI()

	def initUI(self):
		
		self.enterLabel = QtGui.QLabel(self)
		self.enterLabel.setText('Enter Description')

		self.enterText = QtGui.QLineEdit(self)

		self.enterLayout = QtGui.QHBoxLayout()
		self.enterLayout.setSpacing(15)
		self.enterLayout.addWidget(self.enterLabel)
		self.enterLayout.addWidget(self.enterText)


		self.prioritySelector = QtGui.QComboBox(self)
		self.prioritySelector.addItems(['Choose a Priority', 'High', 'Medium', 'Low'])


		self.addButton = QtGui.QPushButton('Add Event')
		self.connect(self.addButton, QtCore.SIGNAL('clicked()'), self.AddEvent)
		self.cancelButton = QtGui.QPushButton('Cancel')
		self.connect(self.cancelButton, QtCore.SIGNAL('clicked()'), self.cancel)

		self.buttonLayout = QtGui.QHBoxLayout()
		self.buttonLayout.setSpacing(15)
		self.buttonLayout.addWidget(self.addButton)
		self.buttonLayout.addWidget(self.cancelButton)


		self.mainLayout = QtGui.QVBoxLayout()
		self.setLayout(self.mainLayout)
		self.mainLayout.addLayout(self.enterLayout)
		self.mainLayout.addWidget(self.prioritySelector)
		self.mainLayout.addLayout(self.buttonLayout)


## define methods
	def cancel(self):
		self.reject()

	def AddEvent(self):
		description = self.enterText.text()
		if description == '':
			self.warning = QtGui.QMessageBox.information(self, 'Warning', 'You must enter a description', QtGui.QMessageBox.Close)
			return
		priority = str(self.prioritySelector.currentText())
		newEvent = Event(self.note, description, priority)
		self.note.events.append(newEvent)
		self.note.displayEvents()
		JSONfunctions.convert_all_events(self.note, NotesOnDisplay, NotesOnDisplayJSON)
		JSONfunctions.save(NotesOnDisplayJSON, SIZE, FONTSIZE)	
		self.accept()


def main():
	global SIZE, FONTSIZE
	NotesDisplayed = [] #keeps reference to newly created notes so they actually show on
	json_data = open('settings.txt')
	data = json.load(json_data)
	SIZE = data['SIZE']
	FONTSIZE = data['FONTSIZE']
	NotesToDisplay = data['days']
	app = QtGui.QApplication(sys.argv)
	if len(NotesToDisplay) == 0:
		first = Note()
	for item in NotesToDisplay:
		new_day = Note(item['day'], item['position'], item['background'])
		for event in item['events']:
			new_event = Event(new_day, str(event['description']), JSONfunctions.convert_RGBList_to_Color(event['priority']))
			new_day.events.append(new_event)
			new_day.displayEvents()
		JSONfunctions.convert_all_events(new_day, NotesOnDisplay, NotesOnDisplayJSON)
		NotesDisplayed.append(new_day)
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

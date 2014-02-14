from PyQt4 import QtGui, QtCore
import datetime
import sys
import json
import JSONfunctions

#define constants
SIZE = 150
DaysOnDisplay = []
DaysOnDisplayJSON = []


class Day(QtGui.QWidget):
	def __init__(self, day, position=[50, 50]):
		''' day is int[0,4], where 0 is today,
		1 is next day, etc'''
		super(Day, self).__init__()
		self.day = day
		self.position = QtCore.QPoint(position[0], position[1])
		self.date = datetime.date.today()
		self.parent = None
		self.events = []
		self.WIDTH = SIZE
		self.HEIGHT = SIZE
		self.selected = None
		self.background = Event.KHAKI
		self.initUI()

	def initUI(self):
		global DaysOnDisplay
		# manage widgets
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self.setStyleSheet('QWidget { font-size: 8pt }')

		self.todayLabel = QtGui.QLabel(self)
		self.dateLabel = QtGui.QLabel(self)

		if self.day == 0:
			self.todayLabel.setText('Today')
			self.dateLabel.setText(self.formatDate(self.day))
		else:
			self.todayLabel.setText('')
			self.dateLabel.setText('')

		self.menuLabel = ClickableQLabel(self)
		self.menuLabel.setPixmap(QtGui.QPixmap('media\menu.png'))

		self.deleteLabel = ClickableQLabel(self)
		self.deleteLabel.setText('Delete Event')
		self.addLabel = ClickableQLabel(self)
		self.addLabel.setText('Add')

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
		QtGui.QShortcut(QtGui.QKeySequence('F1'), self, self.changeColor)
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self, self.exitApp)

		DaysOnDisplay.append(self)
		DaysOnDisplayJSON.append(JSONfunctions.convert_day_to_dict(self))
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)



	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.draw(qp, self.background)
		qp.end()

	def draw(self, qp, color):
		qp.setBrush(color) #khaki
		qp.drawRect(0, 0, self.WIDTH, self.HEIGHT)


	def formatDate(self, day):
		date = datetime.date.today() + datetime.timedelta(days=day)
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
		self.closeAction = QtGui.QAction('&Delete this note', self.menuLabel, triggered=self.delete)
		self.newNoteAction = QtGui.QAction('&New note', self.menuLabel, triggered=self.openNewNote)
		self.addEventAction = QtGui.QAction('&Add event', self.menuLabel, triggered=self.addEvent)
		self.changeColorAction = QtGui.QAction('&Change Background Color', self.menuLabel, triggered=self.changeColor)
		actionsList = [self.exitAction, self.closeAction, self.newNoteAction, self.addEventAction, self.changeColorAction]
		return actionsList

	def setupContextMenu(self):
		menu = QtGui.QMenu()
		point = self.menuLabel.rect().topLeft()
		
		# add actions
		for action in self.createActions():
			menu.addAction(action)
		menu.exec_(self.menuLabel.mapToGlobal(point))

	def openNewNote(self):
		self.new = Day(0)
		self.new.resize(self.WIDTH, self.HEIGHT)
		self.new.show()


	def changeColor(self):
		col = QtGui.QColorDialog.getColor()
		if col.isValid():
			self.background = col
			self.repaint()
			for event in self.events:
				event.eventLabel.setStyleSheet("QWidget { background-color: % s }" % col.name())


	#emit mouse event signals
	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))
		if self.__mousePressPos is not None:
			moved = event.globalPos() - self.__mousePressPos
			self.position = QtGui.QCursor.pos()
			JSONfunctions.update_pos(self, self.position, DaysOnDisplay, DaysOnDisplayJSON)
			JSONfunctions.save(DaysOnDisplayJSON, SIZE)
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
		if len(DaysOnDisplay) == 1:
			index = DaysOnDisplay.index(self)
			del DaysOnDisplayJSON[index]
			del DaysOnDisplay[index]
			self.hide()
			self.deleteLater()
			JSONfunctions.save(DaysOnDisplayJSON, SIZE)
			self.exitApp()
		else:
			index = DaysOnDisplay.index(self)
			del DaysOnDisplayJSON[index]
			del DaysOnDisplay[index]
			self.hide()
			self.deleteLater()
			JSONfunctions.save(DaysOnDisplayJSON, SIZE)
			

	def exitApp(self):
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)
		sys.exit()

	def __repr__(self):
		return '<Day(%s)>' % self.day


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

	# define colors for priority tags
	KHAKI = QtGui.QColor(240, 230, 140)
	RED = QtGui.QColor(255, 0, 0)
	ORANGE = QtGui.QColor(255, 140, 0)
	GREEN = QtGui.QColor(124, 252, 0)

	def __init__(self, day, description, time=None, priority=None):
		super(Event, self).__init__()
		self.day = day
		self.time = time
		self.description = description
		self.priority = priority
		self.col = Event.KHAKI
		self.selected = False
		self.initUI()

	def initUI(self):
		self.initLabelUI(self.formatForDisplay())

		self.setPriority()

		self.createActions()

# define methods
	def getDescription(self):
		return self.description

	def getPriority(self):
		return self.priority

	def getLabel(self):
		return self.eventLabel

	def formatForDisplay(self):
		if self.time == None:
			timeDisplay = ''
		else:
			timeDisplay = str(self.time[0:-6]) + ' - '
		return timeDisplay + str(self.getDescription())

	def initLabelUI(self, text):
		self.eventLabel = ClickableQLabel(self.day)
		self.eventLabel.setText(text)
		self.eventLabel.setToolTip('Double click to edit')
		self.eventLabel.setWordWrap(True)

		# connect signals and slots for events
		self.connect(self.eventLabel, QtCore.SIGNAL('doubleClicked()'), self.beginEditAct)
		self.connect(self.eventLabel, QtCore.SIGNAL('clicked()'), self.setFocus)
		self.connect(self.eventLabel, QtCore.SIGNAL('focusIn()'), self.outlineLabel)
		self.connect(self.eventLabel, QtCore.SIGNAL('focusOut()'), self.deleteOutline)
		self.eventLabel.setFocusPolicy(QtCore.Qt.StrongFocus)


	def setPriority(self):
		if self.priority == 'High':
			self.col = Event.RED
		elif self.priority == "Medium":
			self.col = Event.ORANGE
		elif self.priority == "Low":
			self.col = Event.GREEN
		else:
			self.col = Event.KHAKI
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())

	def beginEditAct(self):
		index = self.day.eventLayout.indexOf(self.eventLabel)
		self.eventLabel.deleteLater()
		self.eventLabel = QtGui.QLineEdit(self.eventLabel.text())
		self.eventLabel.returnPressed.connect(self.finishEditAct)
		self.day.events[index] = self
		self.day.displayEvents()

	def finishEditAct(self):
		index = self.day.eventLayout.indexOf(self.eventLabel)
		text = self.eventLabel.text()
		self.eventLabel.deleteLater()
		self.initLabelUI(text)
		self.setPriority()
		self.day.events[index] = self
		self.createActions()
		self.day.displayEvents()
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)


	def createActions(self):
		self.eventLabel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.eventLabel.customContextMenuRequested.connect(self.setupContextMenu)
		self.setPriorityHighAct = QtGui.QAction('High', self.eventLabel, triggered=self.setPriorityHigh)
		self.setPriorityMediumAct = QtGui.QAction('Medium', self.eventLabel, triggered=self.setPriorityMed)
		self.setPriorityLowAct = QtGui.QAction('Low', self.eventLabel, triggered=self.setPriorityLow)
		self.setPriorityNoneAct = QtGui.QAction('None', self.eventLabel, triggered=self.setPriorityNone)
		self.deleteAction = QtGui.QAction('Delete Event', self.eventLabel, triggered=self.delete)

	def setupContextMenu(self, point):
		menu = QtGui.QMenu()
		priorityMenu = QtGui.QMenu('Edit Priority')
		priorityMenu.addAction(self.setPriorityHighAct)
		priorityMenu.addAction(self.setPriorityMediumAct)
		priorityMenu.addAction(self.setPriorityLowAct)
		priorityMenu.addAction(self.setPriorityNoneAct)

		menu.addAction(self.deleteAction)

		menu.addMenu(priorityMenu)
		menu.exec_(self.eventLabel.mapToGlobal(point))

	def setPriorityHigh(self):
		self.priority = 'High'
		self.col = Event.RED
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)

	def setPriorityMed(self):
		self.priority = 'Medium'
		self.col = Event.ORANGE
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())	
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)

	def setPriorityLow(self):
		self.priority = 'Low'
		self.col = Event.GREEN
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)

	def setPriorityNone(self):
		self.priority = None
		self.col = Event.KHAKI
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)

	def delete(self):
		self.eventLabel.deleteLater()
		self.day.events.remove(self)
		self.day.displayEvents()
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)

	def focus(self):
		self.eventLabel.setFocus(True)

	def outlineLabel(self):
			self.eventLabel.setStyleSheet("QWidget { border-style: dotted; border-width: 2px; background-color: %s }" % self.col.name())
			self.selected = True
			self.day.selected = self


	def deleteOutline(self):
		self.eventLabel.setStyleSheet("QWidget { border-width: 0px }")
		self.selected = False
		self.day.selected = None
		self.setPriority()

class AddMenuPopUp(QtGui.QDialog):
	def __init__(self, day):
		QtGui.QWidget.__init__(self)
		self.day = day
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
		else:
			time = None
		
		priority = self.prioritySelector.currentText()
		newEvent = Event(self.day, description, time, priority)
		self.day.events.append(newEvent)
		self.day.displayEvents()
		JSONfunctions.convert_all_events(self.day, DaysOnDisplay, DaysOnDisplayJSON)
		JSONfunctions.save(DaysOnDisplayJSON, SIZE)	
		self.accept()


def main():
	global SIZE
	DaysDisplayed = [] #keeps reference to newly created days so they actually show on
	json_data = open('settings.txt')
	data = json.load(json_data)
	SIZE = data['SIZE']
	DaysToDisplay = data['days']
	app = QtGui.QApplication(sys.argv)
	for item in DaysToDisplay:
		new_day = Day(item['day'], item['position'])
		for event in item['events']:
			new_event = Event(new_day, str(event['description']), str(event['time']), str(event['priority']))
			new_day.events.append(new_event)
			new_day.displayEvents()
		JSONfunctions.convert_all_events(new_day, DaysOnDisplay, DaysOnDisplayJSON)
		DaysDisplayed.append(new_day)
	ex = Day(0)
	sys.exit(app.exec_())
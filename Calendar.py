from PyQt4 import QtGui, QtCore
import datetime
import sys

class Day(QtGui.QWidget):
	def __init__(self, day, parent):
		''' day is int[0,4], where 0 is today,
		1 is next day, etc'''
		super(Day, self).__init__()
		self.day = day
		self.parent = parent
		self.events = []
		self.WIDTH = 150
		self.HEIGHT = 150
		self.selected = None
		self.initUI()

	def initUI(self):
		
		# manage widgets
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self.setStyleSheet('QWidget { font-size: 8pt }')
		self.setParent(self.parent)

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
		self.deleteLabel.setText('Delete')
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
		self.resize(150, 150)
		self.show()

		#initialize actions and shortcuts
		self.createActions()
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+N'), self, self.openNewNote)
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+A'), self, self.addEvent)
		QtGui.QShortcut(QtGui.QKeySequence('Ctrl+W'), self, self.parent.close)


	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.draw(qp)
		qp.end()

	def draw(self, qp):
		qp.setBrush(QtGui.QColor(240,230,140)) #khaki
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
		self.exitAction = QtGui.QAction('&Exit', self.menuLabel, triggered=sys.exit)
		self.closeAction = QtGui.QAction('&Close this note', self.menuLabel, triggered=self.parent.close)
		self.newNoteAction = QtGui.QAction('&New note', self.menuLabel, triggered=self.openNewNote)
		self.addEventAction = QtGui.QAction('&Add event', self.menuLabel, triggered=self.addEvent)
		actionsList = [self.exitAction, self.closeAction, self.newNoteAction, self.addEventAction]
		return actionsList

	def setupContextMenu(self):
		menu = QtGui.QMenu()
		point = self.menuLabel.rect().topLeft()
		
		# add actions
		for action in self.createActions():
			menu.addAction(action)
		menu.exec_(self.menuLabel.mapToGlobal(point))

	def openNewNote(self):
		self.new = SingleDayDisplay(None)
		self.new.resize(150, 150)
		self.new.show()

	#emit mouse event signals
	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))

	def mouseDoubleClickEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('doubleClicked()'))



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

	def setPriorityMed(self):
		self.priority = 'Medium'
		self.col = Event.ORANGE
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())	

	def setPriorityLow(self):
		self.priority = 'Low'
		self.col = Event.GREEN
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())

	def setPriorityNone(self):
		self.priority = None
		self.col = Event.KHAKI
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())

	def delete(self):
		self.eventLabel.deleteLater()
		self.day.events.remove(self)
		self.day.displayEvents()

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
		self.timeCheckbox = QtGui.QCheckBox('Include Time?', self)

		self.timeEdit = QtGui.QTimeEdit(self)

		self.timeLayout = QtGui.QHBoxLayout()
		self.timeLayout.setSpacing(15)
		self.timeLayout.addWidget(self.timeCheckbox)
		self.timeLayout.addWidget(self.timeEdit)
		
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
		self.mainLayout.addLayout(self.timeLayout)
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
		if self.timeCheckbox.checkState() == 2:
			time = self.timeEdit.text()
		else:
			time = None
		
		priority = self.prioritySelector.currentText()
		newEvent = Event(self.day, description, time, priority)
		self.day.events.append(newEvent)
		self.day.displayEvents()
		self.accept()


class SingleDayDisplay(QtGui.QWidget):
	def __init__(self, day):
		super(SingleDayDisplay, self).__init__()
		self.day = day
		self.initUI()

	def initUI(self):
		self.day1 = Day(self.day, self)
		
		#manage layout
		self.layout = QtGui.QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.addWidget(self.day1)
		self.setLayout(self.layout)
		self.layout.setContentsMargins(0,0,0,0)

		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.resize(150, 150)
		self.show()

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

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))
		if self.__mousePressPos is not None:
			moved = event.globalPos() - self.__mousePressPos
			if moved.manhattanLength() > 3:
				event.ignore()
				return

	def close(self):
		self.hide()

def main():
	app = QtGui.QApplication(sys.argv)
	ex = SingleDayDisplay(0)
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

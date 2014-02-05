from PyQt4 import QtGui, QtCore
import datetime
import sys

class Day(QtGui.QWidget):
	def __init__(self, day):
		''' day is int[0,4], where 0 is today,
		1 is next day, etc'''
		super(Day, self).__init__()
		self.day = day
		self.events = []
		self.WIDTH = 150
		self.HEIGHT = 150
		self.selected = None
		self.initUI()

	def initUI(self):
		self.setMinimumSize(self.WIDTH, self.HEIGHT)
		self.setStyleSheet('QWidget { font-size: 8pt }')
		self.dateLayout = QtGui.QHBoxLayout()
		self.mainLayout = QtGui.QVBoxLayout()
		self.connect(self, QtCore.SIGNAL('clicked()'), self.focus)

		if self.day == 0:
			self.todayLabel = QtGui.QLabel(self)
			self.todayLabel.setText('Today')
		else:
			self.todayLabel = QtGui.QLabel(self)
			self.todayLabel.setText('')

		self.dateLayout.addWidget(self.todayLabel)
		self.dateLayout.addStretch(1)


		self.dateLabel = QtGui.QLabel(self)
		self.dateLabel.setText(self.formatDate(self.day))
		self.dateLayout.addWidget(self.dateLabel)

		self.deleteLabel = ClickableQLabel(self)
		self.deleteLabel.setText('Delete')
		self.connect(self.deleteLabel, QtCore.SIGNAL('clicked()'), self.deleteEvent)

		self.addLabel = ClickableQLabel(self)
		self.addLabel.setText('Add')
		self.connect(self.addLabel, QtCore.SIGNAL('clicked()'), self.addEvent)


		self.eventLayout = QtGui.QVBoxLayout()
		for item in self.events:
			self.eventLayout.addWidget(item.getDescription())
		self.eventLayout.addStretch(1)

		self.editLayout = QtGui.QHBoxLayout()
		self.editLayout.addWidget(self.deleteLabel)
		self.editLayout.addStretch(1)
		self.editLayout.addWidget(self.addLabel)

		self.mainLayout.addLayout(self.dateLayout)
		self.mainLayout.addLayout(self.eventLayout)
		self.mainLayout.addStretch(1)
		self.mainLayout.addLayout(self.editLayout)

		self.setLayout(self.mainLayout)
		self.show()

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

	def focusInEvent(self, event):
		self.selected = None

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))

	def focus(self):
		self.setFocus(True)

class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		self.numberOfDays = 0
		self.initUI()

	def initUI(self):
		#to do: how to properly load these images from media directory
		exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit Application')
		exitAction.triggered.connect(QtGui.qApp.quit)

		self.menubar = self.menuBar()
		self.fileMenu = self.menubar.addMenu('&File')
		self.fileMenu.addAction(exitAction)
		#self.menubar.hide()


		# currently only supports display of one day
		day1 = Day(0)
		self.numberOfDays += 1
		# day2 = Day(1)
		# self.numberOfDays += 1
		# day3 = Day(2)
		# self.numberOfDays += 1
		# day4 = Day(3)
		# self.numberOfDays += 1
		# day5 = Day(4)
		# self.numberOfDays += 1

		cwidget = QtGui.QWidget(self)
		self.setCentralWidget(cwidget)
		cwidget.setWindowOpacity(0.1)

		self.expandLabel = QtGui.QLabel(self)
		self.expandLabel.setText('Show Less')
		self.setStyleSheet('QWidget {font-size: 8pt }')
		#self.expandLabel.hide()

		# layout management
		layout = QtGui.QVBoxLayout()
		cwidget.setLayout(layout)
		layout.setSpacing(0)
		layout.addWidget(day1)
		layout.addWidget(self.expandLabel)
		# layout.addWidget(day2)
		# layout.addWidget(day3)
		# layout.addWidget(day4)
		# layout.addWidget(day5)




		self.setGeometry(0,40,150,150)
		self.setWindowTitle('To Do')
		self.setWindowIcon(QtGui.QIcon('calendaricon.png'))
		#self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		day1.setMouseTracking(True)

		self.show()

	# def mouseMoveEvent(self, event):
	# 	self.menubar.show()
	# 	self.expandLabel.show()


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
		self.col = Event.RED
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())

	def setPriorityMed(self):
		self.col = Event.ORANGE
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())	

	def setPriorityLow(self):
		self.col = Event.GREEN
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())

	def setPriorityNone(self):
		self.col = Event.KHAKI
		self.eventLabel.setStyleSheet("QWidget { background-color: % s }" % self.col.name())

	def delete(self):
		self.eventLabel.deleteLater()
		self.day.events.remove(self)
		self.day.displayEvents()

	def focus(self):
		self.eventLabel.setFocus(True)

	def outlineLabel(self):
			self.eventLabel.setStyleSheet("QWidget { border-style: dotted; border-width: 2px }")
			self.selected = True
			self.day.selected = self

	def deleteOutline(self):
		self.eventLabel.setStyleSheet("QWidget { border-width: 0px }")
		self.selected = False
		self.day.selected = None

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



def main():
	app = QtGui.QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

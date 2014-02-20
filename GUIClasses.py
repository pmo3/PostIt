######### To Do:
'''
Google Calendar Integration

 '''


from PyQt4 import QtGui, QtCore
import datetime
import sys
import json
import JSONfunctions
import startup
import os
import time


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
		self.setStyleSheet('QWidget { font-size: %s }' % FONTSIZE)

		# self.todayLabel = QtGui.QLabel(self)
		self.dateLabel = QtGui.QLabel(self)

		if type(self.date) == datetime.date:
			self.dateLabel.setText(self.formatDate(self.date))
			self.date = self.formatDate(self.date)
		else:
			self.dateLabel.setText(self.date)

		self.dateLabel.setStyleSheet('QWidget {font-size:8pt }')

		self.deleteLabel = ClickableQLabel(self)
		self.deleteLabel.setText('Delete Event')
		self.addLabel = ClickableQLabel(self)
		self.addLabel.setText('Add')

		self.deleteLabel.setStyleSheet('QWidget {font-size:8pt }')
		self.addLabel.setStyleSheet('QWidget {font-size:8pt }')

		#manage signal/slot connections
		self.connect(self, QtCore.SIGNAL('clicked()'), self.focus)
		self.connect(self, QtCore.SIGNAL('doubleClicked()'), self.addEvent)
		self.connect(self.deleteLabel, QtCore.SIGNAL('clicked()'), self.deleteEvent)
		self.connect(self.addLabel, QtCore.SIGNAL('clicked()'), self.addEvent)

		# manage layouts
		self.dateLayout = QtGui.QHBoxLayout()
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
		self.selected = None

	def focus(self):
		self.setFocus(True)

	def createActions(self):
		self.exitAction = QtGui.QAction('Exit\tCtrl+Q', self, triggered=self.exitApp)
		self.closeAction = QtGui.QAction('Delete this note\tCtrl+W', self, triggered=self.delete)
		self.newNoteAction = QtGui.QAction('New note\tCtrl+N', self, triggered=self.openNewNote)
		self.addEventAction = QtGui.QAction('Add event\tCtrl+A', self, triggered=self.addEvent)
		
		self.setPink = QtGui.QAction('Pink\tF2', self, triggered=self.changeColor(PINK), checkable=True)
		self.setGreen = QtGui.QAction('Green\tF3', self, triggered=self.changeColor(GREEN), checkable=True)
		self.setOrange = QtGui.QAction('Orange\tF4', self, triggered=self.changeColor(ORANGE), checkable=True)
		self.setPurple = QtGui.QAction('Purple\tF5', self, triggered=self.changeColor(PURPLE), checkable=True)
		self.setDefault = QtGui.QAction('Default\tF1', self, triggered=self.changeColor(KHAKI), checkable=True)
		self.setCustom = QtGui.QAction('Custom\tF6', self, triggered=self.changeColor('Custom'), checkable=True)

		self.colorMenu = QtGui.QMenu('Change Background Color')
		self.colorMenu.addAction(self.setDefault)
		self.colorMenu.addAction(self.setPink)
		self.colorMenu.addAction(self.setGreen)
		self.colorMenu.addAction(self.setOrange)
		self.colorMenu.addAction(self.setPurple)
		self.colorMenu.addAction(self.setCustom)
		
		self.setColorChecked()

		self.fontMenu = QtGui.QMenu('Change Font Size')
		self.setFontSmall = QtGui.QAction('Small', self, triggered=self.changeFontSize('8pt'), checkable=True)
		self.setFontMed = QtGui.QAction('Medium', self, triggered=self.changeFontSize('10pt'), checkable=True)
		self.setFontLarge = QtGui.QAction('Large', self, triggered=self.changeFontSize('12pt'), checkable=True)
		self.fontMenu.addAction(self.setFontSmall)
		self.fontMenu.addAction(self.setFontMed)
		self.fontMenu.addAction(self.setFontLarge)

		self.setFontChecked()

		self.sizeMenu = QtGui.QMenu('Change Size')
		self.setSizeSmall = QtGui.QAction('Small', self, triggered=self.changeSize(150), checkable=True)
		self.setSizeMed = QtGui.QAction('Med', self, triggered=self.changeSize(250), checkable=True)
		self.setSizeLarge = QtGui.QAction('Large', self, triggered=self.changeSize(320), checkable=True)
		self.sizeMenu.addAction(self.setSizeSmall)
		self.sizeMenu.addAction(self.setSizeMed)
		self.sizeMenu.addAction(self.setSizeLarge)

		self.setSizeChecked()


		#set contextmenu policy for Note
		self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.setupMainContextMenu)	

	def setupMainContextMenu(self):
		mainMenu = QtGui.QMenu()
		mainMenu.addAction(self.newNoteAction)
		mainMenu.addAction(self.addEventAction)
		mainMenu.addMenu(self.colorMenu)
		mainMenu.addMenu(self.fontMenu)
		mainMenu.addMenu(self.sizeMenu)
		mainMenu.addAction(self.closeAction)
		mainMenu.addAction(self.exitAction)
		mainMenu.exec_(QtGui.QCursor.pos())	


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
			JSONfunctions.update_pos(self, self.rect().topLeft(), NotesOnDisplay, NotesOnDisplayJSON)
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
		elif color == 'None' or color == 'Choose a Priority':
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

class QuoteScreen(QtGui.QDialog):
	def __init__(self):
		super(QuoteScreen, self).__init__()
		self.backgrounds = []
		for file in os.listdir("media/splash"):
			self.backgrounds.append(file)

		self.initUI()

	def initUI(self):
		from random import choice
		self.label = ClickableQLabel(self)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.resize(640, 480)
		self.label.setWordWrap(True)
		self.setStyleSheet('QDialog {background-image: url("media/splash/%s"); background-repeat: no-repeat}' % choice(self.backgrounds))
		self.label.setStyleSheet('ClickableQLabel {font-size: 20pt; color:white}')
		self.label.setText(startup.findQuote()[0])

		self.labelLayout = QtGui.QHBoxLayout()
		self.labelLayout.addStretch(1)
		self.labelLayout.addWidget(self.label)
		self.labelLayout.addStretch(1)

		self.author = ClickableQLabel(self)
		self.author.setStyleSheet('ClickableQLabel {font-size: 18pt; color:white}')
		self.author.setText("- " + startup.findQuote()[1])

		#layout management
		self.authorLayout = QtGui.QHBoxLayout()
		self.authorLayout.addStretch(1)
		self.authorLayout.addWidget(self.author)

		self.layout = QtGui.QVBoxLayout()
		self.layout.addStretch(1)
		self.layout.addLayout(self.labelLayout)
		self.layout.addStretch(1)
		self.layout.addLayout(self.authorLayout)
		self.layout.addStretch(1)
		self.setLayout(self.layout)

		self.connect(self, QtCore.SIGNAL('clicked()'), self.closeSplash)

		self.center()
		self.show()

	def center(self):
		'''center widget on screen'''
		self.screen = QtGui.QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.move((self.screen.width() - size.width())/2, (self.screen.height() - size.height())/2)

	def closeSplash(self):
		self.deleteLater()
		for item in NotesOnDisplay:
			item.show()

	def mouseReleaseEvent(self, event):
		if event.button() == QtCore.Qt.LeftButton:
			self.emit(QtCore.SIGNAL('clicked()'))



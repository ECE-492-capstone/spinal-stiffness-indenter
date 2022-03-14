# UI imports
from PyQt5.QtWidgets import*
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

# data management imports
import sys

#custom  class imports
from Indenter import *

# delete these later
import numpy as np
import random


class MainWindow(QMainWindow):

    def __init__(self, UIFileName):
        # initialize Qt for the GUI
        QMainWindow.__init__(self)
        loadUi(UIFileName, self)
        self.setWindowTitle("Indenter Control Panel")
        
        self.Indenter = Indenter(self.MplWidget)

        # set up bindings for the buttons and plot widgets
        self.pushButton_generate_random_signal.clicked.connect(self.updateGraph) # random button
        self.pushButton_clear_graph.clicked.connect(self.MplWidget.clear)        # clear button
        self.LoadButton.clicked.connect(self.loadFile)                           # load button
        self.SaveButton.clicked.connect(self.saveFile)                           # save button
        self.exitButton.clicked.connect(self.exitProgram)                        # exit button
        
        self.startButton.clicked.connect(self.startMeasurement)                  # start button
        self.stopButton.clicked.connect(self.Indenter.emergencyStop)             # stop button

        self.upButton.pressed.connect(self.Indenter.startJogUp)                  # jog up button pressed
        self.upButton.released.connect(self.Indenter.stopJogging)                  # jog up button released

        self.downButton.pressed.connect(self.Indenter.startJogDown)              # jog down button pressed
        self.downButton.released.connect(self.Indenter.stopJogging)              # jog down button released
        
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))          # MPL nav bar
        
        # set up the force application buttons / readout
        self.incrementButton.setAutoRepeat(True)
        self.decrementButton.setAutoRepeat(True)
        self.forceText.insertPlainText("20")
        self.incrementButton.pressed.connect(
            lambda: self.update_force('increment'))
        self.decrementButton.pressed.connect(
            lambda: self.update_force('decrement'))


    def saveFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()", "", "CSV File (*.csv)", options=options)
        if filename:
            self.Indenter.saveResults(filename)


    def loadFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "", "All Files (*);;CSV Files (*.csv)", options=options)
        if filename:
            self.Indenter.loadAndShowResults(filename)


    def update_force(self, _str):
        init_force = int(self.forceText.toPlainText())
        new_force = (init_force+5) if _str == 'increment' else (init_force-5)

        if(0 <= new_force <= 100):
            self.forceText.setText(str(new_force))
        else:
            self.forceText.setText('0')


    def startMeasurement(self):
        loadGrams = int(self.forceText.toPlainText())/9.81*1000 # convert force to mass
        self.Indenter.takeStiffnessMeasurement(int(loadGrams))


    def exitProgram(self):
        print("stopped")
        Indenter.shutdown()
        sys.exit()
        

    # remove me in the future
    def updateGraph(self):
        f = random.randint(1, 50)
        length_of_signal = 10000
        t = np.linspace(0, 1, length_of_signal)

        cosinus_signal = np.cos(2*np.pi*f*t)
        sinus_signal = np.sin(2*np.pi*f*t)

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(t, cosinus_signal)
        self.MplWidget.canvas.axes.plot(t, sinus_signal)
        self.MplWidget.canvas.axes.legend(('cosine', 'sine'), loc='upper right')
        self.MplWidget.canvas.axes.set_title('Cosine - Sine Signal')
        self.MplWidget.canvas.figure.tight_layout()
        self.MplWidget.canvas.draw() 
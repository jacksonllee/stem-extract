#!/usr/bin/python

"""
GUI for extracting inflectional stems based on substrings, multisets, and subsequences

Jackson Lee
2014-04-03
"""

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import stemExtract as SE





class widgetFromFile(QWidget):
    def __init__(self, parent=None):
        super(widgetFromFile, self).__init__(parent)

        self.dirty = False
        self.noDataText = '[no data loaded]'
        self.dataFile = None
        self.dataFileLabel = self.noDataText
        self.headerDataFile = QLabel('')
        self.badFilenameChars = '#%&{}\\/<>*?$!`\'\":@+|= '

        self.resize(400, 100)
        self.setWindowTitle('StemExtract')

        #### data file settings ####
        # delimiter


        #### output settings ####
        # filename text box
        self.outputFilename = QLineEdit(self)
        outputFilenameLayout = QHBoxLayout()
        outputFilenameLayout.addWidget(QLabel('Filename:'))
        outputFilenameLayout.addWidget(self.outputFilename)
        self.connect(self.outputFilename, SIGNAL('editingFinished()'), self.checkFilename)

        # width and height
        self.width = QDoubleSpinBox()
        self.width.setValue(8.5)
        self.height = QDoubleSpinBox()
        self.height.setValue(11)

        widthHeightLayout = QHBoxLayout()
        widthHeightSpinBoxesGrid = QGridLayout()
        widthHeightSpinBoxesGrid.addWidget(QLabel('Width (inches):'), 0, 0)
        widthHeightSpinBoxesGrid.addWidget(self.width, 0, 1)
        widthHeightSpinBoxesGrid.addWidget(QLabel('Height (inches):'), 1, 0)
        widthHeightSpinBoxesGrid.addWidget(self.height, 1, 1)
        widthHeightLayout.addLayout(widthHeightSpinBoxesGrid)

        reverseWidthHeightButton = QPushButton('Reverse', self)
        self.connect(reverseWidthHeightButton, SIGNAL('clicked()'), self.reverseWidthHeight)
        widthHeightLayout.addWidget(reverseWidthHeightButton)

        resetWidthHeightButton = QPushButton('Reset', self)
        self.connect(resetWidthHeightButton, SIGNAL('clicked()'), self.resetWidthHeight)
        widthHeightLayout.addWidget(resetWidthHeightButton)
        widthHeightLayout.addStretch(1)

        # layout
        outputLayout = QVBoxLayout()
        outputLayout.addLayout(outputFilenameLayout)
        outputLayout.addLayout(widthHeightLayout)

        # output group box
        outputGroupBox = QGroupBox()
        outputGroupBox.setTitle('Output file settings')
        outputGroupBox.setLayout(outputLayout)


        #### bottom buttons ####
        # "Run" button
        runButton = QPushButton('Run', self)
        self.connect(runButton, SIGNAL('clicked()'), self.runSE)

        # "Read data" button
        readDataButton = QPushButton('Read data', self)
        self.connect(readDataButton, SIGNAL('clicked()'), self.showOpenFileDialog)

        # "Clear data" button
        clearDataButton = QPushButton('Clear data', self)
        self.connect(clearDataButton, SIGNAL('clicked()'), self.clearData)

        # buttons' layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(runButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(readDataButton)
        buttonLayout.addWidget(clearDataButton)



        #### overall layout ####
        self.updateWidget()

        overallLayout = QVBoxLayout()

        overallLayout.addWidget(self.headerDataFile)
        overallLayout.addWidget(outputGroupBox)
        overallLayout.addLayout(buttonLayout)
        self.setLayout(overallLayout)

    def runSE(self):
        if self.dataFile and self.checkFilename:
            SE.main(self.dataFile, self.outputFilename.text(),
                    str(self.width.value()), str(self.height.value()))
        else:
            QMessageBox.warning(self, "No data",
                                      "Please specify a suitable .csv data file .")

    def showOpenFileDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open data file', '.', '*.csv')
        if fname:
            self.loadFile(fname)

    def loadFile(self, fname=None):
        if fname is None:
            return
        if fname:
            self.dataFile = open(fname, 'r')
            self.dataFileLabel = self.dataFile.name.split('/')[-1]
            self.updateWidget()

    def clearData(self):
        self.dataFile = None
        self.dataFileLabel = self.noDataText
        self.outputFilename.setText('')
        self.updateWidget()

    def updateWidget(self):
        self.headerDataFile.setText('Data file: %s\n' % (self.dataFileLabel))

    def resetWidthHeight(self):
        self.width.setValue(8.5)
        self.height.setValue(11)

    def reverseWidthHeight(self):
        oldWidth = self.width.value()
        self.width.setValue(self.height.value())
        self.height.setValue(oldWidth)

    def checkFilename(self):
        if filter(lambda x: x in self.badFilenameChars, str(self.outputFilename.text())):
            QMessageBox.warning(self, "Output filename",
                                      "No space or any of these characters are allowed:\n%s\n"
                                      "(or leave \"Filename\" empty to use data filename)" %
                                      (' '.join(self.badFilenameChars)))
            return False # = bad filename
        else:
            return True # = good filename


class widgetMain(QWidget):
    def __init__(self, parent=None):
        super(widgetMain, self).__init__(parent)

        self.dirty = False
        headerMain = QLabel('StemExtract\nBy Jackson Lee and John Goldsmith\n')
        self.resize(400, 300)
        self.setWindowTitle('StemExtract')

#        #### tabs ####
#        tabWidget = QTabWidget(self)
#        tabWidget.addTab(widgetFromFile(), QString('From file'))
#        tabWidget.addTab(widgetFromUser(), QString('From user'))

        #### bottom buttons ####
        # "Quit" button
        quitButton = QPushButton('Quit', self)
        self.connect(quitButton, SIGNAL('clicked()'), QCoreApplication.instance().quit)

        # buttons' layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(quitButton)

        #### overall layout ####
        overallLayout = QVBoxLayout()

        overallLayout.addWidget(headerMain)
        overallLayout.addWidget(widgetFromFile())
        overallLayout.addLayout(buttonLayout)

        self.setLayout(overallLayout)




def main():
    app = QApplication(sys.argv)
    w = widgetMain()
    w.show()
    app.exec_()

if __name__ == '__main__':
    main()



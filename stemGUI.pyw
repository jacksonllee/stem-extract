#!/usr/bin/python

"""
GUI for extracting inflectional stems based on substrings, multisets, and subsequences

Jackson Lee and John Goldsmith
May 2014
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
        outputLayout.addWidget(QLabel('If \"Filename\" is blank, it takes the filename of the data file.'))
        outputLayout.addLayout(widthHeightLayout)

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

        # buttons' layouts
        runButtonLayout = QHBoxLayout()
        runButtonLayout.addStretch(1)
        runButtonLayout.addWidget(runButton)
        runButtonLayout.addStretch(1)

        loadDataButtonLayout = QHBoxLayout()
        loadDataButtonLayout.addStretch(1)
        loadDataButtonLayout.addWidget(readDataButton)
        loadDataButtonLayout.addWidget(clearDataButton)
        loadDataButtonLayout.addStretch(1)

        #### overall layout ####
        self.updateWidget()

        dataFileDisplayLayout = QHBoxLayout()
        dataFileDisplayLayout.addStretch(1)
        dataFileDisplayLayout.addWidget(self.headerDataFile)
        dataFileDisplayLayout.addStretch(1)

        overallLayout = QVBoxLayout()
        overallLayout.addWidget(QLabel('Step 1: <b>Read data file</b> '))
        overallLayout.addLayout(loadDataButtonLayout)
        overallLayout.addLayout(dataFileDisplayLayout)
        overallLayout.addWidget(QLabel('Step 2: <b>Adjust output file settings</b> '))
        overallLayout.addLayout(outputLayout)
        overallLayout.addWidget(QLabel('Step 3: <b>Click \"Run\"</b> '))
        overallLayout.addLayout(runButtonLayout)
        overallLayout.addWidget(QLabel('<hr>'))
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
        headerMain = QLabel('StemExtract\nBy Jackson Lee and John Goldsmith')
        self.resize(400, 300)
        self.setWindowTitle('StemExtract')

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

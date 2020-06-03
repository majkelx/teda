from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFileDialog
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ScanToolbar(QWidget):

    signalStatus = QtCore.Signal(str)

    def __init__(self,parent):
        QWidget.__init__(self, parent)

        self.parent = parent
        self.activeScan=False

        self.layout = QHBoxLayout(self)
        self.BtnScan = QPushButton("Scan")
        self.BtnScan.clicked.connect(self.startScan)
        self.layout.addWidget(self.BtnScan)

        self.BtnStop = QPushButton("Stop")
        self.BtnStop.clicked.connect(self.stopScan)
        self.BtnStop.setVisible(False)
        self.layout.addWidget(self.BtnStop)

        self.BtnPause = QPushButton("Pause")
        self.BtnPause.clicked.connect(self.pauseScan)
        self.BtnPause.setVisible(False)
        self.layout.addWidget(self.BtnPause)

        self.BtnResume = QPushButton("Resume")
        self.BtnResume.clicked.connect(self.resumeScan)
        self.BtnResume.setVisible(False)
        self.layout.addWidget(self.BtnResume)

        self.BtnStartScan = QPushButton("StartScan")
        self.BtnStartScan.setVisible(False)
        self.layout.addWidget(self.BtnStartScan)
        self.BtnStopScan = QPushButton("StopScan")
        self.BtnStopScan.setVisible(False)
        self.layout.addWidget(self.BtnStopScan)
        self.BtnPauseScan = QPushButton("PauseScan")
        self.BtnPauseScan.setVisible(False)
        self.layout.addWidget(self.BtnPauseScan)
        self.BtnResumeScan = QPushButton("ResumeScan")
        self.BtnResumeScan.setVisible(False)
        self.layout.addWidget(self.BtnResumeScan)

        # Create a new worker thread.
        self.createWorkerThread()
        # Make any cross object connections.
        self._connectSignals()

    def startScan(self):
        fileName = QFileDialog.getExistingDirectory(self, 'Select directory')

        if fileName:
            self.BtnScan.setVisible(False)
            self.BtnStop.setVisible(True)
            self.BtnPause.setVisible(True)
            #self.worker.setActive(True)
            self.activeScan = True
            self.worker.setFileName(fileName)
            self.BtnStartScan.click()

    def stopScan(self):
        #self.worker.setActive(False)
        self.BtnScan.setVisible(True)
        self.BtnStop.setVisible(False)
        self.BtnPause.setVisible(False)
        self.BtnResume.setVisible(False)
        self.activeScan = False
        self.forceWorkerReset()

    def pauseScan(self):
        #self.worker.setActive(False)
        self.BtnPause.setVisible(False)
        self.BtnResume.setVisible(True)
        self.activeScan = False
        self.forceWorkerReset()

    def resumeScan(self):
        #self.worker.setActive(True)
        self.BtnPause.setVisible(True)
        self.BtnResume.setVisible(False)
        self.activeScan = True
        self.BtnResumeScan.click()

    def _connectSignals(self):
        self.signalStatus.connect(self.updateStatus)
        #self.parent.aboutToQuit.connect(self.forceWorkerQuit)


    def createWorkerThread(self):

        # Setup the worker object and the worker_thread.
        self.worker = WorkerObject()
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Connect any worker signals
        self.worker.signalStatus.connect(self.updateStatus)
        self.BtnStartScan.clicked.connect(self.worker.startWork)
        self.BtnResumeScan.clicked.connect(self.worker.startWork)


    def forceWorkerReset(self):
        if self.worker_thread.isRunning():
            print('Terminating thread.')
            #self.worker_thread.quit()
            #del (self.worker_thread)
            #print('Waiting for thread termination.')
            #self.worker_thread.wait()

            #print('building new working object.')
            #self.createWorkerThread()


    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

    @QtCore.Slot(str)
    def updateStatus(self, status):
        if self.activeScan:
            time.sleep(1)
            print(status)
            try:
                self.parent.open_fits(status)
            except FileNotFoundError:
                print('Błąd w odczycie pliku')
            except OSError:
                print('Pusty lub błedny format pliku')

class WorkerObject(QtCore.QObject):

    signalStatus = QtCore.Signal(str)

    def __init__(self, parent=None,filename = ""):
        super(self.__class__, self).__init__(parent)
        self.filename = filename
        self.active = True
        self.event_handler = MyHandler(self.signalStatus)

    def setFileName(self,filename):
        self.filename = filename

    @QtCore.Slot()
    def startWork(self):

        observer = Observer()
        observer.schedule(self.event_handler, path=self.filename, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

class MyHandler(FileSystemEventHandler):
    def __init__(self, signal):
        self.signal = signal

    def on_created(self, event):
        self.signal.emit(event.src_path)
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

        self.worker = None
        self.worker_thread = None

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

        #buttony do wywoływania ręcznie ich akcji , na click nie działa self.worker.startWork
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
        # self.createWorkerThread()
        # Make any cross object connections.
        self._connectSignals()

    def startScan(self):
        fileName = QFileDialog.getExistingDirectory(self, 'Select directory')

        if fileName:
            self.createWorkerThread()
            self.BtnScan.setVisible(False)
            self.BtnStop.setVisible(True)
            self.BtnPause.setVisible(True)
            self.worker_thread.start() #powinno tu być ale jest w create
            self.worker.setActive(True)
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
        self.BtnStopScan.click()

    def pauseScan(self):
        #self.worker.setActive(False)
        self.BtnPause.setVisible(False)
        self.BtnResume.setVisible(True)
        self.activeScan = False
        self.BtnPauseScan.click()

    def resumeScan(self):
        self.worker.setActive(True)
        self.BtnPause.setVisible(True)
        self.BtnResume.setVisible(False)
        #self.worker_thread.start()
        self.activeScan = True
        self.BtnResumeScan.click()

    def _connectSignals(self):
        self.signalStatus.connect(self.updateStatus)
        #self.parent.aboutToQuit.connect(self.forceWorkerQuit)


    def createWorkerThread(self):
        if self.worker is None:
            # Setup the worker object and the worker_thread.
            self.worker = WorkerObject()
            self.worker_thread = QtCore.QThread()
            self.worker.moveToThread(self.worker_thread)
            #self.worker_thread.start() # powinno być na przyciskach ale i tak nie ubijam tego threada

            # Connect any worker signals
            self.worker.signalStatus.connect(self.updateStatus)
            self.BtnStartScan.clicked.connect(self.worker.startWork)
            self.BtnResumeScan.clicked.connect(self.worker.startWork)
            self.BtnStopScan.clicked.connect(self.forceWorkerStop)
            self.BtnPauseScan.clicked.connect(self.forceWorkerStop)


    def forceWorkerStop(self):
        #self.worker.stopWork()
        if self.worker_thread.isRunning():
            self.worker.setActive(False)
            #nie udaje mi sie ubić tego worker_thread
            #print('Terminating thread.')
            #self.worker_thread.terminate() #lub quit
            #print('Waiting for thread termination.')
            #self.worker_thread.wait()



    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

    @QtCore.Slot(str)
    def updateStatus(self, status):
        if self.activeScan: # Wprowadzona flaga by ignorować sygnał gdy skan zatrzymany
            time.sleep(1)
            if self.parent.fits_image.isFitsFile(status):
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

    def setActive(self, val):
        self.active = val
        #chciałem tu zatrzymać obserwer by thread zatrzymać ale nie działąło
        #if not val:
        #    self.observer.stop()


    @QtCore.Slot()
    def startWork(self):
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.filename, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    @QtCore.Slot()
    def stopWork(self):
        self.observer.stop()

class MyHandler(FileSystemEventHandler):
    def __init__(self, signal):
        FileSystemEventHandler.__init__(self)
        self.signal = signal

    def on_created(self, event):
        self.signal.emit(event.src_path)
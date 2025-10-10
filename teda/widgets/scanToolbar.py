import glob
import os

from PySide6 import QtCore, QtGui
from PySide6.QtGui import QAction
from PySide6.QtCore import QObject, QEvent, QSettings, QMutex, QMutexLocker
from PySide6.QtWidgets import QFileDialog, QApplication, QMessageBox
import time
from teda.icons import IconFactory
import threading
from traitlets import Float, Int, HasTraits, Bool


class ScanToolbar(QObject):

    signalStatus = QtCore.Signal(str)

    def __init__(self,parent):
        super().__init__()

        self.parent = parent
        self.activeScan = False
        self.mutex = QMutex()  # Protect shared state

        self.worker = None
        self.worker_thread = None
        self.lastScanedFits = None

        # Create a new worker thread.
        # self.createWorkerThread()
        # Make any cross object connections.
        self._connectSignals()

        self.scanAct = QAction(IconFactory.getIcon('play_circle_outline'), 'Scan', self,
                                 statusTip="Scan", triggered=self.startScan)
        self.stopAct = QAction(IconFactory.getIcon('stop_circle'), 'Stop', self,
                                 statusTip="Stop", triggered=self.stopScan)
        self.stopAct.setVisible(False)
        self.pauseAct = QAction(IconFactory.getIcon('pause_circle_outline'), 'Pause', self,
                                 statusTip="Pause", triggered=self.pauseScan)
        self.pauseAct.setVisible(False)
        self.resumeAct = QAction(IconFactory.getIcon('not_started'), 'Resume', self,
                                 statusTip="Resume", triggered=self.resumeScan)
        self.resumeAct.setVisible(False)
        self.autopauseAct = QAction(IconFactory.getIcon('autopause'), 'Autopause', self,
                                 statusTip="Disable Autopause", triggered=self.autopauseClick)
        self.autopauseAct.setVisible(False)
        self.disabledautopauseAct = QAction(IconFactory.getIcon('autopause_disabled'), 'Disabled Autopause', self,
                                    statusTip="Enable Autopause", triggered=self.autopauseClick)
        self.disabledautopauseAct.setVisible(False)

        self.lastmouseposition = None
        self.obserwableValue = ObserwableValue()
        self.obserwableValue.observe(lambda change: self.onAutopauseChange(change), ['autopauseFlag'])
        self.enableAutopause = self.getAutopauseFlagFormSettings()

    def getAutopauseFlagFormSettings(self):
        if self.parent.tedaCommandLine.ignoreSettings:
            return True

        settings = QSettings()
        settings.beginGroup("ScanToolbar")
        flag = settings.value("autopause")
        settings.endGroup()

        if flag != None:
            if flag=="true":
                return True
            else:
                return False
        else:
            return True


    def setNewestFits(self, path):
        list_of_files = glob.glob(path+'/*')
        found=False
        while not found:
            if list_of_files.__len__()>0:
                latest_file = max(list_of_files, key=os.path.getctime)
                if self.parent.fits_image.isFitsFile(latest_file, False):
                    found = True
                    self.parent.open_fits(latest_file)
                else:
                    list_of_files.remove(latest_file)
            else:
                found = True #not found byt no fits in


    def startScan(self):
        try:
            from watchdog.observers import Observer
        except ImportError:
            msgBox = QMessageBox()
            msgBox.setText("The 'watchdog' package not installed")
            msgBox.setInformativeText(
                "In order to use directory scanning, install watchdog package\n  pip install watchdog")
            msgBox.exec()
            return

        self.lastScanedFits = None
        fileName = QFileDialog.getExistingDirectory(None, 'Select directory')
        if fileName:
            self.setNewestFits(fileName)
            self.createWorkerThread()
            self.scanAct.setVisible(False)
            self.stopAct.setVisible(True)
            self.pauseAct.setVisible(True)
            self.worker_thread.start() # Should be here but it's in create
            self.worker.setActive(True)
            self.activeScan = True
            self.worker.setFileName(fileName)
            self.BtnStartScan.trigger()
            if self.enableAutopause:
                self.obserwableValue.autopauseFlag = True
            self.showAutopauseButton()
            #self.startAutopauseTimer()

    def stopScan(self):
        locker = QMutexLocker(self.mutex)
        self.scanAct.setVisible(True)
        self.stopAct.setVisible(False)
        self.pauseAct.setVisible(False)
        self.resumeAct.setVisible(False)
        self.lastScanedFits = None
        self.activeScan = False
        locker.unlock()  # Unlock before calling forceWorkerStop
        self.forceWorkerStop()
        self.obserwableValue.autopauseFlag = False
        self.hideAutopauseButton()

    def pauseScan(self):
        locker = QMutexLocker(self.mutex)
        self.pauseAct.setVisible(False)
        self.resumeAct.setVisible(True)
        self.activeScan = False
        locker.unlock()  # Unlock before calling forceWorkerStop
        self.forceWorkerStop()
        self.obserwableValue.autopauseFlag = False
        self.hideAutopauseButton()

    def resumeScan(self):
        locker = QMutexLocker(self.mutex)
        self.worker.setActive(True)
        self.pauseAct.setVisible(True)
        self.resumeAct.setVisible(False)
        # Load fits if appeared when paused
        if self.lastScanedFits is not None:
            pending_file = self.lastScanedFits
            self.lastScanedFits = None
            locker.unlock()
            self.parent.open_fits(pending_file)
            locker.relock()
        self.activeScan = True
        locker.unlock()
        self.BtnResumeScan.trigger()
        self.obserwableValue.autopauseFlag = True
        self.showAutopauseButton()

    def _connectSignals(self):
        self.signalStatus.connect(self.updateStatus)
        #self.parent.aboutToQuit.connect(self.forceWorkerQuit)


    def createWorkerThread(self):
        if self.worker is None:
            # Setup the worker object and the worker_thread.
            self.worker = WorkerObject()
            self.worker_thread = QtCore.QThread()
            self.worker.moveToThread(self.worker_thread)
            # self.worker_thread.start() should be in button handlers, but thread cleanup wasn't working

            # Connect any worker signals
            self.worker.signalStatus.connect(self.updateStatus)

            self.BtnStartScan = QAction(IconFactory.getIcon(''), 'BtnStartScan', self,
                                        statusTip="Scan", triggered=self.worker.startWork)
            self.BtnResumeScan = QAction(IconFactory.getIcon(''), 'BtnResumeScan', self,
                                         statusTip="Scan", triggered=self.worker.startWork)


    def forceWorkerStop(self):
        """Properly stop worker thread and observer"""
        if self.worker is not None:
            # Signal worker to stop
            self.worker.setActive(False)

        if self.worker_thread is not None and self.worker_thread.isRunning():
            # Request thread to quit cleanly
            self.worker_thread.quit()
            # Wait up to 5 seconds for thread to finish
            if not self.worker_thread.wait(5000):
                # If thread doesn't stop gracefully, terminate it
                print('Warning: Thread did not stop gracefully, terminating...')
                self.worker_thread.terminate()
                self.worker_thread.wait()



    def forceWorkerQuit(self):
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()

    @QtCore.Slot(str)
    def updateStatus(self, status):
        if status == "1secPing":
            self.autopauseTimer()
        else:
            # Defer file loading to avoid blocking the UI thread
            # Use QTimer.singleShot to add a small delay without blocking
            QtCore.QTimer.singleShot(1000, lambda: self._loadFile(status))

    def _loadFile(self, status):
        """Helper method to load FITS file without blocking UI"""
        # Use mutex to protect access to shared state
        locker = QMutexLocker(self.mutex)

        if not self.obserwableValue.autopauseFlag:
            if self.activeScan:
                if self.parent.fits_image.isFitsFile(status, True):
                    print(status)
                    try:
                        self.parent.open_fits(status)
                        self.lastScanedFits = None
                    except FileNotFoundError:
                        print('Error reading file')
                    except OSError:
                        print('Empty or invalid file format')
            else:
                if self.parent.fits_image.isFitsFile(status, False):
                    self.lastScanedFits = status
        else:
            if self.parent.fits_image.isFitsFile(status, False):
                self.lastScanedFits = status

    def autopauseTimer(self):
        if self.obserwableValue.autopauseFlag:
            if self.lastmouseposition == QtGui.QCursor.pos():
                self.timerCount -= 1
                if self.timerCount == 8:
                    self.autopauseAct.setIcon(IconFactory.getIcon('count4'))
                if self.timerCount == 6:
                    self.autopauseAct.setIcon(IconFactory.getIcon('count3'))
                if self.timerCount == 4:
                    self.autopauseAct.setIcon(IconFactory.getIcon('count2'))
                if self.timerCount == 2:
                    self.autopauseAct.setIcon(IconFactory.getIcon('count1'))
            else:
                self.lastmouseposition = QtGui.QCursor.pos()
                self.resetMaxTimer()
                self.autopauseAct.setIcon(IconFactory.getIcon('count5'))
            if self.timerCount < 1:
                self.obserwableValue.autopauseFlag = False
        else:
            pass

    def resetMaxTimer(self):
        self.timerCount = 10

    def stopAutopauseTimer(self):
        self.timerCount = 0

    def showAutopauseButton(self):
        if not self.enableAutopause:
            self.autopauseAct.setVisible(False)
            self.disabledautopauseAct.setVisible(True)
        else:
            self.autopauseAct.setVisible(True)
            self.disabledautopauseAct.setVisible(False)

    def hideAutopauseButton(self):
        self.autopauseAct.setVisible(False)
        self.disabledautopauseAct.setVisible(False)

    def onAutopauseChange(self,change):
        if change.new:
            self.autopauseAct.setIcon(IconFactory.getIcon('count5'))
            self.resetMaxTimer()
            self.lastmouseposition = None
        else:
            self.timerCount = 0
            self.autopauseAct.setIcon(IconFactory.getIcon('autopause'))
            if self.lastScanedFits != None:  # load fits if appeared when paused
                self.parent.open_fits(self.lastScanedFits)
                self.lastScanedFits = None

    def autopauseClick(self):
        if not self.enableAutopause:
            self.autopauseAct.setVisible(True)
            self.disabledautopauseAct.setVisible(False)
            self.obserwableValue.autopauseFlag = True
        else:
            self.autopauseAct.setVisible(False)
            self.disabledautopauseAct.setVisible(True)
            self.obserwableValue.autopauseFlag = False
        self.enableAutopause = not self.enableAutopause

        settings = QSettings()
        settings.beginGroup("ScanToolbar")
        settings.setValue("autopause", self.enableAutopause)
        settings.endGroup()

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
        # Tried to stop observer here to stop thread but it didn't work
        # if not val:
        #     self.observer.stop()


    @QtCore.Slot()
    def startWork(self):
        from watchdog.observers import Observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.filename, recursive=False)
        self.observer.start()
        try:
            while self.active:  # Check active flag to allow clean shutdown
                time.sleep(0.5)
                if self.active:  # Check again after sleep
                    self.signalStatus.emit("1secPing")
        except KeyboardInterrupt:
            pass
        finally:
            # Always stop observer when exiting
            if self.observer is not None:
                self.observer.stop()
                self.observer.join()

    @QtCore.Slot()
    def stopWork(self):
        self.observer.stop()

try:
    from watchdog.events import FileSystemEventHandler
    HandlerBase = FileSystemEventHandler
except ImportError:
    HandlerBase = object


class MyHandler(HandlerBase):
    def __init__(self, signal):
        FileSystemEventHandler.__init__(self)
        self.signal = signal

    def on_created(self, event):
        self.signal.emit(event.src_path)

class ObserwableValue(HasTraits):
    autopauseFlag = Bool(default_value=False)
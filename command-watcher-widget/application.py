import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer, QThreadPool, QRunnable, pyqtSignal, QObject
import subprocess
import time
import shlex

COMMAND1 = 'aws s3 ls'
COMMAND2 = 'aws sts get-caller-identity --query UserId --output text'

class Signals(QObject):
    output1 = pyqtSignal(str)
    output2 = pyqtSignal(str)

class ALWTMC(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('ALWTMC')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.job1_label = QLabel('JOB 1: Refresh Interval: 30, Remaining: 20')
        self.job1_output = QTextEdit()
        self.job2_label = QLabel('JOB 2: Refresh Interval: 30, Remaining: 20')
        self.job2_output = QTextEdit()
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stopTimer)

        self.layout.addWidget(self.job1_label)
        self.layout.addWidget(self.job1_output)
        self.layout.addWidget(self.job2_label)
        self.layout.addWidget(self.job2_output)
        self.layout.addWidget(self.stop_button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshOutput)
        self.timer.start(1000)  # 1 second

        self.thread_pool = QThreadPool()

        self.refreshOutput()

    def refreshOutput(self):
        worker = RefreshWorker()
        worker.signals.output1.connect(self.updateJob1Output)
        worker.signals.output2.connect(self.updateJob2Output)
        self.thread_pool.start(worker)

        remaining1 = int(self.job1_label.text().split(':')[-1].strip())
        remaining2 = int(self.job2_label.text().split(':')[-1].strip())

        if remaining1 > 0:
            self.job1_label.setText(self.job1_label.text().split(':')[0] + ': Refresh Interval: 30, Remaining: ' + str(remaining1 - 1))
        else:
            self.job1_label.setText(self.job1_label.text().split(':')[0] + ': Refresh Interval: 30, Remaining: 20')

        if remaining2 > 0:
            self.job2_label.setText(self.job2_label.text().split(':')[0] + ': Refresh Interval: 30, Remaining: ' + str(remaining2 - 1))
        else:
            self.job2_label.setText(self.job2_label.text().split(':')[0] + ': Refresh Interval: 30, Remaining: 20')

    def updateJob1Output(self, output):
        self.job1_output.setText(output)

    def updateJob2Output(self, output):
        self.job2_output.setText(output)

    def stopTimer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.stop_button.setText('Resume')
        else:
            self.timer.start(1000)
            self.stop_button.setText('Stop')

class RefreshWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = Signals()

    def run(self):
        try:
            output1 = subprocess.check_output(shlex.split(COMMAND1), universal_newlines=True)
            output2 = subprocess.check_output(shlex.split(COMMAND2), universal_newlines=True)
            self.signals.output1.emit(output1)
            self.signals.output2.emit(output2)
        except subprocess.CalledProcessError as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ALWTMC()
    ex.show()
    sys.exit(app.exec_())
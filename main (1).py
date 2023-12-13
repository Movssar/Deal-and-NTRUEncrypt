from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QCheckBox, QMessageBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
import time
import ctypes
import os

deal = ctypes.CDLL("DEAL.dll", winmode=0)
ntruencrypt = ctypes.CDLL("NTRUENCRYPT.dll", winmode=0)

deal.GenerateKeys(256)

class WorkerThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, selected_file_path, selected_method, selected_mode, cipher_mode_choice, output_directory, selected_key, delete_file_var):
        super(WorkerThread, self).__init__()
        self.selected_file_path = selected_file_path
        self.selected_method = selected_method
        self.selected_mode = selected_mode
        self.cipher_mode_choice = cipher_mode_choice
        self.output_directory = output_directory
        self.selected_key = selected_key
        self.delete_file_var = delete_file_var

    def run(self):
        progress_steps = [10, 30, 80, 90, 100]

        progress = 0
        for step in progress_steps:
            progress = step
            self.progress_signal.emit(progress)
            time.sleep(0.6)

        if not self.selected_file_path or not self.output_directory:
            QMessageBox.critical(None, "Error", "Choose a file and a directory to save.")
            return

        if self.delete_file_var and os.path.exists(self.selected_file_path):
            os.remove(self.selected_file_path)


class MyApp(QWidget):
    def __init__(self):
        super(MyApp, self).__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.delete_file_var = QCheckBox("Delete original file")
        layout.addWidget(self.delete_file_var)

        layout.addWidget(QLabel("Select file:"))
        self.file_entry = QLineEdit()
        layout.addWidget(self.file_entry)

        browse_file_button = QPushButton("Browse")
        browse_file_button.clicked.connect(self.browseFile)
        layout.addWidget(browse_file_button)

        layout.addWidget(QLabel("Select method:"))
        self.method_choice = QComboBox()
        self.method_choice.addItems(["DEAL", "NTRUEncrypt"])
        layout.addWidget(self.method_choice)

        layout.addWidget(QLabel("Select mode:"))
        self.mode_choice = QComboBox()
        self.mode_choice.addItems(["Encryption", "Decryption"])
        layout.addWidget(self.mode_choice)

        layout.addWidget(QLabel("Select cipher mode:"))
        self.cipher_mode_choice = QComboBox()
        self.cipher_mode_choice.addItems(["ECB", "CBC", "CFB", "OFB"])
        layout.addWidget(self.cipher_mode_choice)

        layout.addWidget(QLabel("Select key:"))
        self.key_entry = QLineEdit()
        layout.addWidget(self.key_entry)

        browse_key_button = QPushButton("Browse")
        browse_key_button.clicked.connect(self.browseKey)
        layout.addWidget(browse_key_button)

        layout.addWidget(QLabel("Select output directory:"))
        self.output_entry = QLineEdit()
        layout.addWidget(self.output_entry)

        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.browseOutput)
        layout.addWidget(browse_output_button)

        self.next_button = QPushButton("OK")
        self.next_button.clicked.connect(self.startProcessing)
        self.next_button.setEnabled(True)
        layout.addWidget(self.next_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def browseFile(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_path, _ = file_dialog.getOpenFileName()
        if file_path:
            self.file_entry.setText(file_path)

    def browseKey(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        key_path, _ = file_dialog.getOpenFileName()
        if key_path:
            self.key_entry.setText(key_path)

    def browseOutput(self):
        dir_dialog = QFileDialog()
        dir_dialog.setFileMode(QFileDialog.Directory)
        dir_path = dir_dialog.getExistingDirectory()
        if dir_path:
            self.output_entry.setText(dir_path)



    def checkFile(self):
        file_name = self.file_entry.text()
        output_directory = self.output_entry.text()
        if file_name and output_directory:
            self.next_button.setEnabled(True)
        else:
            self.next_button.setEnabled(False)

    def startProcessing(self):
        selected_file_path = self.file_entry.text()
        selected_method = self.method_choice.currentText()
        selected_mode = self.mode_choice.currentText()
        selected_cipher_mode = self.cipher_mode_choice.currentText()
        output_directory = self.output_entry.text()
        selected_key = self.key_entry.text()
        delete_file_var = self.delete_file_var.isChecked()

        if (selected_mode == "Encryption"):
            mode = 1
        if (selected_mode == "Decryption"):
            key = selected_key.encode('cp866')
            mode = 0

        file = selected_file_path.encode('cp866')
        directorytosave = output_directory.encode('cp866')

        if (selected_method == "DEAL"):
            deal.Encryption(file, directorytosave, 256, mode, 0)
        else:
            if (mode == 1):
                ntruencrypt.Encryption(file, directorytosave, 256, mode)
            else:
                ntruencrypt.Decryption(file, key, directorytosave, 256, mode)

        self.worker_thread = WorkerThread(selected_file_path, selected_method, selected_mode, selected_cipher_mode, output_directory, selected_key, delete_file_var)
        self.worker_thread.progress_signal.connect(self.updateProgressBar)
        self.worker_thread.start()

    def updateProgressBar(self, progress):
        self.progress_bar.setValue(progress)


if __name__ == '__main__':
    app = QApplication([])
    my_app = MyApp()
    my_app.show()
    app.exec_()
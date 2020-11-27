import cv2
import time
import sys

from worker import Worker
from enums import Actions, Requests
from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QPushButton, QLabel, QFileDialog, QCheckBox, QGridLayout, QSizePolicy, QSlider
from PyQt5.QtCore import pyqtSignal, Qt

def trap_exc_during_debug(*args):
    print(args)

# Affichage de l'erreur sans faire crasher le GUI
sys.excepthook = trap_exc_during_debug

# Séparateur Horizontal
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class Window(QWidget):
    controller = pyqtSignal(Requests)

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 300, 300)

        self.thread = Worker(self)

        # Bouton Start/Pause
        self.controller.connect(self.thread.handleRequest)

        # Connect action reporter
        self.thread.communicator.connect(self.action)

        # Callback pour le changement de frame
        self.thread.frameChanged.connect(self.frameChanged)

        grid = QGridLayout()
        grid.setSpacing(5)

        # Affichage de l'etat actuel
        self.statusLabel = QLabel('Status: Choississez une vidéo')
        grid.addWidget(self.statusLabel, 0, 0, 1, 8)

        # Affichage des FPS
        self.fpsLabel = QLabel('')
        self.fpsLabel.setAlignment(Qt.AlignRight)
        grid.addWidget(self.fpsLabel, 0, 8, 1, 4)

        # Séparateur horizontal
        grid.addWidget(QHLine(), 1, 0, 1, 12)

        # Fonction permettant d'ouvrir le fichier vidéo
        self.chooseVideoButton = QPushButton('Choississez la vidéo')
        self.chooseVideoButton.clicked.connect(self.chooseVideo)
        self.chooseVideoButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.chooseVideoButton, 2, 0, 1, 12)

        # Chargement des poids du modèle et ouverture de la vidéo
        self.startButton = QPushButton('Démarrer')
        self.startButton.clicked.connect(self.start)
        self.startButton.setEnabled(False)
        self.startButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.startButton, 3, 0, 2, 4)

        # Pause de la lecture
        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.pause)
        self.pauseButton.setEnabled(False)
        self.pauseButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.pauseButton, 3, 4, 1, 4)

        # Reprise de la lecture
        self.resumeButton = QPushButton('Reprendre')
        self.resumeButton.clicked.connect(self.resume)
        self.resumeButton.setEnabled(False)
        self.resumeButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.resumeButton, 4, 4, 1, 4)

        # Arrêt de la lecture et fermeture de la vidéo
        self.stopButton = QPushButton('Stop')
        self.stopButton.clicked.connect(self.stop)
        self.stopButton.setEnabled(False)
        self.stopButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.addWidget(self.stopButton, 3, 8, 2, 4)

        # Label displaying the file path of the chosen video
        self.filePathLabel = QLabel('Fichier: Aucun')
        self.filePathLabel.setWordWrap(True)
        grid.addWidget(self.filePathLabel, 5, 0, 1, 12)

        # Affichage de la durée actuelle de la vidéo 
        self.currentTimeLabel = QLabel('0:00:00')
        grid.addWidget(self.currentTimeLabel, 6, 0, 1, 1)

        # Choix du temps de lecture
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.NoTicks)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.setTime)
        self.slider.setEnabled(False)
        grid.addWidget(self.slider, 6, 1, 1, 10)

        # Affichage de la durée totale de la vidéo
        self.finalTimeLabel = QLabel('0:00:00')
        grid.addWidget(self.finalTimeLabel, 6, 11, 1, 1)

        # Séparateur horizontal
        grid.addWidget(QHLine(), 7, 0, 1, 12)

        # Démarrer la détection de cibles
        self.detectToggle = QCheckBox('Détecter les cibles')
        self.detectToggle.setEnabled(False)
        self.detectToggle.stateChanged.connect(self.toggleDetection)
        grid.addWidget(self.detectToggle, 8, 0, 1, 12)

        # Afficher les masques de détection
        self.masksToggle = QCheckBox('Afficher les masques')
        self.masksToggle.setEnabled(False)
        self.masksToggle.stateChanged.connect(self.toggleMasks)
        self.masksToggle.setChecked(True)
        grid.addWidget(self.masksToggle, 9, 0, 1, 6)

        # Afficher les cibles détectées
        self.boxesToggle = QCheckBox('Afficher les cibles détectées')
        self.boxesToggle.setEnabled(False)
        self.boxesToggle.stateChanged.connect(self.toggleBoxes)
        self.boxesToggle.setChecked(True)
        grid.addWidget(self.boxesToggle, 9, 6, 1, 6)

        # Séparateur horizontal
        grid.addWidget(QHLine(), 10, 0, 1, 12)

        # Sauvegarder le résultat de la détection
        self.saveToggle = QCheckBox('Enregistrer la vidéo')
        self.saveToggle.setEnabled(False)
        self.saveToggle.stateChanged.connect(self.toggleSave)
        self.saveToggle.setChecked(False)
        grid.addWidget(self.saveToggle, 11, 0, 1, 12)

        # Chemin de la sauvegarde
        self.savePathLabel = QLabel('Sauvegarde : ')
        self.savePathLabel.setWordWrap(True)
        grid.addWidget(self.savePathLabel, 12, 0, 1, 12)

        self.setLayout(grid)

    #Définition de la fonction de sauvegarde
    def toggleSave(self):
        if self.saveToggle.isChecked():
            self.controller.emit(Requests.SAVE_ON)
        else:
            self.controller.emit(Requests.SAVE_OFF)
            return
        filePath = QFileDialog.getExistingDirectory(self, "Choississez la déstination de sauvegarde...")
        self.savePathLabel.setText('sauvegarde : ' + filePath)
        self.thread.setSave(filePath)
    # Définition de la fonction permettant le choix du temps de lecture
    def setTime(self):
        seconds = self.slider.value()
        paused = self.thread.paused
        self.pause()
        time.sleep(0.1)
        fps = self.thread.capture.get(cv2.CAP_PROP_FPS)
        new_frame_number = round(seconds * fps)
        print("Chargement pour le Frame", new_frame_number)
        self.thread.capture.set(cv2.CAP_PROP_POS_FRAMES, new_frame_number)
        # Reprendre si la vidéo a été mise en pause
        if not paused:
            self.resume()
    
    # Fonction liée à la mise à jour de la détection
    def toggleDetection(self): 
        if self.detectToggle.isChecked():
            self.controller.emit(Requests.DETECT_ON)
        else:
            self.controller.emit(Requests.DETECT_OFF)
        self.masksToggle.setEnabled(self.detectToggle.isChecked())
        self.boxesToggle.setEnabled(self.detectToggle.isChecked())

    #Fonction liée à la mise à jour des masques
    def toggleMasks(self):
        if self.masksToggle.isChecked():
            self.controller.emit(Requests.MASKS_ON)
        else:
            self.controller.emit(Requests.MASKS_OFF)
        if not self.masksToggle.isChecked() and not self.boxesToggle.isChecked():
            self.detectToggle.setChecked(False)
    #Fonction liée à la mise à jour des rectangles contenant les cibles
    def toggleBoxes(self):
        if self.boxesToggle.isChecked():
            self.controller.emit(Requests.BOXES_ON)
        else:
            self.controller.emit(Requests.BOXES_OFF)
        if not self.masksToggle.isChecked() and not self.boxesToggle.isChecked():
            self.detectToggle.setChecked(False)
    # Fonction permettant le choix de la vidéo
    def chooseVideo(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Choississez le fichier vidéo', '', 'Fichiers | *.mp4;')

        if filePath == '':
            self.statusLabel.setText('Status: Choississez la vidéo')
            self.startButton.setEnabled(False)
            return
        self.filePathLabel.setText('File: ' + filePath)
        self.thread.setVideo(filePath)
        if self.thread.loadedWeights:
            self.statusLabel.setText('Status: Prêt')
        else:
            self.statusLabel.setText('Status: Chargement des poids du modèle...')

        # Chargement des poids du modèle
        if not self.thread.isRunning():
            self.thread.start()
        self.saveToggle.setEnabled(True)
        if self.thread.loadedWeights:
            self.startButton.setEnabled(True)

    # Changement des Frames
    def frameChanged(self):
        formatted = round(self.thread.fps * 100) / 100
        self.fpsLabel.setText('FPS: ' + str(formatted))
        millis = self.thread.capture.get(cv2.CAP_PROP_POS_MSEC)
        self.currentTimeLabel.setText(self.formatTime(millis))


        self.slider.blockSignals(True)
        self.slider.setValue(round(millis / 1000))
        self.slider.blockSignals(False)

        if self.finalTimeLabel.text() == '0:00:00':
            fps = self.thread.capture.get(cv2.CAP_PROP_FPS)
            total_frames = self.thread.capture.get(cv2.CAP_PROP_FRAME_COUNT)

            # Durée de la vidéo en secondes
            duration = (float(total_frames) / float(fps))

            formatted = self.formatTime(duration * 1000)
            self.finalTimeLabel.setText(formatted)
            self.slider.setMaximum(duration)
    # Format de la durée de la vidéo
    def formatTime(self, milliseconds):
        minutes, seconds = divmod(milliseconds / 1000, 60)
        hours, minutes = divmod(minutes, 60)
        return "%d:%02d:%02d" % (hours, minutes, seconds)

    def action(self, action):
        if action is Actions.LOADING_WEIGHTS:
            self.statusLabel.setText('Status: Chargement des poids du modèle...')
        if action is Actions.LOADED_WEIGHTS:
            self.statusLabel.setText('Status: Prêt')
            self.startButton.setEnabled(True)
            self.pauseButton.setEnabled(False)
            self.resumeButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.detectToggle.setEnabled(True)

        if action is Actions.LOADED_VIDEO:
            self.statusLabel.setText('Status: En lecture...')
            self.startButton.setEnabled(False)
            self.resumeButton.setEnabled(False)
            self.pauseButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.slider.setEnabled(True)

        if action is Actions.FINISHED:
            self.statusLabel.setText('Status: Terminé')
            self.stop()

    def start(self):
        self.startButton.setEnabled(False)
        self.resumeButton.setEnabled(False)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.detectToggle.setEnabled(True)
        self.saveToggle.setEnabled(False)
        self.controller.emit(Requests.START)

    def pause(self):
        self.pauseButton.setEnabled(False)
        self.resumeButton.setEnabled(True)
        self.detectToggle.setEnabled(True)
        self.controller.emit(Requests.PAUSE)

    def resume(self):
        self.pauseButton.setEnabled(True)
        self.resumeButton.setEnabled(False)
        self.detectToggle.setEnabled(True)
        self.controller.emit(Requests.RESUME)

    def stop(self):
        self.startButton.setEnabled(True)
        self.resumeButton.setEnabled(False)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.detectToggle.setEnabled(False)
        self.slider.setEnabled(False)
        self.saveToggle.setEnabled(True)
        self.slider.setValue(0)
        self.currentTimeLabel.setText('0:00:00')
        self.finalTimeLabel.setText('0:00:00')
        self.fpsLabel.setText('')

        self.controller.emit(Requests.STOP)


app = QApplication(sys.argv)
window = Window()
window.setWindowTitle('Mask - RCNN')
window.show()

sys.exit(app.exec_())

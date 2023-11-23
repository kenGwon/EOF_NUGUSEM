import face_detector
import pyqt_window



myDetector = face_detector.FaceDetector()
myDetector.collect_data("Ganghyeon")
myDetector.train_model()
myDetector.verify_face()

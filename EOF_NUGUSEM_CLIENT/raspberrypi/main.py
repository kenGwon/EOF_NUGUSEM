import face_collecting
import face_traning
import face_recognizing
import threading

# 프로그램 시작하고 모델 훈련이 필요한 경우
# face_collecting.collect_data("Dohyeon")
face_traning.train_model()
face_recognizing.verify_face()


# while True:
    # 여기서 프로그램 핵심 코드 무한 반복
    # (혹은 이 부분을 라즈베리 리눅스 스레딩으로 처리해야함)
    # ESC같은 입력 들어오면 프로그램 종료



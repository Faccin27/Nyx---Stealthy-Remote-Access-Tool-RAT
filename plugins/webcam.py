import cv2

def capture_photo():
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Erro ao abrir a câmera")
        return None

    ret, frame = cap.read()

    if ret: 
        caminho_foto = "webcam_foto.jpg"
        cv2.imwrite(caminho_foto, frame)
        print("Foto salva")
        cap.release()
        return caminho_foto
    else:
        print("Erro ao capturar a foto")
        cap.release()
        return None

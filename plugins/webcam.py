import cv2
import os

def capture_photo():
    index = 0
    cap = None

    pasta_destino = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Nyx")
    os.makedirs(pasta_destino, exist_ok=True)
    
    while index < 10:  
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Câmera {index} aberta com sucesso!")
            break
        index += 1
    
    if not cap or not cap.isOpened():
        print("Nenhuma câmera encontrada.")
        return None

    ret, frame = cap.read()

    if ret:
        caminho_foto = os.path.join(pasta_destino, "webcam_foto.jpg")
        cv2.imwrite(caminho_foto, frame)
        print(f"Foto capturada e salva em {caminho_foto}")
    else:
        print("Erro ao capturar a foto.")
        caminho_foto = None

    cap.release()
    return caminho_foto

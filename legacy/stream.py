from flask import Flask, send_file, Response
import os
from time import sleep
image_path = ""
app = Flask(__name__)
oldImage = 'old'
IMAGE_FOLDER = '/home/jkb/yoloTest/stream/'  # Pfad zu deinem Ordner mit Bildern

def get_latest_image():
    files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file

@app.route('/latest-image')
def latest_image():
    image_path = get_latest_image()
    if image_path:
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return "No images found", 404

@app.route('/stream')
def stream():
    global oldImage
    print(oldImage)
    def generate():
        global oldImage
#        os.remove(oldImage)
        while True:
            image_path = get_latest_image()
            if oldImage != 'old':
                if image_path != oldImage:
                    os.remove(oldImage)
            oldImage = image_path
            if image_path:
                with open(image_path, 'rb') as image:
                    yield (b'--frame\r\n' b'Content-Type: image/png\r\n\r\n' + image.read() + b'\r\n')
                
                #os.remove(image_path)

            #sleep(1)  # Zeitintervall, nach dem nach neuen Bildern gesucht wird
#            sleep(0.1)
#            os.remove(image_path)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



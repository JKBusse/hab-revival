from flask import Flask, send_file, Response
import os
import time
app = Flask(__name__)
oldImage = 'old'
IMAGE_FOLDER = '/tmp/'  # Path to your folder with images

def get_latest_image():
    files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        return None
    
    # Sort files by creation time
    files.sort(key=os.path.getctime, reverse=True)
    
    # Get the latest file
    latest_file = files[0]
    
    # Delete the oldest 10 files
    for file in files[10:]:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting file {file}: {e}")
    
    return latest_file

@app.route('/stream')
def stream():
    global oldImage
    print(oldImage)
    def generate():
        global oldImage
        while True:
            image_path = get_latest_image()
            oldImage = image_path
            if image_path:
                with open(image_path, 'rb') as image:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/png\r\n\r\n' + image.read() + b'\r\n')
            if oldImage != 'old' and image_path != oldImage:
                try:
                    os.remove(oldImage)
                except Exception as e:
                    print(f"Error deleting old image {oldImage}: {e}")
#            oldImage = image_path
#            if image_path:
#                with open(image_path, 'rb') as image:
#                    yield (b'--frame\r\n'
#                           b'Content-Type: image/png\r\n\r\n' + image.read() + b'\r\n')
#            sleep(1)  # Time interval to check for new images
            time.sleep(0.3) 

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

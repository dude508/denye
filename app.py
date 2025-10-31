import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import base64
import io
from PIL import Image
import requests

# Chaje variab anviwònman an
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

# Konfigire API Gemini
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY pa konfigire nan variab anviwònman an")

genai.configure(api_key=api_key)

# Kreye model la
model = genai.GenerativeModel('gemini-2.5-flash')
vision_model = genai.GenerativeModel('gemini-2.5-flach')

def is_valid_image_url(url):
    """Tcheke si yon URL se yon imaj valide"""
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('content-type', '')
        return content_type.startswith('image/')
    except:
        return False

def download_image(url):
    """Telechaje imaj nan yon URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        raise ValueError(f"Pa telechaje imaj la: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        image_url = data.get('image_url', '').strip()
        image_data = data.get('image_data', '')  # Base64 data
        
        if not message and not image_url and not image_data:
            return jsonify({'error': 'Mesaj la vid oubyen pa gen imaj'}), 400
        
        # Jenere repons lan
        if image_url or image_data:
            # Itilize model vizyon an si gen imaj
            if image_url and is_valid_image_url(image_url):
                image = download_image(image_url)
                response = vision_model.generate_content([message, image])
            elif image_data:
                # Dekode done base64
                image_data = image_data.split(',')[1] if ',' in image_data else image_data
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                response = vision_model.generate_content([message, image])
            else:
                return jsonify({'error': 'URL imaj la pa valide'}), 400
        else:
            # Itilize model tèks sèlman
            prompt = f"""
            Reponn kòm ALIX-IA, yon entèlijans atifisyèl ki ede moun ak enfòmasyon ak asistans.
            Kreyatè w se Mr_Drinx. W ap itilize teknoloji Google Gemini.
            pa itilize non gemini,google,chatgpt nan repons ou
            Mesaj itilizatè a: {message}
            
            Tanpri reponn ak yon ton zanmitay epi enformatif. Si w pa konnen yon repons, di sa klèman.
            """
            response = model.generate_content(prompt)
        
        return jsonify({
            'response': response.text,
            'status': 'success',
            'model_used': 'Gemini2-5-flash'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erè: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/info')
def info():
    """Paj enfòmasyon sou ALIX-IA"""
    return jsonify({
        'name': 'ALIX-IA',
        'version': '2.0',
        'creator': 'Mr_Drinx',
        'technology': 'Google Gemini AI',
        'features': ['Chat tèks', 'Analiz imaj', 'Repons entèlijans'],
        'description': 'ALIX-IA se yon entèlijans atifisyèl, kreye pa Mr_Drinx pou bay asistans ak enfòmasyon.'
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'ALIX-IA', 'creator': 'Mr_Drinx'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

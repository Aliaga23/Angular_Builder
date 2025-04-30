import requests
import base64
import json

GEMINI_API_KEY = "AIzaSyAo5Nl2Y3o2cxhiOgfyjhbTDgP_towXW_o"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

def analizar_mockup(imagen_path: str) -> str:
    with open(imagen_path, "rb") as f:
        imagen_base64 = base64.b64encode(f.read()).decode("utf-8")

    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [{
            "parts": [
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": imagen_base64
                    }
                },
                {
                    "text": """
                    Describe esta foto como componentes de Bootstrap y genera el código HTML correspondiente.
                    No te inventes otros componentes solo los de la imagen, si es necesario incluye iconos de
                    bootstrap.Hazlo como experto a detalle todo , cada palabra debe estar 
                    identica a la foto.
                    """
                
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0
        }
    }

    response = requests.post(
        GEMINI_API_URL + f"?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload
    )

    try:
        result = response.json()
        print("👉 Respuesta de Gemini:")
        print(json.dumps(result, indent=2))
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("❌ Error:")
        print(response.text)
        raise e

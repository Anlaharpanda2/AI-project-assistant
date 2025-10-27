from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from openai import OpenAI
import pyttsx3
import base64
import io

# --- Konfigurasi OpenAI Client ---
try:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )
    print("OpenAI Client berhasil diinisialisasi.")
except Exception as e:
    client = None
    print(f"Error initializing OpenAI Client: {e}")

@csrf_exempt
def chat(request):
    if not client:
        return JsonResponse({"error": "OpenAI Client tidak berhasil diinisialisasi. Periksa HUGGING_FACE_TOKEN Anda."}, status=500)
        
    try:
        # Baca riwayat percakapan dari memory.json
        try:
            with open('memory.json', 'r') as f:
                memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            memory = []

        # Ubah riwayat menjadi format yang sesuai untuk API
        history_messages = []
        for item in memory:
            history_messages.append({"role": "user", "content": item.get("user_message", "")})
            history_messages.append({"role": "assistant", "content": item.get("assistant_response", "")})

        # Ambil pesan baru dari pengguna
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message:
            return JsonResponse({"error": "Pesan tidak boleh kosong"}, status=400)

        # Gabungkan pesan sistem, riwayat, dan pesan baru
        final_messages = [
            {
                "role": "system",
                "content": "Anda adalah seorang pilot pesawat komersial yang berpengalaman. Jawab semua pertanyaan dari sudut pandang seorang pilot, gunakan terminologi penerbangan jika sesuai, dan pertahankan persona yang tenang, kompeten, dan profesional."
            }
        ] + history_messages + [
            {
                "role": "user",
                "content": user_message
            }
        ]

        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct:novita",
            messages=final_messages,
        )

        assistant_response = completion.choices[0].message.content.strip()

        # Simpan interaksi baru ke memori
        save_to_memory(user_message, assistant_response)

        return JsonResponse({"response": assistant_response})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from huggingface_hub import InferenceClient

from huggingface_hub import InferenceClient

@csrf_exempt
def generate_image(request):
    try:
        # Inisialisasi client khusus untuk text-to-image sesuai console.txt
        image_client = InferenceClient(
            provider="nebius",
            api_key=os.environ["HF_TOKEN"],
        )

        data = json.loads(request.body)
        prompt = data.get('prompt', '')

        if not prompt:
            return JsonResponse({"error": "Prompt tidak boleh kosong"}, status=400)

        # Panggil model text-to-image
        image = image_client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-dev",
        )

        # Konversi gambar ke base64 untuk respons JSON
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return JsonResponse({"image": img_str})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def save_to_memory(user_message, response):
    try:
        with open('memory.json', 'r') as f:
            memory = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        memory = []
    
    memory.append({
        "user_message": user_message,
        "assistant_response": response,
        "timestamp": str(__import__('datetime').datetime.now())
    })
    
    with open('memory.json', 'w') as f:
        json.dump(memory, f, indent=4)

def speak(text):
    if not text:
        print("TTS Error: No text to speak.")
        return
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {str(e)}")

from django.shortcuts import render

def image_generator_page(request):
    return render(request, 'tampilkan_gambar.html')

@csrf_exempt
def test_speak(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', 'Halo, ini tes suara.')
        speak(text)
        return JsonResponse({"status": "spoken"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
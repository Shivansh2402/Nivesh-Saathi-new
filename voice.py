from metahackathonfinance import my_logger as log
import requests
from pydub import AudioSegment
from io import BytesIO
import json


def convert_ogg_to_wav(ogg_url, output_filename):
    response = requests.get(ogg_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download OGG file: {response.status_code}")
    ogg_audio = BytesIO(response.content)
    try:
        audio = AudioSegment.from_ogg(ogg_audio)
        audio.export(output_filename, format="wav")
        log.info(f"File successfully converted to {output_filename}")
    except Exception as e:
        raise Exception(f"Error converting OGG to WAV: {str(e)}")


def send_to_sarvam_stt_translate_api(file_path):
    log.info(f"{file_path} for voice input to sarvamAI: in stt_translate_api")
    url = "https://api.sarvam.ai/speech-to-text-translate"
    headers = {'api-subscription-key': 'e9e97313-fc91-4185-a1c1-f13c9a615f9c'}
    payload = {'model': 'saaras:v1', 'with_timestamps': 'true'}

    with open(file_path, 'rb') as audio_file:
        files = [('file', (file_path.split('/')[-1], audio_file, 'audio/wav'))]
        response = requests.post(url, headers=headers, data=payload, files=files)
        log.info(f"{response} from sarvamAI api: in stt_translate_api")

    return response.json()


def send_to_sarvam_stt_api(file_path, lang_code):
    log.info(f"{file_path} for voice inout to sarvamAI: in stt_api")
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {'api-subscription-key': 'e9e97313-fc91-4185-a1c1-f13c9a615f9c'}
    payload = {'language_code': lang_code, 'model': 'saarika:v1', 'with_timestamps': 'false'}
    with open(file_path, 'rb') as audio_file:
        files = [('file', (file_path.split('/')[-1], audio_file, 'audio/wav'))]
        response = requests.post(url, headers=headers, data=payload, files=files)
        log.info(f"{response} from sarvamAI api: in stt_translate_api")

    return response.json()


if __name__ == "__main__":
    ogg_url = "https://fpi-stg.branding-element.com/qa/20842/WA_PUBLIC_ATTACHMENT/a2023017_9277_4e42_a2f1_ac732af3e6f5.ogg-ClquE.ogg"
    output_filename = "output.wav"
    convert_ogg_to_wav(ogg_url, output_filename)

    send_to_sarvam_stt_translate_api("/Users/jaymehta/Downloads/output_67774_919099380271.wav")
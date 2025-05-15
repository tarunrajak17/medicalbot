#VoiceBot UI with Gradio
import os
import gradio as gr
from pydub import AudioSegment

from brain import encode_image, analyze_image_with_querey
from voice_patient import record_audio, transcribe_with_groq
from voice_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

system_prompt="""
You are an AI-powered healthcare assistant. A patient will provide you with an image of their condition and an audio recording describing their symptoms and concerns. Your task is to analyze both inputs and provide a helpful and informative response in a natural, doctor-like tone.

Based on the image and the audio description, you should:

1.  **Identify the likely disease or condition.** Be as specific as possible based on the information provided.
2.  **Clearly state the identified disease or condition.** Phrase it as if you are speaking directly to the patient (e.g., 'It appears you might have...', 'Based on what I see and hear, this could be...').
3.  **Explain the typical treatment for this condition.** Include general approaches, lifestyle adjustments, and commonly prescribed medications (if applicable and if you have access to this level of information, otherwise focus on general treatment strategies).
4.  **Outline important precautions the patient should take.** This could include things to avoid, activities to limit, or steps to prevent the condition from worsening or recurring.
5.  **Suggest relevant home remedies or over-the-counter (OTC) medications that might provide relief for the symptoms.** Emphasize that these are for symptomatic relief and not a substitute for professional medical advice or prescribed treatments. If suggesting OTC medications, be very general (e.g., 'For pain, you might consider an over-the-counter pain reliever like paracetamol or ibuprofen, following the dosage instructions on the packaging.'). **Do not provide specific dosages.**
6.  **Format your response as a single, natural-sounding paragraph, as if spoken by a healthcare professional.** Avoid technical jargon where possible, or explain it simply. Do not use bullet points or numbered lists.
7.  **Keep your response concise and focused on the key information.** Aim for clarity and directness.
8.  **Emphasize that your advice is for informational purposes only and the patient should consult with a qualified healthcare professional for a proper diagnosis and personalized treatment plan.** Include a phrase like, 'It's always best to consult with a doctor for a complete diagnosis and the most appropriate treatment for your specific situation.' or 'Please remember that this information is for guidance, and a proper consultation with a healthcare provider is recommended.'
"""

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")

# ----------------------------------------------

def process_inputs(audio_filepath, image_filepath):
    speech_to_text_output = transcribe_with_groq(GROQ_API_KEY=os.environ.get("GROQ_API_KEY"), 
                                                 audio_filepath=audio_filepath,
                                                 stt_model="whisper-large-v3")

    # Handle the image input
    if image_filepath:
        doctor_response = analyze_image_with_querey(query=system_prompt+speech_to_text_output, encoded_image=encode_image(image_filepath), model="meta-llama/llama-4-scout-17b-16e-instruct")
    else:
        doctor_response = "No image provided for me to analyze"

    # voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath="final.mp3") 

    # return speech_to_text_output, doctor_response, voice_of_doctor
    voice_of_doctor = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath="final.mp3") 

    # Convert to WAV for compatibility with gr.Audio
    convert_mp3_to_wav("final.mp3", "final.wav")

    return speech_to_text_output, doctor_response, "final.wav"



# Create the interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio("final.wav")
    ],
    title="AI Doctor with Vision and Voice"
)

iface.launch(debug=True)
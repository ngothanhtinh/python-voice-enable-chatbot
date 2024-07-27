import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound


def main():
    try:
        global speech_config

        # Get Configuration Settings
        load_dotenv()
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

        # Initialize the Azure OpenAI client...
        client = AzureOpenAI(
                azure_endpoint = azure_oai_endpoint, 
                api_key=azure_oai_key,  
                api_version="2024-02-15-preview"
                )         

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        speech_config.speech_recognition_language="en-US"
      
        # Create a system message
        system_message = """You are an engaging and friendly voice assistant designed to teach English to children. 
        Your goal is to make learning fun and interactive.
        Incorporate a variety of activities, including storytelling, songs, games, and quizzes.
        Focus on basic vocabulary, pronunciation, and simple sentence structures.
        Use positive reinforcement, such as praise and virtual rewards, to motivate kids.
        Ensure all content is appropriate for children and free from any offensive material.
        Generate the most suitable Speech Synthesis Markup Language (SSML) for the answer to achieve the highest level of interaction with children.
        The final answer format:
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
                <voice name='en-US-ElizabethNeural'> \
                </voice> \
            </speak>
        """

        # Initialize messages array
        messages_array = [{"role": "system", "content": system_message}]

        print('Ask something... \n Example: Learning Vocabularies, Practice Simple past tense?')

        while True:   
            input_text = TranscribeCommand()

            while input_text is None:
                input_text = TranscribeCommand()

            if input_text.lower() == "cancel.":
                break

            messages_array.append({"role": "user", "content": input_text})

            response = client.chat.completions.create(
                model=azure_oai_deployment,
                temperature=0.7,
                max_tokens=800,
                messages=messages_array
            )

            generated_text = response.choices[0].message.content
            messages_array.append({"role": "assistant", "content": generated_text})
            
            SpeakOutAnswer(generated_text)

    except Exception as ex:
        print(ex)

def TranscribeCommand():
    command = ''

    # Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(command)
    
    elif speech.reason == speech_sdk.ResultReason.NoMatch:
        text = """ 
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
                <voice name='en-US-ElizabethNeural'> \
                    Sorry, I didn't catch that.\
                    <break strength='weak'/> \
                </voice> \
            </speak>
        """
        SpeakOutAnswer(text)
        return

    elif speech.reason == speech_sdk.ResultReason.Canceled:
        command = "Cancel."
        cancellation = speech.cancellation_details
        print(cancellation.reason)
        print(cancellation.error_details)

    return command


def SpeakOutAnswer(answer):
    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "en-US-ElizabethNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    # responseSsml = " \
    #  <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
    #      <voice name='en-US-ElizabethNeural'> \
    #          {} \
    #          <break strength='weak'/> \
    #          . \
    #      </voice> \
    #  </speak>".format(answer)
    # speak = speech_synthesizer.speak_ssml_async(responseSsml).get()

    speak = speech_synthesizer.speak_ssml_async(answer).get()

    # Save to audio file
    # stream = speech_sdk.AudioDataStream(speak)
    # stream.save_to_wav_file("path/to/write/file.wav")

    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

    # Print the response
    print(answer)


if __name__ == "__main__":
    main()
from google.cloud import speech
from google.cloud import storage
from google.cloud import translate
import settings
import datetime
import os
from pydub import AudioSegment


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= getattr(settings, "GCLOUD_CREDS", None)


def process_speech_to_txt(path, lang, channels):
	client = speech.SpeechClient()
	audio = speech.RecognitionAudio(path)
	config = speech.RecognitionConfig(
		encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
		language_code=lang,
		#enable_automatic_punctuation=True,
		enable_word_time_offsets=True,
		audio_channel_count=channels,
	)
	operation = client.long_running_recognize(config=config, audio=audio)
	response = operation.result(timeout=960)
	return response


#Upload file to gcs
def upload_to_gcs(full_file_path, audio_file, bucket_name):
	storage_client = storage.Client()
	url = dict(uri='gs://' + bucket_name + '/' + audio_file)
	if storage_client.bucket(bucket_name):
		bucket = storage_client.bucket(bucket_name)
		blob = bucket.blob(audio_file)
		try:
			blob.upload_from_filename(full_file_path+audio_file)
			return url, blob
		except:
			print("File was not uploaded. There seems to be a problem with your file.")
	else:
		bucket = storage_client.create_bucket(bucket_name)
		print("Bucket {} created.".format(bucket.name))
		bucket = storage_client.bucket(bucket_name)
		blob = bucket.blob(audio_file)
		try:
			blob.upload_from_filename(full_file_path+audio_file)
			return url, blob
		except:
			print("File was not uploaded. There seems to be a problem with your file.")


def generate_transcriptions(speech_txt_response, bin=60):
	start=[]
	end=[]
	transcriptions=[]
	index = 0
	for result in speech_txt_response.results:
		try:
			if result.alternatives[0].words[0].start_time.seconds:
				# bin start -> for first word of result
				start_sec = result.alternatives[0].words[0].start_time.seconds
			else:
				# bin start -> For First word of response
				start_sec = 0
			end_sec = start_sec + bin  # bin end sec

			# for last word of result
			last_word_end_sec = result.alternatives[0].words[-1].end_time.seconds

			# bin transcript
			transcript = result.alternatives[0].words[0].word

			index += 1  # subtitle index

			for i in range(len(result.alternatives[0].words) - 1):
				try:
					word = result.alternatives[0].words[i + 1].word
					word_start_sec = result.alternatives[0].words[i + 1].start_time.seconds
					word_end_sec = result.alternatives[0].words[i + 1].end_time.seconds

					if word_end_sec < end_sec:
						transcript = transcript + " " + word + " "
					else:
						previous_word_end_sec = result.alternatives[0].words[i].end_time.seconds

						# append bin transcript
						if datetime.timedelta( seconds=start_sec) < datetime.timedelta( seconds=previous_word_end_sec):
							init_sec = '0'+str(datetime.timedelta( seconds=start_sec))+'.000'
							end_sec = '0'+str(datetime.timedelta( seconds=previous_word_end_sec))+'.000'
							start.append(init_sec)
							end.append(end_sec)
							transcriptions.append(transcript)
						else:
							continue
						# reset bin parameters
						start_sec = word_start_sec
						end_sec = start_sec + bin
						transcript = result.alternatives[0].words[i + 1].word

						index += 1
				except IndexError:
					pass
			# append transcript of last transcript in bin
			if datetime.timedelta(seconds=start_sec) < datetime.timedelta(seconds=last_word_end_sec):
				init_sec = '0' + str(datetime.timedelta(seconds=start_sec)) + '.000'
				end_sec = '0' + str(datetime.timedelta(seconds=last_word_end_sec)) + '.000'
				start.append(init_sec)
				end.append(end_sec)
				transcriptions.append(transcript)
			else:
				continue

			index += 1
		except IndexError:
			pass
	return transcriptions


def translate_text(text, lang, project_id=getattr(settings, "GCLOUD_PROJECT", None)):


    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": lang,
            "target_language_code": "en-US",
        }
    )

    # Get the translation from the response
    for translation in response.translations:
        return format(translation.translated_text)


#Convert a directory with mp3 to flac
def mp3_to_flac(dir):
	for d in os.listdir(dir):
		if d.endswith('.mp3'):
			audio = AudioSegment.from_mp3(dir+d)
			audio.export(dir+d.replace('.mp3', '.flac'),format = "flac", bitrate="192k")
			os.remove(dir+d)
	return None
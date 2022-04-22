from models.summarization import summarize_text
from utils import speech_to_text as sp
import os
import settings


def process_transcripts(directory, lang='ru-RU'):
	for aud in os.listdir(directory):
		translations = []
		if (directory+aud).endswith('.flac'):
			bkt = getattr(settings, "BUCKET_NAME", None)
			gc_url, blob = sp.upload_to_gcs(directory, aud, bkt)
			response = sp.process_speech_to_txt(gc_url, lang)
			transcript = sp.generate_transcriptions(response)
			blob.delete()
			dur = round(len(transcript) / 4)
			for i in range(0, 4):
				if i == 0:
					trans = transcript[i:dur - 1]
					translations.append(sp.translate_text(''.join(trans), lang))
				else:
					trans = transcript[dur*i:(dur*i)+(dur - 1)]
					translations.append(sp.translate_text(''.join(trans), lang))
			with open('transcripts/'+aud.replace('.flac', '_translation.txt'), 'w') as f:
				for trans in translations:
					f.write(trans + "\n")
			print("transcripts completed")


def create_summaries(transcripts_dir):
	for t in os.listdir(transcripts_dir):
		summaries = []
		if t.endswith('.txt'):
			with open(transcripts_dir+t) as f:
				lines = f.readlines()
				lines.pop(0)
				for l in lines:
					suma = summarize_text(l)
					summaries.append(suma)
			with open('summaries/'+t.replace('_translation.txt', '_summary.txt'), 'w') as fi:
				for s in summaries:
					fi.write(s[0]['summary_text'] + "\n")
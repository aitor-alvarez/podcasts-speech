from models.summarization import summarize_text
from utils import speech_to_text as sp
import os
import settings


def process_summaries(directory, lang='ru-RU'):
	for aud in os.listdir(directory):
		translations = []
		if (directory+aud).endswith('.flac'):
			bkt = getattr(settings, "BUCKET_NAME", None)
			gc_url, blob = sp.upload_to_gcs(directory, aud, bkt)
			response = sp.process_speech_to_txt(gc_url, lang)
			transcript = sp.generate_transcriptions(response)
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
		summaries = [summarize_text(tr) for tr in translations]

		with open('transcripts/'+aud.replace('.flac', '_summary.txt'), 'w') as f:
			for suma in summaries:
				f.write(suma + "\n")
	print("summaries completed")

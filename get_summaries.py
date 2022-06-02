from models.summarization import summarize_text
from utils import speech_to_text as sp
import os
import settings
import pandas as pd


def process_transcripts(directory, lang='ru-RU'):
	for aud in os.listdir(directory):
		translations = []
		transcript_out = []
		if (directory+aud).endswith('.flac'):
			bkt = getattr(settings, "BUCKET_NAME", None)
			gc_url, blob = sp.upload_to_gcs(directory, aud, bkt)
			response = sp.process_speech_to_txt(gc_url, lang)
			transcript = sp.generate_transcriptions(response)
			for i, result in enumerate(response.results):
				alternative = result.alternatives[0]
				transcript_out.append(alternative.transcript)
			blob.delete()
			#translations.append(translate_transcript(transcript, lang))
			with open('transcripts/'+aud.replace('.flac', '_transcript.txt'), 'w') as f:
				for trans in transcript_out:
					f.write(trans + "\n")
	print("transcripts completed")


#Provide a directory of transcripts and translate them
def translate_transcript(transcript, lang):
	translation=[]
	dur = round(len(transcript) / 4)
	for i in range(0, 4):
		if i == 0:
			trans = transcript[i:dur - 1]
			translation.append(sp.translate_text(''.join(trans), lang))
		else:
			trans = transcript[dur * i:(dur * i) + (dur - 1)]
			translation.append(sp.translate_text(''.join(trans), lang))
	return translation


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


def get_txt_translations(data_file, lang='ru-RU'):
	df = pd.read_excel(data_file, engine='openpyxl')
	title_trans=[]
	description_trans=[]
	for i in range(0, len(df)):
		if not pd.isna(df['ZITEMDESCRIPTIONWITHOUTHTML'][i]):
			title_trans.append(sp.translate_text(df['ZCLEANEDTITLE'][i], lang))
			description_trans.append(sp.translate_text(df['ZITEMDESCRIPTIONWITHOUTHTML'][i], lang))
		else:
			title_trans.append('')
			description_trans.append('')
	df_out = pd.DataFrame({'title_translation': title_trans, 'description_translation': description_trans, 'web_url': df['ZWEBPAGEURL'],
	                       'audio_url':df['ZENCLOSUREURL'],'podcast_id':df['ZUUID'],'series_id':df['ZPODCASTUUID']})
	df_out.to_excel('Podcasts_Translate.xlsx', engine='openpyxl')
	return None


def get_txt_summaries(data_file):
	summaries=[]
	df = pd.read_excel(data_file, engine='openpyxl')
	for i in range(0, len(df)):
		if not pd.isna(df['description_translation'][i]):
			suma = summarize_text(df['description_translation'][i])
			summaries.append(suma[0]['summary_text'])
		else:
			summaries.append('')
	df['summaries'] = summaries
	df.to_excel('Podcasts_Translate.xlsx', engine='openpyxl')
	return None

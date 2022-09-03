from models.summarization import summarize_text
from utils import speech_to_text as sp
import os
import settings
import pandas as pd
from pydub.utils import mediainfo
from nltk.corpus import stopwords
import stanza

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma')

def process_transcripts(directory, lang='ru-RU'):
	for aud in os.listdir(directory):
		translations = []
		if (directory+aud).endswith('.flac'):
			bkt = getattr(settings, "BUCKET_NAME", None)
			audio_data = mediainfo(directory+aud)
			channels = int(audio_data['channels'])
			gc_url, blob = sp.upload_to_gcs(directory, aud, bkt)
			response = sp.process_speech_to_txt(gc_url, lang, channels)
			transcript = sp.generate_transcriptions(response)
			blob.delete()
			translations = translate_transcript(transcript, lang)
			with open('transcripts/'+aud.replace('.flac', '_transcript.txt'), 'w') as f:
				for trans in transcript:
					f.write(trans + "\n")
			with open('./translation/'+aud.replace('.flac', '_translationt.txt'), 'w') as t:
				for transl in translations:
					t.write(transl + "\n")
	print("transcripts completed")


#translate transcript data
def translate_transcript(transcript, lang):
	translation=[]
	dur = len(transcript)
	for i in range(0, dur):
		translation.append(sp.translate_text(transcript[i], lang))
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



def create_corpus(path):
	direct = os.listdir(path)
	corpus=[]
	for txt_file in direct:
		if txt_file.endswith('.txt'):
			txt = open('translation/' + txt_file, 'r')
			tx = txt.read()
			corpus.append(get_lemmas(tx))
	return corpus


def get_lemmas(txt):
	stop_words = set(stopwords.words('english'))
	sentence = nlp(txt)
	lemmas = [w.lemma for w in sentence.iter_words() if
	          w.text not in stop_words and w.text not in '@.,!#$%*:;"' and len(w.text) > 2]
	return lemmas
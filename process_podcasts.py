import sqlite3, os, codecs
import jieba
import pandas as pd
from pydub import AudioSegment
import get_summaries as sm
from utils.speech_to_text import translate_text
from models.openAI import get_completion_response
from time import sleep


con = sqlite3.connect("")
stop_chinese = codecs.open('zh_stopwrods.txt', 'r', 'utf-8').read().split(',')
stopwords = list(stop_chinese[0].replace("\n", ""))


def process_audio(dir, lang = "zh"):
    sm.process_transcripts(dir, lang)
    title=[]
    summary=[]
    podcast_url=[]
    duration=[]
    language_id =[]
    sophistication=[]
    author=[]
    guid=[]
    title_en=[]
    summary_lang = []
    for f in os.listdir(dir):
        if f.endswith('.txt'):
            try:
                sound = AudioSegment.from_file(dir+f.replace("_transcript.txt", ".flac"))
                cur = con.cursor()
                zuid = f.replace("_transcript.txt", "")
                data = cur.execute('select ztitle, zwebpageurl, zauthor from ZMTEPISODE where ZUUID="'+zuid+'"').fetchone()
                txt = open(dir + f).readlines()
                txt_suma = ' '.join(txt[0:10])
                text = ' '.join(txt).split()
                suma = get_completion_response([{'role': 'user', 'content': 'Create a summary in English:'+txt_suma}])
                summary.append(suma['choices'][0]['message']['content'])
                title.append(data[0])
                podcast_url.append(data[1])
                duration.append(sound.duration_seconds*1000000)
                language_id.append(1)
                ws = jieba.lcut(' '.join(txt), cut_all=True)
                words = [t for t in ws if t not in stopwords]
                density = (len(words) / len(text))
                speech_rate = round(len(words) / sound.duration_seconds)
                speech_density = round((0.6 * density) + (0.4 * speech_rate))
                sophistication.append(speech_density)
                author.append(data[2])
                guid.append(zuid)
                translate_title = translate_text(data[0], lang)
                title_en.append(translate_title)
                summary_lang.append(txt_suma)
                sleep(25)
            except Exception as e:
                print(e)
                print(f)

    df = pd.DataFrame({'title': title, 'summary':summary, 'podcast_url': podcast_url, 'duration': duration, 'language_id': language_id, 'sophistication': sophistication,
             'author': author, 'guid': guid, 'title_en': title_en, 'summary_lang':summary_lang})

    df.to_excel(dir+'chinese_podcasts.xlsx', engine='openpyxl')
    print("Podcasts data extracted")

    return None

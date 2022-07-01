import os
import pandas as pd
import requests


def download_resources(data_file, direct):
	assert os.path.isfile(data_file)
	df = pd.read_excel(data_file, engine='openpyxl')
	for i in range(0, len(df)):
		audio_file = requests.get(df['ZENCLOSUREURL'][i])
		with open(direct+df['ZUUID'][i], 'wb') as aud:
			aud.write(audio_file.content)
	print("Audio files downloaded")
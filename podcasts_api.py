import requests
import json
from time import sleep
import pandas as pd

class Podcast:

	def __init__(self, keywords, country, language):
		self.keywords = keywords
		self.language = language
		self.country = country
		self.base_url = 'https://itunes.apple.com/search?term='


	def get_podcast_data(self, term):
		url = self.base_url+term+"&limit=200&country="+self.country+"&lan="+self.language+"&entity=podcast"

		try:
			response_data = requests.get(url)
			response = json.load(response_data)
			if response['resultCount'] >0:
				return response
			else:
				return None

		except ValueError:
			pass


	def create_dataset(self):
		name=[]
		creator=[]
		creator_url=[]
		collection=[]
		collection_url=[]
		url=[]
		primaryGenre=[]
		col_names=['name', 'url', 'primaryGenre', 'creator', 'creator_url', 'collection', 'creator_url']

		for term in self.keywords:
			data = self.get_podcast_data(term)
			if data is not None:
				name.append(data['response']['trackName'])
				creator.append(data['response']['artistName'])
				collection.append(data['response']['collectionName'])
				creator_url.append(data['response']['artistViewUrl'])
				url.append(data['response']['trackViewUrl'])
				collection_url.append(data['response']['collectionViewUrl'])
				primaryGenre.append(data['response']['primaryGenre'])
				sleep(3)
			else:
				sleep(2)
				continue

			df = pd.DataFrame([name, url, primaryGenre, creator, creator_url, collection, creator_url ])
			df.columns = col_names

			return df



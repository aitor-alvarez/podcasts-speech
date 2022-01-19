import requests
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
			response = response_data.json()
			if response['resultCount'] >0:
				return response
			else:
				return None

		except ValueError:
			pass


	def create_dataset(self):
		name=[]
		creator=[]
		collection=[]
		collection_url=[]
		url=[]
		primaryGenre=[]

		for term in self.keywords:
			data = self.get_podcast_data(term)
			if data is not None:
				for result in data['results']:
					try:
						name.append(result['trackName'])
						creator.append(result['artistName'])
						collection.append(result['collectionName'])
						url.append(result['trackViewUrl'])
						collection_url.append(result['collectionViewUrl'])
						primaryGenre.append(result['primaryGenreName'])
					except:
						continue
			else:
				pass
			sleep(3)

		df = pd.DataFrame({'name':name, 'url':url, 'primaryGenre':primaryGenre, 'creator':creator, 'collection':collection, 'collection url': collection_url})

		return df



from podcasts_api import Podcast
import argparse
import pandas as pd


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', '--keywords', type=str, default=None,
	                    help='Excel spreadsheet with list of words')

	parser.add_argument('-c', '--country', type=str, default=None,
	                    help='country as a string')

	parser.add_argument('-l', '--language', type=str, default=None,
	                    help='language as a string')

	parser.add_argument('-o', '--output_path', type=str, default=None,
	                    help='Text file used as a reference to be compared against')

	args = parser.parse_args()
	keywords = pd.read_excel(args.keywords, engine='openpyxl')
	keywords = keywords['tokens'].tolist()
	pod = Podcast(keywords, args.country, args.language)
	dataset = pod.create_dataset()
	dataset.to_excel(args.output_path)


if __name__ == '__main__':
	main()
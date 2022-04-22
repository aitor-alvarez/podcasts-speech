from podcasts_api import Podcast
import argparse
import pandas as pd
import get_summaries as sm


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', '--keywords', type=str, default=None,
	                    help='Excel spreadsheet with list of words')

	parser.add_argument('-c', '--country', type=str, default=None,
	                    help='country as a string')

	parser.add_argument('-l', '--language', type=str, default=None,
	                    help='language as a string')

	parser.add_argument('-o', '--output_path', type=str, default=None,
	                    help='Output Excel file path + filename')

	parser.add_argument('-a', '--audio_dir', type=str, default=None,
	                    help='Audio directory to obtain summaries and topics')

	args = parser.parse_args()
	if args.keywords:
		keywords = pd.read_excel(args.keywords, engine='openpyxl')
		keywords = keywords['tokens'].tolist()
		pod = Podcast(keywords, args.country, args.language)
		dataset = pod.create_dataset()
		dataset.to_excel(args.output_path, engine='openpyxl')
	elif args.audio_dir:
		sm.process_summaries(args.audio_dir)




if __name__ == '__main__':
	main()
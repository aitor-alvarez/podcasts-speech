from podcasts_api import Podcast
import argparse


def main(keywords, country, out_path):
	pod = Podcast(keywords, country)
	dataset = pod.create_dataset()
	dataset.to_excel(out_path)


if __name__ == '__main__':
	#TODO get data from arguments from argparse
	main()
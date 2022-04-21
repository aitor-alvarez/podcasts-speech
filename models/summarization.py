from transformers.pipelines import pipeline


def summarize_text(text_file):
	summary = pipeline("summarization")
	f = open(text_file, "r", encoding="latin1")
	txt = f.readlines()
	summarized = summary(txt, min_length=65, max_length=150)
	return summarized

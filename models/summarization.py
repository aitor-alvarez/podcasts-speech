from transformers.pipelines import pipeline


def summarize_text(txt):
	summary = pipeline("summarization")
	summarized = summary(txt, min_length=20, max_length=80)
	return summarized

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

def textrank_extract(text, num_sentences=4):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    return " ".join(str(s) for s in TextRankSummarizer()(parser.document, num_sentences))

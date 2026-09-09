from pathlib import Path
from core.corpus.manager import CorpusManager

DATA_DIR = Path(__file__).parent.parent / 'data'
corpus = CorpusManager(DATA_DIR)

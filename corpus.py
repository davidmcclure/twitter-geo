

import ujson
import re
import attr

from gensim.models.word2vec import Word2Vec

from utils import scan_paths


@attr.s
class Corpus:

    root = attr.ib()

    def paths(self):
        """Generate partition paths.
        """
        return scan_paths(self.root, '\.json')

    def tweets(self):
        """Generate parsed tweets.
        """
        for path in self.paths():
            with open(path) as fh:
                for line in fh:
                    yield ujson.loads(line)

    def filtered_tweets(self, key):
        raise NotImplementedError

    def sentences(self, key):
        """Generate sentences for a key.
        """
        for tweet in self.filtered_tweets(key):

            text = re.sub(r"http\S+", "", tweet['text'])

            yield re.findall('[a-z0-9#@]+', text)

    def word2vec_model(self, state):
        """Train a model for a state.
        """
        sents = list(self.sentences(state))

        return Word2Vec(sents, size=100, min_count=10, workers=8)


class StateCorpus(Corpus):

    def filtered_tweets(self, state):
        """Generate sentences for a state.
        """
        for tweet in self.tweets():
            if tweet['state'] == state:
                yield tweet


class CityCorpus(Corpus):

    def filtered_tweets(self, city):
        """Generate sentences for a city.
        """
        for tweet in self.tweets():
            if tweet['city'] == city:
                yield tweet

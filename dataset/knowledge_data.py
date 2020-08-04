import json
from collections import Counter
from os import listdir
from os.path import isfile, join
from typing import List, Dict, Tuple

from config import DatasetConfig
from util import load_pkl, save_pkl


class AttributeData:
    def __init__(self, key_vocab=None, value_vocab=None):
        self.key_vocab: Dict[str, int] = key_vocab
        self.value_vocab: Dict[Tuple[int, str], int] = value_vocab

    def __repr__(self):
        res = ''
        res += 'key_vocab: ' + self.key_vocab.__repr__() + '\n'
        res += 'value_vocab: ' + self.value_vocab.__repr__() + '\n'
        return res

    @staticmethod
    def from_file():
        key_vocab = {attr: idx for idx, attr in
                     enumerate(DatasetConfig.product_attributes)}
        value_vocab = {}

        # Count value of each attribute.
        counters: Dict[str, Counter] = {attr: Counter() for attr in
                                        DatasetConfig.product_attributes}
        print('Building attribute data from files...')
        files = listdir(DatasetConfig.product_data_directory)
        print('# Product files: {}'.format(len(files)))
        for idx, file_name in enumerate(files):
            if (idx + 1) % 1000 == 0:
                print('{} / {}'.format(idx + 1, len(files)))
            file_path = join(DatasetConfig.product_data_directory, file_name)
            with open(file_path, 'r') as file:
                product_json: Dict[str, str] = json.load(file)
            for key, value in product_json.items():
                if key in counters:
                    key = key.lower()
                    value = value.lower()
                    counters[key].update([value])

        # Assign an index for each value.
        for key, counter in counters.items():
            key_id = key_vocab[key]
            values = [word for word, freq in counter.most_common() if
                      freq >= DatasetConfig.product_value_cutoff]
            for value in values:
                value_vocab[(key_id, value)] = len(value_vocab)
            print("Key {}: {}".format(key, len(values)))

        return AttributeData(key_vocab, value_vocab)


class KnowledgeData:
    def __init__(self):
        self.styletips_data: StyleTipsData = None
        self.celebrity_data: CelebrityData = None
        self.attribute_data: AttributeData = None

        if isfile(DatasetConfig.knowledge_data_file):
            # Read existed extracted data files.
            knowledge_data = load_pkl(DatasetConfig.knowledge_data_file)
            self.attribute_data = knowledge_data.attribute_data
        else:
            # Load data from raw data file and save them into pkl.
            self.attribute_data = AttributeData.from_file()
            save_pkl(self, 'KnowledgeData', DatasetConfig.knowledge_data_file)

    def __repr__(self):
        res = ''
        res += 'attribute_data: ' + self.attribute_data.__repr__() + '\n'
        return res

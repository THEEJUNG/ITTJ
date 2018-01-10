import os,sys
import pandas as pd
import zipfile
import collections
from tensorflow.contrib import learn
import numpy as np

from utils import lowerr

class TimeSeriesDataLoader():

    def __init__(self, data_path, filename, feature = ['volatil'], ticker="AAPL", start_date="1990-01-01", end_date="2010-12-31", seq_len = 12, step = 1, test_size = 12, normalize = False):
        self.data_path = data_path
        self.filename = filename
        self.feature = feature
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.seq_len = seq_len
        self.step = step
        self.normalize = normalize
        self.test_size = test_size


    def load_data(self):
        # 1. Load all CSV file to pandas Dataframe, indexing with timestamp
        df = pd.read_csv(os.path.join(self.data_path, self.filename), header = 0)

        #print df.head(), df['ym'].head()
        df.index = pd.to_datetime(df['ym'])

        # 2. Left df only specific company and period

        df = df.loc[df['ticker'] == self.ticker]
        df = df[self.start_date:self.end_date]

        #print(len(df))

        # 3. Make a 3-dim array [N x W x F] N = num of train, W = seq length, F = num of features
        df_array = np.array(df[self.feature]).transpose()
        sequence_length = self.seq_len + self.step
        print self.seq_len, self.step

        for f in df_array: #what if we have several features?
            result = list()
            #print len(f) - sequence_length
            for i in xrange(len(f) - sequence_length+1):
                #print f[i:i+sequence_length]
                result.append(f[i:i+sequence_length])

            result = np.array(result)
            print len(result)

            train_size = len(result) -self.test_size
            train, test = result[:train_size], result[train_size:]
            self.train_x, self.train_y = train[:,:-1*self.step], train[:,-1*self.step:]
            self.test_x, self.test_y = test[:,:-1*self.step], test[:,-1*self.step:]

            print len(self.train_x), len(self.train_y), len(self.test_x), len(self.test_y)
            print self.train_x[0], self.train_y[0], self.train_x[1], self.train_y[1]

            # 4. Normalize window if normalize_window = True

            if self.normalize:
                self.normalize_window(self.train_x)
                self.normalize_window(self.test_x)

            self.train_x = np.reshape(self.train_x, (self.train_x.shape[0], self.train_x.shape[1],len(self.feature)))
            self.test_x = np.reshape(self.test_x, (self.test_x.shape[0], self.test_x.shape[1], len(self.feature)))




    def normalize_window(self, arr):
        array_change = []

        for list in arr:
            array_change.append([(float(p)/list[0]) - 1 for p in list])

        arr = array_change





class DataLoader():
    def __init__ (self, data_path, train_filename, pad_size=10, max_vocab=False):
        self.data_path = data_path
        self.train_filename = train_filename
        self.pad_size = pad_size  # based on average length of sentences: 6.89 #TODO get from data late
        self.max_vocab = max_vocab
        self.train = []
        self.test = []
        self.num_class = -1

    def read_data(self):
        # road train data into pandas DataFrame
        with zipfile.ZipFile(os.path.abspath(self.data_path + self.train_filename)) as z:
            with z.open(z.namelist()[0]) as f:
                train = pd.read_csv(f, header=0, delimiter='\t')
        print 'Load train data done!'

        train_sentence, self.length = lowerr(train.Phrase)
        self.create_vocab(train_sentence)
        self.y = train.Sentiment

        vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length=self.pad_size)
        vocab_processor.fit(self.vocab)
        X = list(vocab_processor.fit_transform(train_sentence))
        print 'X transformation Done!'

        ## Train vs Test
        df = pd.DataFrame({'X': X, 'Y': self.y, 'length': self.length})
        df = df.sample(frac=1, random_state=63).reset_index(drop=True)
        test_len = np.floor(len(df) * 0.1)
        self.test, self.train = df.ix[:test_len - 1], df.ix[test_len:]
        self.num_class = len(np.unique(df.Y))
        print 'Train/Test split Done!', len(X)


    def create_vocab(self,train_sentence):
        # Top n vocab only!
        # n = 20000  # We can change it if we want!
        flat_sentences = [z for y in [x.strip().split(' ') for x in train_sentence] for z in y]
        #print 'Number of Words in Train', len(flat_sentences)
        #print flat_sentences[:100]

        freq_dict = collections.Counter(flat_sentences)
        print 'Create Vocab: Top 10 freq words and freq', freq_dict.most_common(10)
        #print '1st, 2nd, 3rd freq Words', freq_dict.most_common(100)[0][0], freq_dict.most_common(100)[1][0], freq_dict.most_common(100)[2][0]

        if self.max_vocab:
            freq_list = freq_dict.most_common(self.max_vocab)
        else:
            freq_list = freq_dict.most_common()
        self.vocab = [k for k,c in freq_list]

        print "Create Vocab Done!", len(self.vocab)






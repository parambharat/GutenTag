import os
import cPickle as pickle
import settings
from collections import defaultdict, OrderedDict
from matplotlib import pylab as plt
import numpy as np
# from pprint import pprint
import shutil
import logging

logger = logging.getLogger('text_similar')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def get_genres():
    logger.info("Fetching genres from pickle")
    genre_file = os.path.join(settings.project_root,
                              'tmp', 'One_Genre.pickle.new')
    gf = open(genre_file, 'rb')
    genres = pickle.load(gf)
    gf.close()
    logger.info("Fetched genres from pickle")
    return genres


def clean_genres(genres):
    logger.info("Clening genres")
    for doc, genre in genres.iteritems():
        if genre == u'[General Cryptor':
            genres[doc] = genre.strip('[')
        else:
            continue
    cleaned_genres = {str(doc): genre for doc, genre in genres.iteritems()}
    logger.info("Cleaned Genres")
    return cleaned_genres


def sample_genres(genres, hist=None, top=None, count=None):
    logger.info("Creating Samples")
    samples = defaultdict(list)
    if not count:
        logger.info("Using samples size == least genre's sample size")
        count = hist.items()[top-1][1]
    elif hist and count > hist.items()[top-1][1]:
        logger.info("More samples requested than lowest population\
              falling back to least population")
        count = hist.items()[top-1][1]
    if not hist:
        logger.info("Creating samples for the top 10")
        genre_list = [u'Hurt/Comfort']
    else:
        genre_list = set([key for key, _ in hist.items()[:top]])
    logger.info("Generating Samples")
    for key, item in genres.iteritems():
        if item in genre_list:
            samples[item].append(key)
    logger.info("Reducing Samples to {}".format(count))
    for key, value in samples.iteritems():
        samples[key] = np.random.choice(value, count, replace=False)
    logger.info("Sampled successfully")
    return samples


def sample_paths(samples):
    logger.info("Geberating paths for sample files")
    for key, values in samples.iteritems():
        samples[key] = [os.path.join(settings.project_root, 'tmp',
                                     'test_files', '{}.txt'.format(value))
                        for value in values]
    logger.info("Sample Paths Generated Successfully")
    return samples


def copy_samples(samples):
    logger.info("copying Samples")
    for key, values in samples.iteritems():
        genre_dir = os.path.join(settings.project_root, 'tmp',
                                 'sample_dir', key)
        os.mkdir(genre_dir)
        logger.info("Copying {} samples to {}".format(key, genre_dir))
        counter = 0
        for value in values:
            shutil.copy(value, genre_dir)
            counter += 1
            if counter % 100 == 0:
                logger.info("Copied {} samples to {} folder".format(counter,
                                                                    genre_dir))


def create_hist(genres):
    hist = defaultdict(int)
    for item in genres.itervalues():
        hist[item] += 1
    return hist


def normalize_hist(hist):
    norm = float(sum(hist.values()))
    for key, value in hist.iteritems():
        hist[key] = value/norm
    return hist


def plot_data(hist):
    X = np.arange(len(hist))
    plt.bar(X, hist.values(), align='center', width=0.5)
    plt.xticks(X, hist.keys())
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    ymax = max(hist.values()) + 0.1
    plt.ylim(0, ymax)
    plt.show()


def remove_genres(genres, *keys):
    for key in keys:
        del genres[key]
    return genres

if __name__ == '__main__':
    genres = get_genres()
    genres = clean_genres(genres)
    hist = create_hist(genres)
    hist = OrderedDict((item, hist[item]) for item in
                       sorted(hist, key=hist.get, reverse=True))

    samples = sample_genres(genres, count=20000)
    samples = sample_paths(samples)
    copy_samples(samples)

"""
    for value in samples.values():
        print(os.path.isfile(value[0]))

    hist = normalize_hist(hist)
    remove_keys = [u'General Cryptor', u'General Woundwart',
                   u'Western', u'Spiritual']
    hist = remove_genres(hist, *remove_keys)
    hist = normalize_hist(hist)
    pprint(hist)
    plot_data(hist)
"""

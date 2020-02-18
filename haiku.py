import json
import os
import random as rnd
import re
from io import BytesIO
from pickle import dump, load
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from PIL import Image, ImageDraw, ImageFont
import tweepy

PIXABAY_URL = 'https://pixabay.com/api/'
PIXABAY_KEY = os.getenv('PIXABAY_KEY')

SYLLABLE_FILE = "../syllables.p"
DATA_FILE = "nettalk.data"
COMMON_WORDS_FILE = "common-words.txt"
FONT_STYLE = 'Raleway-Light.ttf'
OUTPUT_DIR = "../imgs/"

MR_PEANUT = "https://i.ytimg.com/vi/fkKEVt3f5Vo/maxresdefault.jpg"

TWT_API_KEY = os.getenv('TWT_API_KEY')
TWT_API_SECRET = os.getenv('TWT_API_SECRET')
TWT_ACCESS_KEY = os.getenv('TWT_ACCESS_KEY')
TWT_ACCESS_SECRET = os.getenv('TWT_ACCESS_SECRET')

FONT_SIZE = 80
FONT = ImageFont.truetype(FONT_STYLE, size=FONT_SIZE)
EXCLAMATIONS = ['.', '?', '!', '...']

twitter_auth = tweepy.OAuthHandler(TWT_API_KEY, TWT_API_SECRET)
twitter_auth.set_access_token(TWT_ACCESS_KEY, TWT_ACCESS_SECRET)
twt_api = tweepy.API(twitter_auth)

sched = BlockingScheduler()

def centered_random(x):
    section = x / 3
    return round(rnd.randint(0, round(x - section)) + section / 10)


def get_image(keyword, range=3):
    response = requests.get(PIXABAY_URL, {
        'key': PIXABAY_KEY,
        'q': keyword, 'per_page': range
    })

    data = json.loads(response.text)
    if len(data['hits']) < 1:
        return ""

    return data['hits'][rnd.randint(0, len(data['hits']) - 1)]['largeImageURL']


class HaikuGenerator:

    def __init__(self):
        if os.path.isfile(SYLLABLE_FILE):
            self.syls_to_word = load(open(SYLLABLE_FILE, "rb"))
            print(f"Loaded {SYLLABLE_FILE}")
        else:
            self.syls_to_word = self.load_data()
            dump(self.syls_to_word, open(SYLLABLE_FILE, "wb"))
            print(f"Generated and saved {SYLLABLE_FILE}")

    def load_data(self):
        with open(COMMON_WORDS_FILE, 'r') as common_f:
            common_words = [word.rstrip() for word in common_f.readlines()]

        with open(DATA_FILE, 'r') as f:
            syl_data = f.readlines()[10:]
            syl_data = map(lambda x: x.split(), syl_data)
            syl_data = [[entry[0], entry[2]] for entry in syl_data if entry[0] in common_words]
            syl_data = [[word, len([i for i in re.split(r'\D', syls) if i])] for word, syls in syl_data]

        # syls_to_word is a dictionary with the keys k as syllables,
        # and values v being a list of words with k syllables.

        data = dict()
        for k, v in dict(syl_data).items():
            if v in data:
                data[v].append(k)
            else:
                data[v] = list([k])

        return data

    def generate_haiku(self, structure=[5, 7, 5]):
        result = [[], [], []]
        for idx, line_count in enumerate(structure):
            remaining = line_count
            while remaining > 0:
                min_syllables = min(remaining, max(self.syls_to_word.keys()))
                word_syls = rnd.randint(1, min_syllables)

                chosen_index = rnd.randint(0, len(self.syls_to_word[word_syls]) - 1)
                chosen_word = self.syls_to_word[word_syls][chosen_index]
                result[idx].append(chosen_word)
                remaining -= word_syls

        results = dict()
        results['num_words'] = [len(line) for line in result]
        haiku_string = ', '.join([' '.join(line) for line in result])
        results['haiku'] = haiku_string + EXCLAMATIONS[rnd.randint(0, len(EXCLAMATIONS) - 1)]

        words = results['haiku'].replace(',', '').split()
        results['img_word'] = words[rnd.randint(0, len(words) - 1)]
        results['img_url'] = get_image(results['img_word'])
        return results

    def generate_img(self, haiku_data, font, font_size):
        if rnd.randint(0, 100) > 95:
            img = Image.open(BytesIO(requests.get(MR_PEANUT).content))
        else:
            img = Image.open(BytesIO(requests.get(haiku_data['img_url']).content))

        poem = haiku_data['haiku']
        img_size = img.size
        draw = ImageDraw.Draw(img)

        pixels = img.getdata()
        average_rgb = [sum(rgb) / len(rgb) for rgb in zip(*pixels)]
        text_color = "#FFFFFF" if all(map(lambda x: x < 125, average_rgb)) else "#000000"

        text_height_pos = centered_random(img_size[1])

        poem_lines = poem.split(",")
        for idx, line in enumerate(poem_lines):
            line = line.strip()
            line = line + "," if idx != len(poem_lines) - 1 else line
            draw.text((20, text_height_pos), line, fill=text_color, font=font)
            text_height_pos += font.getsize(line)[1]

        img_name = OUTPUT_DIR + poem[:10].replace(" ", "").replace(",", "") + str(rnd.randint(1, 100)) + ".jpg"
        img.save(img_name)
        return img_name


def generate_and_post_tweet():
    try:
        twt_api.verify_credentials()
        print("Valid Twitter credentials!")

        generator = HaikuGenerator()

        haiku_data = generator.generate_haiku()
        while not haiku_data['img_url']:
            haiku_data = generator.generate_haiku()

        tweet_img_name = generator.generate_img(haiku_data, FONT, FONT_SIZE)

        media_upload = twt_api.media_upload(tweet_img_name)
        print("Successfully uploaded Image data!")

        twt_api.update_status(status=haiku_data['haiku'], media_ids=[media_upload.media_id_string])
        print("Successfully posted tweet!")

    except:
        print("Invalid Twitter credentials..")


@sched.scheduled_job('interval', minutes=60)
def start_process():
    generate_and_post_tweet()


sched.start()

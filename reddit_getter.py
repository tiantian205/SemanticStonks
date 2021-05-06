import praw
import csv
import lexicon
import re
from typing import Dict, List, Set
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import stock


def get_lm_dict(file: str) -> Dict:
    """return a dict of words with semantics"""
    ret = {}
    if file == 'data/lm_positive.csv':
        with open(file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                ret[row[0]] = 0.5
    elif file == 'data/lm_positive.csv':
        with open(file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                ret[row[0]] = -0.5
    else:
        raise NameError
    return ret


def get_stock_names_and_indices(name: str) -> Dict:
    """return a dict of the form {ticker: company name} from the csv file"""
    comps = {}
    with open(name, 'r') as file:
        reader = csv.reader(file)

        # This skips the first row of the CSV file.
        next(reader)

        for row in reader:
            if '^' not in row[0]:
                comps[row[0]] = row[1].replace('"', '')  # {ticker: name}

    return comps


def get_stock_names(name: str) -> Set:
    """return s set filled with company names from csv file"""
    names = set()
    with open(name, 'r') as file:
        reader = csv.reader(file)

        # This skips the first row of the CSV file.
        next(reader)

        for row in reader:
            if '^' not in row[0]:
                names.add(row[1].replace('"', ''))

    return names


def name_to_index(all_comps: dict, name: str) -> str:
    """return the company's stock index from the company's name"""
    for c in all_comps:
        if name.lower() in all_comps[c].lower().split(" "):
            return c


def get_ticker(msg: str, comps: Set) -> str:
    """interprets a string to notice to a relatively accurate degree which stock/company is
    mentioned, and returns the said company ticker. Return None if the string itself doesn't
    explicitly mention any company/stock"""
    p = msg.split(" ")
    for word in p:
        if word != '' and len(word) > 1:
            word = re.sub('[^A-Za-z0-9]+', '', word)
            if (word in stocks) and word not in lexicon.blacklist:
                return word.replace('$', '')
            elif any({word in w.replace('"', '').replace(',', '').split(" ") for w in comps}) \
                    and word.lower() not in lexicon.common and word not in lexicon.blacklist \
                    and word.isalpha():
                return name_to_index(stocks, word)
    return "None"


def interpret_sentiment(txt: str) -> float:
    """uses nltk's vader with modification to interpret the attitute of the given text"""
    analyser = SentimentIntensityAnalyzer()
    analyser.lexicon.update(lexicon.wsb_words)
    analyser.lexicon.update(lexicon.emojis)
    return analyser.polarity_scores(txt)['compound']


def find_ticker(lst: List[stock.Stock], t: str) -> stock.Stock:
    for s in lst:
        if s.get_name() == t:
            return s


if __name__ == '__main__':
    stocks = get_stock_names_and_indices(
        'data/nyse.csv') | get_stock_names_and_indices(
        'data/nasdaq.csv')
    companies = get_stock_names('data/nyse.csv').union(get_stock_names('data/nasdaq.csv'))
    reddit = praw.Reddit(
        user_agent="Comment Extraction",
        client_id="fv4OUTKIhmmUHA",
        client_secret="ab7LLxoLxstwV5XYJJ8NY4I-1cbgAA",
    )

    subreddit = 'wallstreetbets'
    sub = reddit.subreddit(subreddit)
    all_mentioned_stocks = []
    for submission in sub.new(limit=20):
        if "Daily Discussion Thread for" not in submission.title:
            focus_ticker = get_ticker(submission.title, companies)
            if focus_ticker == 'None':
                focus_ticker = get_ticker(submission.selftext.replace('\n', ' '), companies)

            if focus_ticker != 'None':
                post_sentiment = interpret_sentiment(
                    submission.title + ' ' + submission.selftext.replace('\n', ' '))
                if focus_ticker not in [s.get_name() for s in all_mentioned_stocks]:
                    ticker = stock.Stock(focus_ticker)
                    all_mentioned_stocks.append(ticker)
                    ticker.add_to_mentions(1 + len(submission.comments))
                    ticker.add_sentiment((1 + len(submission.comments)) * post_sentiment)
                else:
                    ticker = find_ticker(all_mentioned_stocks, focus_ticker)
                    ticker.add_to_mentions(1 + len(submission.comments))
                    ticker.add_sentiment((1 + len(submission.comments)) * post_sentiment)
                print('-----------start of post-------------')
                print("POST TITLE: " + submission.title)
                print("POST BODY: " + submission.selftext.replace('\n', ' '))
                print("POST TICKER: " + focus_ticker)
                print("POST SENTIMENT: " + str(post_sentiment))
                submission.comments.replace_more(limit=100)
                for comment in submission.comments.list():
                    if comment.score >= 0 and 'bot' not in comment.body and comment.body is not None:
                        print('\t' + "comment: " + comment.body.replace('\n', ' '))
                        comment_sentiment = interpret_sentiment(comment.body.replace('\n', ' '))
                        ticker.add_to_mentions(1)
                        ticker.add_sentiment(comment_sentiment)
                print("---------------end of post-----------------")
    print("####################################################################################")
    for t in all_mentioned_stocks:
        print("ticker: " + t.get_name() + "  ---- average sentiment: " + str(t.get_average_sentiment()))

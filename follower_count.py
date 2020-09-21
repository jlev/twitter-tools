from __future__ import unicode_literals
import os, sys
import csv, codecs
import argparse
import tweepy

consumer_key = os.environ.get('TWITTER_CONSUMER_TOKEN')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')

if consumer_key and consumer_secret:
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
else:
    print('need to set TWITTER_CONSUMER_TOKEN and TWITTER_CONSUMER_SECRET in .env')
    sys.exit(-1)

access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWITTER_ACCESS_SECRET')
if access_token and access_token_secret:
    auth.set_access_token(access_token, access_token_secret)

def open_csv(filename):
    targets = []
    with open(filename, 'r') as targets_file:
        reader = csv.DictReader(targets_file)
        for row in reader:
            handle = row['twitter'].replace('@', '').replace('https://twitter.com/', '')
            targets.append(handle)

    return targets

def get_users(targets, write_to):
    outfile = csv.DictWriter(write_to, fieldnames=['UID', 'Username', 'Follower Count', 'Verified'])
    outfile.writeheader()

    for idx, target in enumerate(targets):
        try:
            user = api.get_user(target)
            outfile.writerow({'UID': target, 'Username': user.name, 'Follower Count': user.followers_count, 'Verified': user.verified})
        except tweepy.TweepError as e:
            print(idx, target, e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get follow count from input list')
    parser.add_argument('--list', type=str, nargs='+', help='stdin')
    parser.add_argument('--in', dest='filein', type=str, nargs=1, help='CSV file to read in')
    parser.add_argument('--out', dest='fileout', type=str, nargs=1, help='CSV file to write out')
    args = parser.parse_args()

    if args.filein:
        targets = open_csv(args.filein[0])
    elif args.list:
        targets = args.list
    else:
        parser.print_help()
        sys.exit(-1)

    if args.fileout:
        with codecs.open(args.fileout[0], 'wb', 'utf-8') as outcsv:
            get_users(targets, outcsv)
    else:
        get_users(targets, sys.stdout)

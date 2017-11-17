"""
Tweets downloaded in csv file in the following format:
<Tweet ID> <Date> <Tweet-Text> <Media-URL>
It only downloads those tweets which contains both Hash-Tags and ImageUrls.
It recursively adds the UserName from seed Users and downloads their tweets recursively as well. 
It also  keeps track of users already crawled.

"""


import tweepy #https://github.com/tweepy/tweepy
import csv
import sys
import re
#Twitter API credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""


USERS = []
CRAWLED = []
def get_all_tweets():
        #Twitter only allows access to a users most recent 3240 tweets with this method

        #authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        #initialize a list to hold all the tweepy Tweets
        while(1):
            for screen_name in USERS:
                CRAWLED.append(screen_name) 
                alltweets = []
                print "getting tweets for user: %s" % (screen_name)
                #make initial request for most recent tweets (200 is the maximum allowed count)
                new_tweets = api.user_timeline(screen_name = screen_name,count=1)

                #save most recent tweets
                alltweets.extend(new_tweets)
                

                #save the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

                #keep grabbing tweets until there are no tweets left to grab
                while len(new_tweets) > 0:
                        print "getting tweets before %s" % (oldest)

                        #all subsequent requests use the max_id param to prevent duplicates
                        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
                        #print new_tweets
                        #save most recent tweets
                        alltweets.extend(new_tweets)

                        #update the id of the oldest tweet less one
                        oldest = alltweets[-1].id - 1

                        print "...%s tweets downloaded so far" % (len(alltweets))

                #go through all found tweets and remove the ones with no images 
                outtweets = [] #initialize master list to hold our ready tweets
                #add new users to list
                for tw in alltweets:
                    new_users = re.findall(r'@([a-zA-Z0-9_]*?)[^a-zA-Z0-9_]',
                                            tw.text.encode('utf-8').replace('@', ' @'))
                    #sys.stderr.write('Found new users\n')
                    
                    for user_ in new_users:
                        if user_ not in CRAWLED:
                            xuser_ = re.sub(r'[0-9_]', r'', user_)
                            if not xuser_:
                                continue
                            xuser_ = re.sub(r'([A-Z])', r' \1', xuser_).split()
                            # if any(elm.score(' '.join(w.lower())) < hlm.score(' '.join(w.lower())) for w in xuser_):
                            #     continue
                            sys.stderr.write('user ``%s`` added\n' % user_)
                            USERS.append(user_)
                            print "user added: %s" % user_
                for tweet in alltweets:
                    #not all tweets will have media url, so lets skip them
                    try:
                        print tweet.entities['media'][0]['media_url']
                    except (NameError, KeyError):
                        #we dont want to have any entries without the media_url so lets do nothing
                        pass
                    else:
                        #remove those tweets that doesnot containn #tags in text
                        tmp = re.findall(r"(?:^|\s)[#]{1}(\w+)", tweet.text.encode("utf-8"))
                        if(len(tmp) != 0):

                        #got media_url - means add it to the output
                            outtweets.append([tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.entities['media'][0]['media_url']])
                        else:
                            continue

                #write the csv  
                with open('%s_tweets.csv' % screen_name, 'wb') as f:
                    writer = csv.writer(f)
                    writer.writerow(["id","created_at","text","media_url"])
                    writer.writerows(outtweets)
                f.close()
                pass


if __name__ == '__main__':
        #pass in the username of the account you want to download
        #USERS.append("instagram")
        USERS.append("nytimes")
        get_all_tweets()

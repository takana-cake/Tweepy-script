# _*_ coding: utf-8 _*_

twitter_conf = {
	'consumer' : {
		'key'   : "",
		'secret' : ""
	},
	'access'   : {
		'key'   : "",
		'secret' : ""
	}
}

### tweepy ###

def tweepyauth():
	import tweepy
	auth = tweepy.OAuthHandler(
		twitter_conf['consumer']['key'],
		twitter_conf['consumer']['secret'])
	auth.set_access_token(
		twitter_conf['access']['key'],
		twitter_conf['access']['secret'])
	tweepy_auth = tweepy.API(auth)
	return(tweepy_auth)

### OAuth ###

def oaauth():
	from requests_oauthlib import OAuth1Session
	twitter = OAuth1Session(
		twitter_conf['consumer']['key'],
		twitter_conf['consumer']['secret'],
		twitter_conf['access']['key'],
		twitter_conf['access']['secret'],
	)
	return(twitter)

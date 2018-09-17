# _*_ coding: utf-8 _*_

'''

### flow(予定) ###

'''

import tweepy
import json


# 認証
def tweepy_api():
	twitter_conf = {
		'consumer' : {
		'key'	: "",
		'secret' : ""
		},
		'access'   : {
		'key'	: "",
		'secret' : ""
		}
	}
	auth = tweepy.OAuthHandler(
		twitter_conf['consumer']['key'],
		twitter_conf['consumer']['secret'])
	auth.set_access_token(
		twitter_conf['access']['key'],
		twitter_conf['access']['secret'])
	tweepy_auth = tweepy.API(auth)
	return(tweepy_auth)

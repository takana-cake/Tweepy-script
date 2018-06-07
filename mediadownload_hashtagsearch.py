# _*_ coding: utf-8 _*_

import tweepy
import sys
import urllib.request
import os
import datetime
import time
import json


# 認証
twitter_conf = {
    'consumer' : {
        'key'    : "",
        'secret' : ""
    },
    'access'   : {
        'key'    : "",
        'secret' : ""
    }
}
auth = tweepy.OAuthHandler(
    twitter_conf['consumer']['key'],
    twitter_conf['consumer']['secret'])
auth.set_access_token(
    twitter_conf['access']['key'],
    twitter_conf['access']['secret'])
api = tweepy.API(auth)



# _hashtag_list.json    {'hash_tag':'tweet_id', }
# _hashtag_add.txt	    1行ずつ検索ワード記載


# hashtag_add	      ハッシュタグ追加用
# hashtag_json	    json読み込み用
# hashtag			      追加用一時変数
def init_start():
	hashtag_json = {}
	if os.path.exists(working_directory) == False:
		os.makedirs(working_directory)
	if os.path.exists(working_directory + "/_hashtag_list.json") == False:
		f = open(working_directory + "/_hashtag_list.json",'w+')
		f.close()
	if os.path.exists(working_directory + "/_hashtag_add.txt") == False:
		f = open(working_directory + "/_hashtag_add.txt",'w+')
		f.close()
	if os.path.getsize(working_directory + "/_hashtag_add.txt"):
		f = open(working_directory + "/_hashtag_add.txt")
		hashtag_add = f.read().split('\n')
		f.close()
		if os.path.getsize(working_directory + "/_hashtag_list.json"):
			f = open(working_directory + "/_hashtag_list.json",'r')
			hashtag_json = json.load(f)
			f.close()
			for hashtag in hashtag_add:
				if not hashtag in hashtag_json:
					hashtag_json[hashtag] = ""
		else:
			for hashtag in hashtag_add:
				hashtag_json[hashtag] = ""
		f = open(working_directory + "/_hashtag_list.json",'w')
		json.dump(hashtag_json,f)
		f.close()
		f = open(working_directory + "/_hashtag_add.txt",'w')
		f.close()


# hashtag_json
# hash_tag
# tweet_id
# twi
def tweet_search():
	if not os.path.getsize(working_directory + "/_hashtag_list.json"):
		return
	hashtag_json = {}
	retry_count = 0
	f = open(working_directory + "/_hashtag_list.json",'r')
	hashtag_json = json.load(f)
	f.close()
	for hash_tag,tweet_id in hashtag_json.items():
		if tweet_id:
			search_query = 'since_search'
		else:
			search_query = 'max_search'
			tweet_id = api.search(q=hash_tag)
			tweet_id = tweet_id[0].id
		for l in range(50):
			try:
				if search_query == 'since_search':
					for twi in api.search(q=hash_tag, count=100, since_id=tweet_id):
						media_get(twi)
						tweet_id = twi.id
				else:
					for twi in api.search(q=hash_tag, count=100, max_id=tweet_id):
						media_get(twi)
						tweet_id = twi.id
			except tweepy.RateLimitError as err:
				retry_count = retry_count +1
				if retry_count < 3:
					time.sleep(60 * 5)
					continue
				else:
					retry_count = 0
			except:
				retry_count = retry_count +1
				if retry_count < 3:
					time.sleep(10)
					continue
				else:
					retry_count = 0
			retry_count = 0
		hashtag_json[hash_tag] = tweet_id
	f = open(working_directory + "/_hashtag_list.json",'w')
	json.dump(hashtag_json,f)
	f.close()


# mediaget_fault_count    :media_get()用3回まで再試行する用
# twi_def		      :media_get()用tweet_id_get()から受け取ったツイート詳細
# getmedia_type		:動画あり
def media_get(twi_def):
	# 画像取得
	mediaget_fault_count = 0
	# リツイート判断
	if hasattr(twi_def, 'retweeted_status') is False:
		# メディア判断
		if hasattr(twi_def, "extended_entities"):
			if 'media' in twi_def.extended_entities:
				for media in twi_def.extended_entities["media"]:
					if media["type"] == 'photo':
						dl_filename = media["media_url"]
						dl_media = dl_filename + ":orig"
					if media["type"] == 'animated_gif' and getmedia_type is "video":
						dl_media = media["video_info"]["variants"][0]["url"]
						dl_filename = dl_media
					if media["type"] == 'video' and getmedia_type is "video":
						dl_media = media["video_info"]["variants"][0]["url"]
						if '.m3u8' in dl_media:
							dl_media = media["video_info"]["variants"][1]["url"]
						if '?tag=' in dl_media:
							dl_media = dl_media[:-6]
						dl_filename = dl_media
					if os.path.exists(working_directory + "/" + os.path.basename(dl_filename)) == False:
						try:
							with open(working_directory + "/" + os.path.basename(dl_filename), 'wb') as f:
								dl_file = urllib.request.urlopen(dl_media).read()
								f.write(dl_file)
						except tweepy.RateLimitError as err:
							mediaget_fault_count = mediaget_fault_count +1
							if mediaget_fault_count < 3:
								time.sleep(60 * 5)
								continue
							else:
								mediaget_fault_count = 0
						except Exception as err:
							mediaget_fault_count = mediaget_fault_count +1
							if mediaget_fault_count < 3:
								time.sleep(60)
								continue
							else:
								mediaget_fault_count = 0
					mediaget_fault_count = 0


#
# main
#

file_path = os.getcwd()

working_directory = file_path + "/foo"
getmedia_type = "photo"
init_start()
tweet_search()
working_directory = file_path + "/bar"
getmedia_type = "video"
init_start()
tweet_search()

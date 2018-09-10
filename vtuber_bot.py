'''

---------------
Description
---------------
g_file_path/
　├ vtubermedia_downloader.py
　├ user_list.json
　├ user1/
　│　└ <dl media>
　├ user2/

1. ユーザごとにハッシュタグを保持。とりあえずjsonで管理
	user_list.json
	vtuber{ user1:{dummy:date, tag1:date, tag2:date}, 
		user2:{dummy:date, tag1:date, tag2:date}}
2. プロフィールを監視
	アイコン、ヘッダ、プロフ
3. ハッシュタグで検索。最終検索時刻保持、画像有
	search_hashtags()
	画像有の場合ファボリツ＆保存
	create_favorite(user_id)
4. ユーザのTLを検索。最終検索時刻保持
	search_user_tl()
	短縮URLの展開。配信とアーカイブのURL採集とリツ
	時間収集。テキスト形成しツイ＆トップに
	ハッシュタグ収集

とりあえずダブり画像は考えないものとする

---------------
Flow
---------------
init jsonチェック
user or hash追加チェック
ユーザプロフチェック
TLチェック
ハッシュタグチェック

'''

# _*_ coding: utf-8 _*_

import tweepy
import sys
import urllib.request
import os
import datetime
import time
import json



def tweepy_api():
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
	tweepy_auth = tweepy.API(auth)
	return(tweepy_auth)

def init_script():
	print('please run "python3 vtubermedia_downloader.py user_add user1 user2..."')
	sys.exit()

def user_add(users):
	user_list_useradd = g_user_list_json
	del users[0:2]
	for i in users:
		if hasattr(g_user_list_json, i) is False:
			user_dict = {k:"" for k in user_description_check(i)}
			user_dict.update({"dummy",""})
			user_list_useradd[i] = user_dict
		if os.path.exists(g_file_path + "/" + i) == False:
			os.makedirs(g_file_path + "/" + i)
	return(user_list_useradd)

def hashtag_add(tags):
	user_list_tagadd = g_user_list_json
	key = tags[2]
	del tags[0:3]
	for i in tags:
		if hasattr(g_user_list_json, i) is False:
			user_list_tagadd[key].update({i, ""})
	return(user_list_tagadd)

def user_description_check(check_userid):
	description = g_api.get_user(check_userid).description
	description = re.sub(r'#', " #", description)
	pattern = re.compile(r'[\s\[\]\(\)\<\>\（\）\＜\＞\"\']')
	description_split = re.split(pattern, description)
	description_hashtags = [x for x in description_split if '#' in x]
	return(description_hashtags)

def search_hashtags(s_hashtags):
	retry_count = 0
	for hashtag,date in s_hashtags.items():
		if date:
			search_query = 'since_search'
		else:
			search_query = 'until_search'
			date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
		for l in range(50):
			try:
				if search_query == 'since_search':
					for twi in g_api.search(q=hashtag, count=100, since=date):
						date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
						media_get(twi)
				else:
					for twi in g_api.search(q=hashtag, count=100, until=date):
						date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
						media_get(twi)
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
		# リターンさせる

def search_user_tl(s_user,s_date):
	if s_date:
		search_query = 'since_search'
	else:
		search_query = 'until_search'
		s_date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
	for l in range(50):
		try:
			if search_query == 'until_search':
				for twi in g_api.user_timeline(s_user, count=100, until=date):
					date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
					media_get(twi)
			else:
				for twi in g_api.user_timeline(s_user, count=100, since=date):
					date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
					media_get(twi)
		except tweepy.RateLimitError as err:
			time.sleep(60 * 15)
			continue
		except tweepy.TweepError as err:
			tweetidget_fault_count = tweetidget_fault_count +1
			if tweetidget_fault_count < 3:
				time.sleep(60 * 5)
				continue
			else:
				tweetidget_fault_count = 0
		tweetidget_fault_count = 0
	###
	for twi in g_api.search(q="#testing", count=10, until=s_date, tweet_mode = 'extended'):
		print(twi.full_text)
	tweet_hashtags = []
	for i in g_api.get_status(1010433527404347393).entities['hashtags']:
		#tweet_hashtags.append("#" + i['text'])

def media_get(twi_def):
	mediaget_fault_count = 0
	if hasattr(twi_def, "extended_entities"):
		if 'media' in twi_def.extended_entities:
			for media in twi_def.extended_entities["media"]:
				if media["type"] == 'photo':
					dl_filename = media["media_url"]
					dl_media = dl_filename + ":orig"
				if media["type"] == 'animated_gif':
					dl_media = media["video_info"]["variants"][0]["url"]
					dl_filename = dl_media
				if media["type"] == 'video':
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



# main

g_file_path = os.getcwd()
if os.path.exists(g_file_path + "/user_list.json") == False:
	os.makedirs(g_file_path + "/user_list.json")
	init_script()
else:
	json_file = open(g_file_path + "/user_list.json",'r')
	g_user_list_json = json.load(json_file)
	json_file.close()
	if len(g_user_list_json) == 0:
		init_script()

g_args = sys.argv
if len(g_args) != 1:
	if g_args[1] is 'user_add':
		g_user_list_new = user_add(g_args)
	elif os.path.exists(g_file_path + "/user_list.json") == False:
		init_script()
	elif g_args[1] is 'hashtag_add':
		g_user_list_new = hashtag_add(g_args)
	else:
		print("please chech parameter: " + g_args)
		sys.exit()
elif os.path.exists(g_file_path + "/user_list.json") == False:
	init_script()

#json_file = open(g_file_path + "/user_list.json",'w')
#json.dump(g_user_list_new,json_file)
#json_file.close()

g_api = tweepy_api()
for g_user,g_tags in g_user_list_new.items():
	g_working_directory = g_file_path + "/" + user
	for i in user_description_check(g_user):
		if i not in g_tags:
			g_tags.update({i, ""})
	search_user_tl(g_user,g_tags["dummy"])
	search_hashtags(g_tags)
	g_user_list_new[g_user] = g_tags

g_json_file = open(g_file_path + "/user_list.json",'w')
json.dump(g_user_list_new,g_json_file)
g_json_file.close()

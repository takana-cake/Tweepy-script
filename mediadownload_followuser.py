# _*_ coding: utf-8 _*_

import tweepy
import sys
import urllib.request
import os
import datetime
import time
import json


# 認証
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



#my_id = [ '' , '' ]
my_id = ""
my_friends_ids = []		#フォローしているIDとスクリーン名
my_friends_list = {}		#
my_friends_list_json = {}	#


def limit_handled(h):
	while True:
		try:
			yield h.next()
		except tweepy.RateLimitError as err:
			print(str(datetime.datetime.now()) + ": RateLimitError_1: " + str(err))
			with open(working_directory + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": RateLimitError_1: " + str(err) + "\n")
			time.sleep(60 * 15)
		except tweepy.TweepError as err:
			print(str(datetime.datetime.now()) + ": TweepError_1: " + str(err))
			with open(working_directory + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": TweepError_1: " + str(err) + "\n")
			time.sleep(60 * 15)


### 新規フォロー初期化用
# json_file		:_my_friends_listをオープン
# my_friends_list_json	:_my_friends_listを格納
# new_follow_screen	:スクリーン名格納
# new_follow_detail	:nameと最終取得日(ブランク)格納
def new_follow_ids_json():
	json_file = open(working_directory + "/_my_friends_list.json",'r')
	my_friends_list_json = json.load(json_file)
	json_file.close()
	for new_follow_screen,new_follow_detail in my_friends_list_json.items():
		if os.path.exists(working_directory + "/" + new_follow_screen) == False:
			os.makedirs(working_directory + "/" + new_follow_screen)
			my_friends_list_json[new_follow_screen] = new_follow_detail
	json_file = open(working_directory + "/_my_friends_list.json",'w')
	json.dump(my_friends_list_json,json_file)
	json_file.close()



# idget_fault_count	:APIエラー時の確認用フラグ
# json_file		:_my_friends_listをオープン
# my_friends_list_json	:_my_friends_listを格納
# follow_id_get		:ID格納。tweet_id_get()に渡す
# follow_screen_get	:スクリーン名格納
# query			:検索クエリ。tweet_id_get()に渡す
# maxid			:検索開始ツイートID。tweet_id_get()に渡す
# idget_fault_count	:api失敗カウンタ
def first_search_date_set():
	# 取得開始のdateを
	idget_fault_count = 0
	json_file = open(working_directory + "/_my_friends_list.json",'r')
	my_friends_list_json = json.load(json_file)
	json_file.close()
	for follow_screen_get,follow_detail_get in my_friends_list_json.items():
		if follow_detail_get["last_search_date"]:
			search_query = 'since_search'
			date = follow_detail_get["last_search_date"]
		else:
			search_query = 'until_search'
			date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
		for l in range(50):
			try:
				if search_query == 'since_search':
					for twi in api.user_timeline(follow_screen_get, count=100, since=date):
						date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
						media_get(twi)
				else:
					for twi in api.user_timeline(follow_screen_get, count=100, until=date):
						date = datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S_JST")
						media_get(twi)
			except tweepy.RateLimitError as err:
				with open(working_directory + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": " + str(follow_screen_get) + ": RateLimitError_3: " + str(err) + "\n")
				idget_fault_count = idget_fault_count +1
				if idget_fault_count < 3:
					time.sleep(60 * 5)
					continue
				else:
					idget_fault_count = 0
			except Exception as err:
				with open(working_directory + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": " + str(follow_screen_get) + ": Exception_3: " + str(err) + "\n")
				idget_fault_count = idget_fault_count +1
				if idget_fault_count < 3:
					time.sleep(10)
					continue
				else:
					idget_fault_count = 0
			idget_fault_count = 0
		my_friends_list_json[follow_screen_get]["last_search_date"] = date
		#tweet_id_get(query, follow_id_get, maxid)
	json_file = open(working_directory + "/_my_friends_list.json",'w')
	json.dump(my_friends_list_json,json_file)
	json_file.close()


# tweetidget_fault_count	:tweet_id_get()用3回まで再試行する用
# l				:tweet_id_get()用50×count100=5000ツイート
# query_def			:tweet_id_get()用first_tweet_id_set()から受け取った検索クエリ
# follow_id			:tweet_id_get()用first_tweet_id_set()から受け取った_my_friends_listからのフォローID
# maxid_def			:tweet_id_get()用処理中ツイートID。初期値はfirst_tweet_id_set()から受け取った検索開始ID
# twi				:tweet_id_get()用フォローIDのタイムライン
# maxid_def			:tweet_id_get()用first_tweet_id_set()から受け取った検索クエリ
# maxid_def			:tweet_id_get()用first_tweet_id_set()から受け取った検索クエリ
def tweet_id_get(query_def, follow_id, maxid_def):
	# ツイートIDを取得
	tweetidget_fault_count = 0
	for l in range(50):
		#02-1 TLを取得_API
		try:
			if query_def == 'max_search':
				#03-1 新規サーチ
				for twi in api.user_timeline(follow_id, count=100, max_id=maxid_def):
					# media_getへ
					media_get(twi, follow_id)
					maxid_def = twi.id
			elif query_def == 'since_search':
				#03-2 既存サーチ
				for twi in api.user_timeline(follow_id, count=100, since_id=maxid_def):
					# media_getへ
					media_get(twi, follow_id)
					maxid_def = twi.id
				with open(working_directory + "/" + follow_id + "/_maxid.txt", 'w+') as f:
					f.write(str(maxid_def))
		#02-2
		except tweepy.RateLimitError as err:
			with open(working_directory + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": " + str(follow_id) + ": RateLimitError_4: " + str(maxid_def) + ": TC=" + str(tweetidget_fault_count) + ": " + str(err) + "\n")
			time.sleep(60 * 15)
			continue
		#02-3
		except tweepy.TweepError as err:
			print(str(datetime.datetime.now()) + str(follow_id) + ": TweepError_4: " + str(maxid_def) + ": TC=" + str(tweetidget_fault_count) + ": " + str(err))
			with open(working_directory + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": " + str(follow_id) + ": TweepError_4: " + str(maxid_def) + ": TC=" + str(tweetidget_fault_count) + ": " + str(err) + "\n")
			tweetidget_fault_count = tweetidget_fault_count +1
			if tweetidget_fault_count < 3:
				time.sleep(60 * 5)
				continue
			else:
				tweetidget_fault_count = 0
		tweetidget_fault_count = 0


		
# mediaget_fault_count		:media_get()用3回まで再試行する用
# twi_def			:media_get()用tweet_id_get()から受け取ったツイート詳細
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
					if os.path.exists(working_directory + "/" + twi_def["screen_name"] + "/" + os.path.basename(dl_filename)) == False:
						try:
							with open(working_directory + "/" + twi_def["screen_name"] + "/" + os.path.basename(dl_filename), 'wb') as f:
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



### main

# file_path		:プログラムを実行しているパスを取得
# my_id_select		:my_idから作業対象のIDを取得
# working_directory	:作業しているフォルダ
# my_friends_ids	:リスト型でフォローIDを抽出
# my_friends_list	:辞書型にスクリーン名とIDを格納
# follow_counter	:フォロー数カウンター

file_path = os.getcwd()
api = tweepy_api()

#for my_id_select in my_id:
#	working_directory = file_path + "/" + my_id_select

working_directory = file_path
# ユーザディレクトリチェック
if os.path.exists(working_directory) == False:
	os.makedirs(working_directory)
# ログファイル作成
with open(working_directory + "/_log.txt",'w+') as f:
	f.write(str(datetime.datetime.now()) + ": start: " + str(my_id) + "\n")

# my_id_selectのフォローしたIDをmy_friends_idsに取得
# Cursor使うとすべて取ってきてくれるが，配列ではなくなるので配列に入れる
for tmp_id in limit_handled(tweepy.Cursor(api.friends_ids, id=my_id).items()):
	my_friends_ids.append(tmp_id)
# 100IDsずつ詳細をmy_friends_listへ
follow_counter = 0
for i in range(0, len(my_friends_ids), 100):
	try:
		for tmp_user in api.lookup_users(user_ids=my_friends_ids[i:i+100]):
			follow_counter = follow_counter + 1
			my_friends_list[tmp_user.screen_name] = {"name":tmp_user.name, "last_search_date":""}
	except tweepy.RateLimitError as err:
		print(str(datetime.datetime.now()) + ": RateLimitError_2: " + str(err))
		with open(working_directory + "/_log.txt",'a') as f:
			f.write(str(datetime.datetime.now()) + ": RateLimitError_2: " + str(err) + "\n")
		time.sleep(60 * 15)
		continue
	except Exception as err:
		print(str(datetime.datetime.now()) + ": " + str(err))
		with open(working_directory + "/_log.txt",'a') as f:
			f.write(str(datetime.datetime.now()) + ": TweepError_2: " + str(err) + "\n")
		time.sleep(60 * 3)
		continue
print(str(datetime.datetime.now()) + ": " + str(len(my_friends_ids)) + "/" + str(follow_counter))
with open(working_directory + "/_log.txt",'a') as f:
	f.write(str(datetime.datetime.now()) + ": " + str(len(my_friends_ids)) + "/" + str(follow_counter) + "\n")

# _my_friends_list.jsonが無ければ作成
if os.path.exists(working_directory + "/_my_friends_list.json") == False:
	f = open(working_directory + "/_my_friends_list.json",'w+')
	json.dump(my_friends_list,f)
	f.close()

# 新規フォローIDをjsonに保存
new_follow_ids_json()

# ツイートIDの取得
first_search_date_set()

my_friends_list.clear()
my_friends_list_json.clear()
my_friends_ids = []

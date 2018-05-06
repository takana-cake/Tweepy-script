# _*_ coding: utf-8 _*_


import tweepy
import sys
import urllib
import os
import datetime
import time

def limit_handled(h):
	while True:
		try:
			yield h.next()
		except tweepy.RateLimitError, err:
			print str(datetime.datetime.now()) + ": RateLimitError_1: " + str(err)
			#print(str(datetime.datetime.now()) + ": RateLimitError_1: " + str(err))
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": RateLimitError_1: " + str(err) + "\n")
			time.sleep(60 * 15)
		except tweepy.TweepError, err:
			print str(datetime.datetime.now()) + ": TweepError_1: " + str(err)
			#print(str(datetime.datetime.now()) + ": TweepError_1: " + str(err))
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": TweepError_1: " + str(err) + "\n")
			time.sleep(60 * 15)

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


my_id = [ '' , '' ]
# my_id_select = リストmy_idより作業IDを格納する一時変数
# tmp_id = api.friends_idsからmy_friends_idsへ格納するときの一時変数
my_friends_ids = []		#フォローしているIDとスクリーン名
my_friends_list = {}	#
# i = len(my_friends_ids) , maxid格納するときの一時変数
# tmp_user = 何用？
# follow_id = フォローしてるid
# follow_screen = フォローしてるスクリーン名
# err = エラー
# f = ファイル
# l = 16*200の16
# twi = TL
tmp_count = 0
tmp_count2 = 0


for my_id_select in my_id:
	print str(datetime.datetime.now()) + ": " + str(my_id_select)
	#print(str(datetime.datetime.now()) + ": " + str(my_id_select))
	file_path = os.getcwd() + "/" + my_id_select
	if os.path.exists(file_path) == False:
		os.makedirs(file_path)
	# ログファイル作成
	with open(file_path + "/_log.txt",'w+') as f:
		f.write(str(datetime.datetime.now()) + ": start: " + str(my_id_select) + "\n")

	## my_id_selectのフォローしたIDをmy_friends_idsに取得
	# Cursor使うとすべて取ってきてくれるが，配列ではなくなるので配列に入れる
	for tmp_id in limit_handled(tweepy.Cursor(api.friends_ids, id=my_id_select).items()):
		my_friends_ids.append(tmp_id)
	# 100IDsずつ詳細をmy_friends_listへ
	# tmp_countはフォロー数カウンター、tmp_count2はエラー時のiチェック
	tmp_count = 0
	tmp_count2 = 0
	for i in range(0, len(my_friends_ids), 100):
		try:	#forと逆に
			for tmp_user in api.lookup_users(user_ids=my_friends_ids[i:i+100]):
				tmp_count = tmp_count + 1
				my_friends_list[unicode(tmp_user.screen_name)] = unicode(tmp_user.name)
				#unicode処理はpython3では不要
			if tmp_count2 == 1:
				print str(datetime.datetime.now()) + ": retry: i=" + str(i) + ": done"
				#print(str(datetime.datetime.now()) + ": retry: i=" + str(i) + ": done")
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": retry: i=" + str(i) + ": done\n")
		except tweepy.RateLimitError, err:
		#except tweepy.RateLimitError as err:
			print str(datetime.datetime.now()) + ": RateLimitError_2: i=" + str(i) + ": " + str(err)
			#print(str(datetime.datetime.now()) + ": RateLimitError_2: i=" + str(i) + ": " + str(err))
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": RateLimitError_2: i=" + str(i) + ": " + str(err) + "\n")
			tmp_count2 = 1
			time.sleep(60 * 15)
			continue
		except tweepy.TweepError, err:
		#except tweepy.TweepError as err:
			print str(datetime.datetime.now()) + ": TweepError_2: i=" + str(i) + ": " + str(err)
			#print(str(datetime.datetime.now()) + ": TweepError_2: i=" + str(i) + ": " + str(err))
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": TweepError_2: i=" + str(i) + ": " + str(err) + "\n")
			tmp_count2 = 1
			time.sleep(60 * 15)
			continue
	print str(datetime.datetime.now()) + ": " + str(len(my_friends_ids)) +"/" + str(tmp_count)
	#print(str(datetime.datetime.now()) + ": " + str(len(my_friends_ids)) +"/" + str(tmp_count))
	with open(file_path + "/_log.txt",'a') as f:
		f.write(str(datetime.datetime.now()) + ": " + str(len(my_friends_ids)) + "/" + str(tmp_count) + "\n")

	## 取得開始のツイートIDをmaxidへいれる
	# tmp_countはAPIエラー時のMAXID確認用フラグ
	# ./my_id_select/follow_id/_maxid.txtに前回実行時のMAXIDを記録している
	# ここ以下のAPIは鍵アカだと取得できないので対ループ用にtmp_countを使用
	tmp_count = 0
	for follow_id,follow_screen in my_friends_list.items():
		print str(datetime.datetime.now()) + ": " + follow_id
		#print(str(datetime.datetime.now()) + ": " + follow_id)
		#follow_idディレクトリが無ければ作成
		if os.path.exists(file_path + "/" + follow_id) == False:
			os.makedirs(file_path + "/" + follow_id)
		#_maxid.txtファイルが無ければ作成
		if os.path.exists(file_path + "/" + follow_id + "/_maxid.txt") == False:
			f = open(file_path + "/" + follow_id + "/_maxid.txt" , 'w+')
			f.close()
		#_maxid.txtファイルが空ならmaxidを取得
		if os.path.getsize(file_path + "/" + follow_id + "/_maxid.txt") == 0:
			query = 'max_search'
			try:
				maxid = api.user_timeline(follow_id).max_id
			#API対策
			except tweepy.RateLimitError, err:
			#except tweepy.RateLimitError as err:
				print str(datetime.datetime.now()) + ": " + str(follow_id) + ": RateLimitError_3: " + str(err)
				#print(str(datetime.datetime.now()) + ": " + str(follow_id) + ": RateLimitError_3: " + str(err))
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": " + str(follow_id) + ": RateLimitError_3: " + str(err) + "\n")
				time.sleep(60 * 15)
				continue
			#その他、鍵アカ対策
			except tweepy.TweepError, err:
			#except tweepy.TweepError as err:
				print str(datetime.datetime.now()) + ": " + str(follow_id) + ": TweepError_3: " + str(err)
				#print(str(datetime.datetime.now()) + ": " + str(follow_id) + ": TweepError_3: " + str(err))
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": " + str(follow_id) + ": TweepError_3: " + str(err) + "\n")
				tmp_count = tmp_count +1
				if tmp_count < 3:
					time.sleep(60 * 5)
					continue
				else:
					tmp_count = 0
			tmp_count = 0
			f = open(file_path + "/" + follow_id + "/_maxid.txt" , 'w')
			f.write(str(maxid))
			f.close()
		#前回の_maxid.txtをmaxidへ入れて検索
		else:
			f = open(file_path + "/" + follow_id + "/_maxid.txt" , 'r')
			for i in f: maxid = i
			f.close()
			query = 'since_search'

		## 画像取得
		# tmp_countは例外検知用、tmp_count2は3回まで再試行する用
		tmp_count = 0
		tmp_count2 = 0
		#01
		for l in range(16):
			#02-1
			#TLを取得_API
			try:	#forと逆にする
				#02のチェック後半
				if tmp_count != 0:
					print str(datetime.datetime.now()) + str(follow_id) + ": 02-1: " + str(maxid) + " TC=" + str(tmp_count)
					#print(str(datetime.datetime.now()) + str(follow_id) + ": 02-1: " + str(maxid) + " TC=" + str(tmp_count))
					tmp_count = 0
					with open(file_path + "/_log.txt",'a') as f:
						f.write(str(datetime.datetime.now()) + str(follow_id) + ": 02-1: " + str(maxid) + " TC=" + str(tmp_count) + "\n")
				if query == 'max_search':
					#03-1
					for twi in api.user_timeline(follow_id, count=200, max_id=maxid):
						# 画像保存
						if hasattr(twi, "extended_entities"):
							if twi.extended_entities.has_key("media"):
							#if 'media' in twi.extended_entities:
								for index,media in enumerate(twi.extended_entities["media"]):
									img_url = media["media_url"]
									url_orig = img_url + ":orig"
									try:
										with open(file_path + "/" + follow_id + "/" + os.path.basename(img_url), 'wb') as f:
											img = urllib.urlopen(url_orig).read()
											f.write(img)
									except Exception as err:
									#except Exception as err:
										print str(datetime.datetime.now()) + str(follow_id) + ": 03-1: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err)
										#print(str(datetime.datetime.now()) + str(follow_id) + ": 03-1: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err))
										with open(file_path + "/_log.txt",'a') as f:
											f.write(str(datetime.datetime.now()) + str(follow_id) + ": 03-1: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
										tmp_count2 = tmp_count2 +1
										if tmp_count2 < 3:
											time.sleep(60)
											continue
										else:
											tmp_count2 = 0
									except:
										# 不具合発生中
										print str(datetime.datetime.now()) + str(follow_id) + ": !!!fail!!!"
										#print(str(datetime.datetime.now()) + str(follow_id) + ": !!!fail!!!")
										with open(file_path + "/_log.txt",'a') as f:
											f.write(str(datetime.datetime.now()) + str(follow_id) + ": 03-1: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
										tmp_count2 = tmp_count2 +1
										if tmp_count2 < 3:
											time.sleep(60)
											continue
										else:
											tmp_count2 = 0
									tmp_count2 = 0
						maxid = twi.id
					#03-1 終了
				elif query == 'since_search':
					#03-2
					for twi in api.user_timeline(follow_id, count=200, since_id=maxid):
						# 画像保存
						if hasattr(twi, "extended_entities"):
							if twi.extended_entities.has_key("media"):
							#if 'media' in twi.extended_entities:
								for index,media in enumerate(twi.extended_entities["media"]):
									img_url = media["media_url"]
									url_orig = img_url + ":orig"
									try:
										with open(file_path + "/" + follow_id + "/" + os.path.basename(img_url), 'wb') as f:
											img = urllib.urlopen(url_orig).read()
											f.write(img)
									except Exception as err:
										print str(datetime.datetime.now()) + str(follow_id) + ": 03-2: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err)
										#print(str(datetime.datetime.now()) + str(follow_id) + ": 03-2: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err))
										with open(file_path + "/_log.txt",'a') as f:
											f.write(str(datetime.datetime.now()) + str(follow_id) + ": 03-2: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
										tmp_count2 = tmp_count2 +1
										if tmp_count2 < 3:
											time.sleep(60)
											continue
										else:
											tmp_count2 = 0
									except:
										# 不具合発生中
										print str(datetime.datetime.now()) + str(follow_id) + ": !!!fail!!!"
										#print(str(datetime.datetime.now()) + str(follow_id) + ": !!!fail!!!")
										with open(file_path + "/_log.txt",'a') as f:
											f.write(str(datetime.datetime.now()) + str(follow_id) + ": 03-2: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
										tmp_count2 = tmp_count2 +1
										if tmp_count2 < 3:
											time.sleep(60)
											continue
										else:
											tmp_count2 = 0
									tmp_count2 = 0
						maxid = twi.id
					#03-2 終了
					with open(file_path + "/" + follow_id + "/_maxid.txt", 'w+') as f:
						f.write(str(maxid))
			#02-2
			except tweepy.RateLimitError, err:
			#except tweepy.RateLimitError as err:
				print str(datetime.datetime.now()) + str(follow_id) + ": RateLimitError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err)
				#print(str(datetime.datetime.now()) + str(follow_id) + ": RateLimitError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err))
				tmp_count = 1
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + str(follow_id) + ": RateLimitError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
				time.sleep(60 * 15)
				continue
			#02-3
			except tweepy.TweepError, err:
			#except tweepy.TweepError as err:
				print str(datetime.datetime.now()) + str(follow_id) + ": TweepError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err)
				#print(str(datetime.datetime.now()) + str(follow_id) + ": TweepError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err))
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + str(follow_id) + ": TweepError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
				tmp_count = 1
				tmp_count2 = tmp_count2 +1
				if tmp_count2 < 3:
					time.sleep(60 * 5)
					continue
				else:
					tmp_count2 = 0
			tmp_count2 = 0
		#01 終了
	my_friends_list.clear()
	my_friends_ids = []

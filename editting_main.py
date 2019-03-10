#!/usr/bin python3
# _*_ coding: utf-8 _*_

from time import sleep
import datetime
import filecmp
import glob
import json
import os
import shutil
import subprocess
import sys
import tweepy
import urllib.request
import argparse
import re
import csv



### 認証 ###
def tweepy_api():
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
	auth = tweepy.OAuthHandler(
		twitter_conf['consumer']['key'],
		twitter_conf['consumer']['secret'])
	auth.set_access_token(
		twitter_conf['access']['key'],
		twitter_conf['access']['secret'])
	tweepy_auth = tweepy.API(auth)
	return tweepy_auth



### user object ###

def _twitter_userobject_get(SCREEN_NAME):
	errcount = 0
	USER_OBJECT = ""
	def _get_description(SCREEN_NAME):
		nonlocal errcount
		nonlocal USER_OBJECT
		try:
			USER_OBJECT = twiapi.get_user(SCREEN_NAME)
		except tweepy.RateLimitError as err_description:
			sleep(60 * 15)
			_get_description(SCREEN_NAME)
		except Exception as err:
			if errcount < 3:
				errcount = errcount + 1
				err_subject = SCREEN_NAME + " : _twitter_userobject_get"
				_log(err_subject, err)
				sleep(60)
				_get_description(SCREEN_NAME)
			USER_OBJECT = "err"
	_get_description(SCREEN_NAME)
	return USER_OBJECT



### URL get ###

def _twiprofurl_get(SCREEN_NAME, USER_OBJECT):
	URLS = []
	USER_URL = USER_OBJECT.entities
	USER_DESCRIPTION = USER_OBJECT.description
	if "url" in USER_URL:
		URLS.append(USER_URL["url"]["urls"][0]["expanded_url"])
	URLS.extend(_split_urls(USER_DESCRIPTION))
	return URLS

def _split_urls(SPLIT_TXT):
	DESCURLS = []
	SHORTURLS = []
	URL_PATTERN = re.compile("http[!-~]+")
	SHORTURLS = re.findall(URL_PATTERN, SPLIT_TXT)
	for j in SHORTURLS:
		if j[-1] in ["]", ")"]:
			j = j[:-1]
		try:
			DESCURL = (urllib.request.urlopen(j,timeout=3).geturl())
			DESCURLS.append(DESCURL)
		except Exception as err:
			err_subject = j + " : "
			_log(err_subject, err)
			DESCURLS.append(j)
			sleep(30)
	return DESCURLS



### hashtag check ###

def _TL_hashtag_check(TWEET_OBJECT):
	hashtag_list = []
	if hasattr(TWEET_OBJECT, "retweeted_status"):
		if "hashtags" in TWEET_OBJECT.retweeted_status.entities:
			for x in TWEET_OBJECT.retweeted_status.entities["hashtags"]:
				hashtag_list.append(x["text"])
	elif hasattr(TWEET_OBJECT, "quoted_status"):
		if "hashtags" in TWEET_OBJECT.quoted_status.entities:
			for y in TWEET_OBJECT.quoted_status.entities["hashtags"]:
				hashtag_list.append(y["text"])
	else:
		if "hashtags" in TWEET_OBJECT.entities:
			for z in TWEET_OBJECT.entities["hashtags"]:
				hashtag_list.append(z["text"])
	return hashtag_list

def _twitter_profile_hashtag(SCREEN_NAME, USER_OBJECT):
	hashtags = []
	hashtag_tmp = re.sub(r'#', " #", USER_OBJECT.description)
	emoji_pattern = re.compile("["
		u"\U0001F600-\U0001F64F"
		u"\U0001F300-\U0001F5FF"
		u"\U0001F680-\U0001F6FF"
		u"\U0001F1E0-\U0001F1FF"
		u"\U0001F201-\U0001F9E6"
		"]+", flags=re.UNICODE)
	hashtag_tmp = re.sub(emoji_pattern, " ", hashtag_tmp)
	pattern = re.compile(r'[\s\[\]\(\)\<\>\（\）\＜\＞\"\']')
	hashtag_split = re.split(pattern, hashtag_tmp)
	hashtags = [x for x in hashtag_split if '#' in x]
	for x in range(len(hashtags)):
		hashtags[x] = re.sub(r'#', "", hashtags[x])
	return hashtags



### TL chech ###

def _TL_search(SCREEN_NAME, TWEET_ID, FILEPATH, retweet_enable, gif_enable, video_enable):
	HASHTAG_LIST = []
	def _get_tweetid(SCREEN_NAME):
		nonlocal TL_search_fault_count
		try:
			get_id = twiapi.user_timeline(SCREEN_NAME).max_id
			return get_id
		except tweepy.RateLimitError as err_description:
			sleep(60 * 15)
			_get_tweetid(SCREEN_NAME)
		except Exception as err_description:
			if TL_search_fault_count < 3:
				TL_search_fault_count = TL_search_fault_count + 1
				err_subject = SCREEN_NAME + " : Exception_TL_search"
				_log(err_subject, err_description)
				sleep(60)
				_get_tweetid(SCREEN_NAME)
	def _TL_tweet_get(SCREEN_NAME, TWEET_ID, FILEPATH, retweet_enable, gif_enable, video_enable, search_flag):
		nonlocal TL_tweet_get_fault_count
		nonlocal HASHTAG_LIST
		try:
			if search_flag == 'max_search':
				for tl_object in twiapi.user_timeline(SCREEN_NAME, count=100, max_id=TWEET_ID):
					_download_check(FILEPATH, tl_object, retweet_enable, gif_enable, video_enable)
					HASHTAG_LIST.extend(_TL_hashtag_check(tl_object))
					TWEET_ID = tl_object.id
					TL_tweet_get_fault_count = 0
			elif search_flag == 'since_search':
				for tl_object in twiapi.user_timeline(SCREEN_NAME, count=100, since_id=TWEET_ID):
					_download_check(FILEPATH, tl_object, retweet_enable, gif_enable, video_enable)
					HASHTAG_LIST.extend(_TL_hashtag_check(tl_object))
					TWEET_ID = tl_object.id
					TL_tweet_get_fault_count = 0
		except tweepy.RateLimitError as err_description:
			sleep(60 * 15)
			_TL_tweet_get(SCREEN_NAME, TWEET_ID, FILEPATH, retweet_enable, gif_enable, video_enable, search_flag)
		except Exception as err_description:
			if TL_tweet_get_fault_count < 3:
				err_subject = str(SCREEN_NAME) + " : Exception_tweet_get : " + str(TWEET_ID)
				_log(err_subject, err_description)
				TL_tweet_get_fault_count = TL_tweet_get_fault_count +1
				sleep(60 * 5)
				_TL_tweet_get(SCREEN_NAME, TWEET_ID, FILEPATH, retweet_enable, gif_enable, video_enable, search_flag)
	if TWEET_ID == "":
		TL_search_fault_count = 0
		TWEET_ID = _get_tweetid(SCREEN_NAME)
		search_flag = 'max_search'
	else:
		search_flag = 'since_search'
	if not TWEET_ID == None:
		TL_tweet_get_fault_count = 0
		while_count = 0
		while while_count < 100:
			while_count += 1
			_TL_tweet_get(SCREEN_NAME, TWEET_ID, FILEPATH, retweet_enable, gif_enable, video_enable, search_flag)
	return TWEET_ID,HASHTAG_LIST



### profile ###

def _profile_get_img(url, file_name):
	profile_get_img_fault_count = 0
	def _get_img(url, file_name):
		nonlocal profile_get_img_fault_count
		try:
			urllib.request.urlretrieve(url, file_name)
		except Exception as err_description:
			if profile_get_img_fault_count < 3:
				profile_get_img_fault_count = profile_get_img_fault_count + 1
				err_subject = url + " : _profile_get_img"
				_log(err_subject, err_description)
				sleep(60)
				_get_img(url, file_name)
	_get_img(url, file_name)

def _profile_get_capture_icon(screen_name, file_path_cap):
	url_user = "https://twitter.com/" + screen_name
	capture_icon_file = file_path_cap + screen_name + "_capture_icon_" + DATE + ".jpg"
	cmd_capture_icon = "wkhtmltoimage --javascript-delay 15000 --crop-h 255 --crop-w 255 --crop-x 50 --crop-y 185 " + url_user + " " + capture_icon_file
	subprocess.call(cmd_capture_icon.split(), shell=False)

def _profile_get_capture_banner(screen_name, file_path_cap):
	url_user = "https://twitter.com/" + screen_name
	capture_banner_file = file_path_cap + screen_name + "_capture_banner_" + DATE + ".jpg"
	cmd_capture_banner = "wkhtmltoimage --javascript-delay 15000 --crop-h 380 --crop-w 1023 --crop-x 1 --crop-y 40 " + url_user + " " + capture_banner_file
	subprocess.call(cmd_capture_banner.split(), shell=False)

def _profile(SCREEN_NAME, USER_OBJECT, FILEPATH):
	file_path_cap = FILEPATH + "profile/"
	if os.path.exists(file_path_cap) == False:
		os.makedirs(file_path_cap)
	prof_flag = "0"

	if hasattr(USER_OBJECT, "profile_image_url_https"):
		profile_icon = USER_OBJECT.profile_image_url_https
		if '_normal' in profile_icon:
			profile_icon = profile_icon.replace("_normal", "")
		elif '_mini' in profile_icon:
			profile_icon = profile_icon.replace("_mini", "")
		elif '_bigger' in profile_icon:
			profile_icon = profile_icon.replace("_bigger", "")
		comparison_icon_file = file_path_cap + SCREEN_NAME + "_comparison_icon_" + DATE + "." + profile_icon.rsplit(".", 1)[1]
		_profile_get_img(profile_icon, comparison_icon_file)
		if not glob.glob(file_path_cap + SCREEN_NAME + '_base_icon*'):
			base_icon_file = file_path_cap + SCREEN_NAME + "_base_icon." + profile_icon.rsplit(".", 1)[1]
			shutil.copyfile(comparison_icon_file, base_icon_file)
			shutil.copyfile(comparison_icon_file, file_path_cap + SCREEN_NAME + "_icon_" + DATE + "." + profile_icon.rsplit(".", 1)[1])
			_profile_get_capture_icon(SCREEN_NAME, file_path_cap)
		base_icon_file = glob.glob(file_path_cap + SCREEN_NAME + '_base_icon*')[0]
		if filecmp.cmp(base_icon_file, comparison_icon_file) == False :
			shutil.copyfile(comparison_icon_file, file_path_cap + SCREEN_NAME + "_icon_" + DATE + "." + profile_icon.rsplit(".", 1)[1])
			shutil.copyfile(comparison_icon_file, base_icon_file)
			_profile_get_capture_icon(SCREEN_NAME, file_path_cap)
			prof_flag = "1"
		os.remove(comparison_icon_file)
	if hasattr(USER_OBJECT, "profile_banner_url"):
		profile_banner = USER_OBJECT.profile_banner_url
		comparison_banner_file = file_path_cap + SCREEN_NAME + "_comparison_banner_" + DATE + ".jpg"
		_profile_get_img(profile_banner, comparison_banner_file)
		if not glob.glob(file_path_cap + SCREEN_NAME + '_base_banner*'):
			base_banner_file = file_path_cap + SCREEN_NAME + "_base_banner.jpg"
			shutil.copyfile(comparison_banner_file, base_banner_file)
			shutil.copyfile(comparison_banner_file, file_path_cap + SCREEN_NAME + "_banner_" + DATE + ".jpg")
			_profile_get_capture_banner(SCREEN_NAME, file_path_cap)
		base_banner_file = glob.glob(file_path_cap + SCREEN_NAME + '_base_banner*')[0]
		if filecmp.cmp(base_banner_file, comparison_banner_file) == False:
			shutil.copyfile(comparison_banner_file, file_path_cap + SCREEN_NAME + "_banner_" + DATE + ".jpg")
			shutil.copyfile(comparison_banner_file, base_banner_file)
			_profile_get_capture_banner(SCREEN_NAME, file_path_cap)
			prof_flag = "1"
		os.remove(comparison_banner_file)

	if prof_flag != "0":
		twi_str = '変わったかも_{0:%H:%M}'.format(datetime.datetime.now())
		#twiapi.update_status(twi_str)



### search ###

def _search(FILEPATH, QUERY, GET_DATE, TWEET_ID, gif_enable, video_enable):
	search_fault_count = 0
	tmp_id = ""

	def _id_search(QUERY, TWEET_ID):
		nonlocal search_fault_count
		try:
			if TWEET_ID:
				search_result = twiapi.search(q=QUERY, since_id=TWEET_ID)
			if search_result == "":
				search_result = twiapi.search(q=QUERY, count=1)
		except tweepy.RateLimitError as err_description:
			sleep(60 * 15)
			_id_search(QUERY, TWEET_ID)
		except Exception as err_description:
			if search_fault_count < 3:
				search_fault_count = search_fault_count +1
				err_subject = str(QUERY) + " : Exception_id_search"
				_log(err_subject, err_description)
				sleep(10)
				_id_search(QUERY, TWEET_ID)
		return search_result

	def _search_start(QUERY, search_flag, FILEPATH, gif_enable, video_enable):
		nonlocal search_fault_count
		nonlocal tmp_id
		try:
			if search_flag == 'since_search':
				for search_object in twiapi.search(q=search_query, count=100, since_id=tmp_id):
					if search_object:
						_download_check(FILEPATH, search_object, False, gif_enable, video_enable)
						tmp_id = search_object.id
						search_fault_count = 0
			else:
				for search_object in twiapi.search(q=search_query, count=100, max_id=tmp_id):
					if search_object:
						_download_check(FILEPATH, search_object, False, gif_enable, video_enable)
						tmp_id = search_object.id
						search_fault_count = 0
		except tweepy.RateLimitError as err_description:
			sleep(60 * 15)
			_search_start(QUERY, search_flag, FILEPATH, gif_enable, video_enable)
		except Exception as err_description:
			if search_fault_count < 3:
				search_fault_count = search_fault_count +1
				err_subject = str(QUERY) + " : Exception_search_start"
				_log(err_subject, err_description)
				sleep(10)
				_search_start(QUERY, search_flag, FILEPATH, gif_enable, video_enable)

	while_count = 0
	search_date_tmp = _id_search(QUERY, TWEET_ID)
	if search_date_tmp == "":
		err_description = ""
		err_subject = str(QUERY) + " : search result None"
		_log(err_subject, err_description)
		return ""
	if TWEET_ID:
		search_flag = 'since_search'
		tmp_id = TWEET_ID
	else:
		search_flag = 'max_search'
		tmp_id = search_date_tmp[0].id
	while while_count < 50:
		search_fault_count = 0
		while_count += 1
		_search_start(QUERY, search_flag, FILEPATH, gif_enable, video_enable)
	return tmp_id



### download ###

def _download_media(DL_URL, FILEPATH, FILENAME):
	errcount = 0
	def _download_file(DL_URL, FILEPATH, FILENAME):
		nonlocal errcount
		try:
			with open(FILEPATH + FILENAME, 'wb') as f:
				dl_file = urllib.request.urlopen(DL_URL).read()
				f.write(dl_file)
		except Exception as err_description:
			if errcount < 3:
				errcount = errcount +1
				err_subject = "Exception_download : " + DL_URL
				_log(err_subject, err_description)
				sleep(60)
				_download_file(DL_URL, FILEPATH, FILENAME)
			else:
				errcount = 0
		if FILENAME[-3:] == 'gif':
			gifenc1 = "ffmpeg -i " + FILEPATH + FILENAME + " -vf fps=20,palettegen=stats_mode=diff -y " + FILEPATH + "palette.png"
			gifenc2 = "ffmpeg -i " + FILEPATH + FILENAME + " -i palette.png -lavfi fps=20,paletteuse -y " + FILEPATH + os.path.splitext(FILENAME)[0] + ".gif"
			subprocess.call(gifenc1.split(), shell=False)
			subprocess.call(gifenc2.split(), shell=False)
	_download_file(DL_URL, FILEPATH, FILENAME)


def _download_check(FILEPATH, dl_object, retweet_enable, gif_enable, video_enable):
	# リツイート判断
	if hasattr(dl_object, 'retweeted_status') == True and retweet_enable == False:
		pass
	else:
		# メディア判断
		if hasattr(dl_object, "extended_entities"):
			if 'media' in dl_object.extended_entities:
				for media in dl_object.extended_entities["media"]:
					if media["type"] == 'photo':
						DL_URL = media["media_url"]
						FILENAME = os.path.basename(DL_URL)
						FILE_CHECK = FILENAME
						DL_URL = DL_URL + ":orig"
					if media["type"] == 'animated_gif' and gif_enable == True:
						DL_URL = media["video_info"]["variants"][0]["url"]
						FILENAME = os.path.basename(DL_URL)
						FILE_CHECK = re.split("[./]", DL_URL)[-2] + ".gif"
					if media["type"] == 'video' and video_enable == True:
						DL_URL = media["video_info"]["variants"][0]["url"]
						if '.m3u8' in DL_URL:
							DL_URL = media["video_info"]["variants"][1]["url"]
						if '?tag=' in DL_URL:
							DL_URL = DL_URL[:-6]
						FILENAME = os.path.basename(DL_URL)
						FILE_CHECK = FILENAME
					if os.path.exists(FILEPATH + FILE_CHECK) == False:
						_download_media(DL_URL, FILEPATH, FILENAME)



### add ###

def _add_new_object():
	for tmp_user in cmd_args.name:
		if not tmp_user in json_dict:
			if os.path.exists(download_directory + tmp_user) == False:
				os.makedirs(download_directory + tmp_user)
			json_dict.append({
				"name":tmp_user,
				"Query":{},
				"Profileflag":cmd_args.profile,
				"hashtagflag":cmd_args.hashtag,
				"TLflag":add_tl,
				"RTflag":cmd_args.rt,
				"videoflag":cmd_args.video,
				"gifflag":cmd_args.gif
			})



### follow user get ###

def _follow_userid_get(SCREEN_NAME):
	my_friends_list = []
	follow_user_fault_count = 0
	follow_user_list_fault_count = 0
	def _follow_user_list(SCREEN_NAME):
		nonlocal follow_user_list_fault_count
		nonlocal my_friends_list
		try:
			for tmp_id in tweepy.Cursor(twiapi.friends_ids, id=SCREEN_NAME).items():
				my_friends_list.append(tmp_id)
				follow_user_list_fault_count = 0
		except tweepy.RateLimitError as err_description:
			sleep(60 * 15)
			_follow_user_list(SCREEN_NAME)
		except Exception as err_description:
			if follow_user_list_fault_count < 3:
				follow_user_list_fault_count = follow_user_list_fault_count + 1
				err_subject = "Exception_follow_userid_get"
				_log(err_subject, err_description)
				sleep(60)
				_follow_user_list(SCREEN_NAME)
	_follow_user_list(SCREEN_NAME)
	return my_friends_list



### init ###

def init_start():
	if os.path.exists(DB_file) == False:
		print("json-file is not found.")
		q = input("Do you want to create a file?(y/n)")
		if q == "y":
			f = open(DB_file,'w+')
			f.close()
			print("result: " + str(os.path.exists(DB_file)))
		else:
			print("Please select json-file.")
			sys.exit()
	print("init done.\n")
	sys.exit()

	
	
### Edit json ###

def _edit_json():
	f = open(DB_file,'w')
	json.dump(json_dict, f)
	f.close()

	
	
### log ###

def _log(err_subject, err_description):
	print(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description))
	with open(LOGFILE,'a') as f:
		f.write(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description) + "\n")

		

### parser ###

def _parser():
	parser = argparse.ArgumentParser(
		usage=' python3 main.py [json-file]\n\
	python3 main.py [json-file] --addf --name user --tl --gif --video\n\
	python3 main.py [json-file] --addo --name user1 user2 user3 --tl --gif --video\n\
	nohup python3 main.py [json-file] &',
		add_help=True,
		formatter_class=argparse.RawTextHelpFormatter
		)
	parser.add_argument("json_file", help="please set DBfile.json.", type=str, nargs=1, metavar="[json-file]")
	parser.add_argument("--name", help="select object.", type=str, nargs='*', metavar="<object-name>...")
	parser.add_argument("--show", help="show object-list. if select object, show query.\n\n", action="store_true")

	parser.add_argument("--addf", help="add Screen's follow-user.", action="store_true")
	parser.add_argument("--addo", help="add new-screen-object or new-search-object.", action="store_true")
	parser.add_argument("--addq", help="add search-query to object.\n\n", type=str, nargs='*', metavar="<query-name>...")

	#parser.add_argument("--delo", help="del screen-object or search-object.", action="store_true")
	#parser.add_argument("--delq", help="del search-query object.\n\n", action="store_true")

	parser.add_argument("--profile", help="profile-check.", action="store_true")
	parser.add_argument("--hashtag", help="hashtag-check(TL, User-Profile).", action="store_true")
	parser.add_argument("--tl", help="TL-check.", action="store_true")
	parser.add_argument("--rt", help="including Retweets at TL-check.", action="store_true")
	parser.add_argument("--video", help="including video-file at Search,TL-check.", action="store_true")
	parser.add_argument("--gif", help="including gif-file at Search,TL-check.", action="store_true")
	return parser.parse_args()



### main ###

if __name__ == '__main__':
	cmd_args = _parser()

	if os.path.dirname(cmd_args.json_file[0]):
		working_directory = os.path.dirname(cmd_args.json_file[0]) + "/"
	else:
		working_directory = os.getcwd() +"/"
	#if not os.path.exists(working_directory + "download"):
	#       os.makedirs(working_directory + "download")
	#download_directory = working_directory + "download/"
	DB_file = working_directory + os.path.basename(cmd_args.json_file[0])
	DATE = datetime.datetime.today().strftime("%Y%m%d_%H%M_%S")
	LOGFILE = working_directory + DATE + "_log.txt"
	if not os.path.exists(DB_file):
		init_start()

	json_dict = []
	try:
		f = open(DB_file,'r')
		json_dict = json.load(f)
		f.close()
		shutil.copyfile(DB_file, DB_file + "_bak")
		print("get backupfile : " + DB_file + "_bak")
	except Exception as e:
		if os.path.getsize(DB_file) != 0:
			err_subject = "JSON file load"
			_log(err_subject, e)
			sys.exit()

	twiapi = tweepy_api()
	if cmd_args.addf or cmd_args.addo or cmd_args.addq is not None or cmd_args.show:
		if cmd_args.tl == False:
			add_tl = False
		else:
			add_tl = {"id":"", "date":""}
		if cmd_args.addf:
			if not cmd_args.name or len(cmd_args.name) != 1:
				print("invalid argument '--name'")
				sys.exit()
			my_friends_ids = _follow_userid_get(cmd_args.name[0])
			for tmp_id in my_friends_ids:
				USER_OBJECT = _twitter_userobject_get(tmp_id)
				if USER_OBJECT is "err":
					continue
				SCREEN_NAME = USER_OBJECT.screen_name
				urls = _twiprofurl_get(SCREEN_NAME, USER_OBJECT)
				channels = []
				for u in urls:
					init_res = _youtube_init(u)
					if init_res is not None:
						channels.append({"channel":init_res})
				if channels:
					for index,channel in enumerate(channels):
						subscript,videos,title = _youtube_info(channel["channel"])
						channels[index].update(title=title, subscript=subscript, videos=videos)
				if os.path.exists(working_directory + SCREEN_NAME) == False:
					os.makedirs(working_directory + SCREEN_NAME)
					if not SCREEN_NAME in json_dict:
						json_dict.append({
							"name":SCREEN_NAME,
							"Query":{},
							"Profileflag":cmd_args.profile,
							"hashtagflag":cmd_args.hashtag,
							"TLflag":add_tl,
							"RTflag":cmd_args.rt,
							"videoflag":cmd_args.video,
							"gifflag":cmd_args.gif
						})
		if cmd_args.addo:
			if not cmd_args.name:
				print("invalid argument '--name'")
			else:
				_add_new_object()
		if cmd_args.addq is not None:
			if not cmd_args.name or len(cmd_args.name) != 1:
				print("invalid argument '--name'")
			if len(cmd_args.addq) < 1:
				print("invalid argument '--addq'")
			else:
				_add_query()
		if cmd_args.show:
			if not cmd_args.name or len(cmd_args.name) != 1:
				print("invalid argument '--name'")
			else:
				_show()
		_edit_json()
		sys.exit()
	if len(json_dict) < 1:
		print("please add object.")
		sys.exit()

	for index,USER_JSON in enumerate(json_dict):
		SCREEN_NAME = USER_JSON["screen"]
		FILEPATH = working_directory + SCREEN_NAME
		
		USER_OBJECT = _twitter_userobject_get(SCREEN_NAME)
		if USER_OBJECT is "err":
			continue
		
		RT_FLAG = USER_JSON["RTflag"]
		GIF_FLAG = USER_JSON["gifflag"]
		VIDEO_FLAG = USER_JSON["videoflag"]
		FOLLOWER = USER_OBJECT.followers_count
		HASHTAG_CSV = []

		# Profile
		if USER_JSON["Profileflag"] == True:
			_profile(SCREEN_NAME, USER_OBJECT)
		#HASHTAG_CSV.extend(_twitter_profile_hashtag(SCREEN_NAME, USER_OBJECT))
		urls = _twiprofurl_get(SCREEN_NAME, USER_OBJECT)
		json_dict[index]["urls"].append(urls)

		# TL Search
		if USER_JSON["TLflag"] != False:
			TWEET_ID = USER_JSON["TLflag"]["id"]
			TWEET_ID,HASHTAG_LIST = _TL_search(SCREEN_NAME, TWEET_ID, FILEPATH, RT_FLAG, GIF_FLAG, VIDEO_FLAG)
			json_dict[index]["TLflag"]["id"] = TWEET_ID
			HASHTAG_CSV.extend(HASHTAG_LIST)

		# Query Search
		if not USER_JSON['Query'] == {}:
			for QUERY,search_date in USER_JSON['Query'].items():
				for l in range(50):
					search_fault_count = 0
					_search(FILEPATH, QUERY, GET_DATE, TWEET_ID, GIF_FLAG, VIDEO_FLAG)


		# tags
		#with open(working_directory + SCREEN_NAME + "/" + DATE + "_" + SCREEN_NAME + "_tags.csv", "w") as f:
		#	w = csv.writer(f, lineterminator='\n')
		#	w.writerow(HASHTAG_CSV)

		_edit_json()
	
	_log("Done.", "")

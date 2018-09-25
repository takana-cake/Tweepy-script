# _*_ coding: utf-8 _*_


from time import sleep
import datetime
import filecmp
import glob
import json
import os
import requests
import shutil
import subprocess
import sys
import tweepy
import urllib.request


### 認証 ###

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



### TL ###

def _TL_search():
	def _get_tweetid():
		nonlocal TL_search_fault_count
		try:
			get_id = api.user_timeline(TL_search_object["name"]).max_id
			return get_id
		except tweepy.RateLimitError as err_description:
			if TL_search_fault_count < 2:
				TL_search_fault_count = TL_search_fault_count + 1
				err_subject = str(follow_screen_get) + " : RateLimitError_3"
				_log(err_subject, err_description)
				sleep(60 * 15)
				_get_tweetid()
		except Exception as err_description:
			if TL_search_fault_count < 2:
				TL_search_fault_count = TL_search_fault_count + 1
				err_subject = str(follow_screen_get) + " : Exception_3"
				_log(err_subject, err_description)
				sleep(60)
				_get_tweetid()
	for TL_search_object in json_file:
		TL_search_fault_count = 0
		if 'TLflag' in TL_search_object:
			if TL_search_object["TLflag"]["id"] == "":
				start_id_and_date = _get_tweetid()
				TL_search_object["TLflag"]["id"] == start_id_and_date
				TL_search_object["TLflag"]["date"] == date
				query = 'max_search'
			else:
				query = 'since_search'
			_TL_tweet_get(TL_search_object, query)



def _TL_tweet_get(TL_search_object, search_flag):
	tweet_id = TL_search_object["TLflag"]["id"]
	screen = TL_search_object["name"]
	retweet_enable = TL_search_object["RTflag"]
	gif_enable = TL_search_object["gifflag"]
	video_enable = TL_search_object["videoflag"]
	
	tweet_id = ""
	
	def _tweet_get():
		nonlocal TL_tweet_get_fault_count
		nonlocal tweet_id
		try:
			if search_flag == 'max_search':
				for twi in api.user_timeline(screen, count=100, max_id=tweet_id):
					_download(twi, screen, retweet_enable, gif_enable, video_enable)
					tweet_id = twi.id
			elif search_flag == 'since_search':
				for twi in api.user_timeline(screen, count=100, since_id=tweet_id):
					_download(twi, screen, retweet_enable, gif_enable, video_enable)
					tweet_id = twi.id
			TL_tweet_get_fault_count = 0
		except tweepy.RateLimitError as err_description:
			if TL_tweet_get_fault_count < 2:
				err_subject = str(screen) + " : RateLimitError_4 : " + str(tweet_id) + " : TC=" + str(tweetidget_fault_count)
				_log(err_subject, err_description)
				TL_tweet_get_fault_count = TL_tweet_get_fault_count +1
				sleep(60 * 15)
				_tweet_get()
		except tweepy.TweepError as err_description:
			if TL_tweet_get_fault_count < 2:
				err_subject = str(screen) + " : TweepError_4 : " + str(tweet_id) + " : TC=" + str(tweetidget_fault_count)
				_log(err_subject, err_description)
				TL_tweet_get_fault_count = TL_tweet_get_fault_count +1
				sleep(60 * 5)
				_tweet_get()

	for l in range(50):
		TL_tweet_get_fault_count = 0
		_tweet_get()



### profile ###

def _profile_description_hashtag(screen_name):
	profile_description_hashtag_fault_count = 0
	def _description_hashtag():
		nonlocal profile_description_hashtag_fault_count
		try:
			description = api.get_user(screen_name).description
			description = re.sub(r'#', " #", description)
			pattern = re.compile(r'[\s\[\]\(\)\<\>\（\）\＜\＞\"\']')
			description_split = re.split(pattern, description)
			description_hashtags = [x for x in description_split if '#' in x]
			return(description_hashtags)
		except Exception as err:
			if profile_description_hashtag_fault_count < 2:
				profile_description_hashtag_fault_count = profile_description_hashtag_fault_count + 1
				sleep(60)
				_description_hashtag()

def _profile_get_url(screen_name):
	profile_get_url_fault_count = 0
	img = ""
	def _get_url():
		nonlocal profile_get_url_fault_count
		nonlocal img
		try:
			img = api.get_user(screen_name)
		except Exception as err:
			if profile_get_url_fault_count < 2:
				profile_get_url_fault_count = profile_get_url_fault_count + 1
				sleep(60)
				_get_url()
	_get_url()
	return img.profile_image_url_https, img.profile_banner_url

def _profile_get_img(url, file_name):
	profile_get_img_fault_count = 0
	def _get_img(url, file_name):
		nonlocal profile_get_img_fault_count
		nonlocal 
		res = requests.get(url=url)
		if res.status_code == 200:
			f = open(file_name, 'wb')
			f.write(res.content)
			f.close()
		elif profile_get_img_fault_count < 2:
			profile_get_img_fault_count = profile_get_img_fault_count + 1
			_get_img(url, file_name)
	_get_img(url, file_name)

def _profile_get_capture_icon(screen_name, file_path_cap):
	url_user = "https://twitter.com/" + screen_name
	capture_icon_file = file_path_cap + screen_name + "_capture_icon_" + date + ".jpg"
	cmd_capture_icon = "wkhtmltoimage --crop-h 255 --crop-w 255 --crop-x 50 --crop-y 185 " + url_user + " " + capture_icon_file
	subprocess.call(cmd_capture_icon.split(), shell=False)

def _profile_get_capture_banner(screen_name, file_path_cap):
	url_user = "https://twitter.com/" + screen_name
	capture_banner_file = file_path_cap + screen_name + "_capture_banner_" + date + ".jpg"
	cmd_capture_banner = "wkhtmltoimage --crop-h 380 --crop-w 1023 --crop-x 1 --crop-y 40 " + url_user + " " + capture_banner_file
	subprocess.call(cmd_capture_banner.split(), shell=False)

def _profile(screen_names):
	screen_name = ""
	file_path = working_directory
	file_path_cap = "<capture閲覧用>"
	flag = "0"
	for screen_name in screen_names:
		profile_image, profile_banner = _profile_get_url(screen_name)
		if '_normal' in profile_image:
			profile_image = profile_image.replace("_normal", "")
		elif '_mini' in profile_image:
			profile_image = profile_image.replace("_mini", "")
		elif '_bigger' in profile_image:
			profile_image = profile_image.replace("_bigger", "")
		comparison_icon_file = file_path + screen_name + "_comparison_icon_" + date + "." + profile_image.rsplit(".", 1)[1]
		_get_img(profile_image, comparison_icon_file)
		comparison_banner_file = file_path + screen_name + "_comparison_banner_" + date + ".jpg"
		_get_img(profile_banner, comparison_banner_file)
		if not glob.glob(file_path + screen_name + '_base*'):
			base_icon_file = file_path + screen_name + "_base_icon." + profile_image.rsplit(".", 1)[1]
			shutil.copyfile(comparison_icon_file, base_icon_file)
			shutil.copyfile(comparison_icon_file, file_path_cap + screen_name + "_icon_" + date + "." + profile_image.rsplit(".", 1)[1])
			base_banner_file = file_path + screen_name + "_base_banner.jpg"
			shutil.copyfile(comparison_banner_file, base_banner_file)
			shutil.copyfile(comparison_banner_file, file_path_cap + screen_name + "_banner_" + date + ".jpg")
			_profile_get_capture_icon(screen_name, file_path_cap)
			_profile_get_capture_banner(screen_name, file_path_cap)
		base_icon_file = glob.glob(file_path + screen_name + '_base_icon*')[0]
		base_banner_file = glob.glob(file_path + screen_name + '_base_banner*')[0]
		if filecmp.cmp(base_icon_file, comparison_icon_file) is False :
			shutil.copyfile(comparison_icon_file, file_path_cap + screen_name + "_icon_" + date + "." + profile_image.rsplit(".", 1)[1])
			shutil.copyfile(comparison_icon_file, base_icon_file)
			_profile_get_capture_icon(screen_name, file_path_cap)
			#api.update_with_media(filename=capture_file)
			flag = "1"
		if filecmp.cmp(base_banner_file, comparison_banner_file) is False:
			shutil.copyfile(comparison_banner_file, file_path_cap + screen_name + "_banner_" + date + ".jpg")
			shutil.copyfile(comparison_banner_file, base_banner_file)
			_profile_get_capture_banner(screen_name, file_path_cap)
			#api.update_with_media(filename=capture_file)
			flag = "1"
			os.remove(comparison_icon_file)
			os.remove(comparison_banner_file)
		if flag != "0":
			api.update_status("変わったかも_自動投稿")



### search ###

### search ###

def _search():
	hashtag_json = {}
	retry_count = 0
	for user_object in json_file:
		if tweet_id:
			search_query = 'since_search'
		else:
			search_query = 'max_search'
			tweet_id = api.search(q=search_query)
			tweet_id = tweet_id[0].id
		for l in range(50):
			try:
				if search_query == 'since_search':
					for twi in api.search(q=search_query, count=100, since_id=tweet_id):
						media_get(twi)
						tweet_id = twi.id
				else:
					for twi in api.search(q=search_query, count=100, max_id=tweet_id):
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
		hashtag_json[search_query] = tweet_id



### init ###

def init_start():
	if os.path.exists(working_directory) == False:
		os.makedirs(working_directory)
	if os.path.exists(working_directory + "db.json") == False:
		f = open(working_directory + "db.json",'w+')
		f.close()
	print("init done.\n")
	print(helptxt)
	sys.exit()



### Edit json ###

def _edit_json(editdata):
	json_file = open(working_directory + "db.json",'w')
	json.dump(editdata,json_file)
	json_file.close()



### add ###

def new_follow_ids_json():
	# 新規フォロー初期化用
	json_file = open(working_directory + "/_my_friends_list.json",'r')
	my_friends_list_json = json.load(json_file)
	json_file.close()
	for new_followuser_screen,new_followuser_detail in my_friends_list_json.items():
		if os.path.exists(working_directory + "/" + new_followuser_screen) == False:
			os.makedirs(working_directory + "/" + new_followuser_screen)
			f = open(working_directory + "/" + new_followuser_screen + "/_maxid.txt" , 'w+')
			f.close()
			my_friends_list_json[new_followuser_screen] = new_followuser_detail
	json_file = open(working_directory + "/_my_friends_list.json",'w')
	json.dump(my_friends_list_json,json_file)
	json_file.close()



### follow user get ###

def limit_handled(h):
	while True:
		try:
			yield h.next()
		except tweepy.RateLimitError as err_description:
			err_subject = "RateLimitError_1"
			_log(err_subject, err_description)
			time.sleep(60 * 15)
		except tweepy.TweepError as err_description:
			err_subject = "TweepError_1"
			_log(err_subject, err_description)
			time.sleep(60 * 15)

def _follow_user_get
	for tmp_id in limit_handled(tweepy.Cursor(api.friends_ids, id=my_id).items()):
		my_friends_ids.append(tmp_id)
	# 100IDsずつ詳細をmy_friends_listへ
	follow_counter = 0
	for i in range(0, len(my_friends_ids), 100):
		try:
			for tmp_user in api.lookup_users(user_ids=my_friends_ids[i:i+100]):
				follow_counter = follow_counter + 1
				my_friends_list[tmp_user.screen_name] = tmp_user.name
				#my_friends_list[tmp_user.screen_name] = {"name":tmp_user.name, "maxid":""}
		except tweepy.RateLimitError as err:
			time.sleep(60 * 15)
			continue
		except Exception as err:
			time.sleep(60 * 3)
			continue



### log ###

def _log(err_subject, err_description):
	print(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description))
	with open(LOGFILE,'a') as f:
		f.write(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description) + "\n")



### download ###

def _download(twi_def, download_filepath, retweet_enable, gif_enable, video_enable):
	download_fault_count = 0
	def _download_file():
		nonlocal download_fault_count
		nonlocal dl_filename
		nonlocal dl_media
		try:
			with open(working_directory + download_filepath + "/" + os.path.basename(dl_filename), 'wb') as f:
				dl_file = urllib.request.urlopen(dl_media).read()
				f.write(dl_file)
		except tweepy.RateLimitError as err:
			if download_fault_count < 2:
				download_fault_count = download_fault_count +1
				time.sleep(60 * 5)
				_download_file()
			else:
				download_fault_count = 0
		except Exception as err:
			if download_fault_count < 2:
				download_fault_count = download_fault_count +1
				time.sleep(60)
				_download_file()
			else:
				download_fault_count = 0
		download_fault_count = 0
	# リツイート判断
	if hasattr(twi_def, 'retweeted_status') is True and retweet_enable = False:
		pass
	else:
		# メディア判断
		if hasattr(twi_def, "extended_entities"):
			if 'media' in twi_def.extended_entities:
				for media in twi_def.extended_entities["media"]:
					if media["type"] == 'photo':
						dl_filename = media["media_url"]
						dl_media = dl_filename + ":orig"
					if media["type"] == 'animated_gif' and gif_enable == True:
						dl_media = media["video_info"]["variants"][0]["url"]
						dl_filename = dl_media
					if media["type"] == 'video' and video_enable == True:
						dl_media = media["video_info"]["variants"][0]["url"]
						if '.m3u8' in dl_media:
							dl_media = media["video_info"]["variants"][1]["url"]
						if '?tag=' in dl_media:
							dl_media = dl_media[:-6]
						dl_filename = dl_media
					if os.path.exists(working_directory + download_filepath + "/" + os.path.basename(dl_filename)) == False:
						_download_file()


						
### help ###
helptxt = "Usage: python3 main.py [OPTION]...				\n\
       python3 main.py --file [DB json]				\n\
									\n\
  --file [DB json]			Select json-file.		\n\
  --name				Select object to edit.	 	\n\
	--add-query [query word]	Add search-query.		\n\
  --add-object				Add object.			\n\
  	--add-query [query word]					\n\
  	--profile [True or False]					\n\
  	--tl [True or False]						\n\
  	--rt [True or False]						\n\
  	--video [True or False]						\n\
  	--gif [True or False]						\n\
"


### main ###

if __name__ == '__main__':
	api = tweepy_api()
	date = datetime.datetime.today().strftime("%Y%m%d_%H%M_%S")
	working_directory = "./"
	#working_directory = os.path.dirname(filepath)
	LOGFILE = working_directory + str(datetime.datetime.now()) + "_log.txt"
	f = open(working_directory + "",'r')
	json_file = json.load(f)
	f.close()
'''
import argparse

parser = argparse.ArgumentParser(
	usage=' python3 main.py\n\
	python3 main.py [DB json] [OPTION]...',
	add_help=True,
	)
parser.add_argument("json", help="please set me.", type=str,  nargs=1)
parser.add_argument("--name", help="select object.", type=str, nargs=1, metavar="<object-name>")
parser.add_argument("--add-object", help="add new-screen or new-search-description.", nargs=1,  metavar="<object-name>")
parser.add_argument("--add-query", help="add search-query to object.", metavar="<query>")
parser.add_argument("--profile", help="profile-check.", choices=['True','False'], nargs=1,   metavar="<True/False>")
parser.add_argument("--tl", help="TL-check.", choices=['True','False'], nargs=1,   metavar="<True/False>")
parser.add_argument("--rt", help="including Retweets at TL-check.", choices=['True','False'], nargs=1,   metavar="<True/False>")
parser.add_argument("--video", help="including video-file at Search,TL-check.", choices=['True','False'], nargs=1,   metavar="<True/False>")
parser.add_argument("--gif", help="including gif-file at Search,TL-check.", choices=['True','False'], nargs=1, metavar="<True/False>")

args = parser.parse_args()

args.gif
'''



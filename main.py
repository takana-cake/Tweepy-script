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
import argparse


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
				err_subject = TL_search_object["name"] + " : RateLimitError_3"
				_log(err_subject, err_description)
				sleep(60 * 15)
				_get_tweetid()
		except Exception as err_description:
			if TL_search_fault_count < 2:
				TL_search_fault_count = TL_search_fault_count + 1
				err_subject = TL_search_object["name"] + " : Exception_3"
				_log(err_subject, err_description)
				sleep(60)
				_get_tweetid()
	for TL_search_object in json_dict:
		TL_search_fault_count = 0
		if TL_search_object["TLflag"] is not "False":
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
	retweet_enable = TL_search_object["RTflag"][0]
	gif_enable = TL_search_object["gifflag"][0]
	video_enable = TL_search_object["videoflag"][0]
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
				err_subject = str(screen) + " : RateLimitError_4 : " + str(tweet_id)
				_log(err_subject, err_description)
				TL_tweet_get_fault_count = TL_tweet_get_fault_count +1
				sleep(60 * 15)
				_tweet_get()
		except tweepy.TweepError as err_description:
			if TL_tweet_get_fault_count < 2:
				err_subject = str(screen) + " : TweepError_4 : " + str(tweet_id)
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

def _profile():
	file_path = working_directory
	#file_path_cap = "<capture閲覧用>"
	file_path_cap = working_directory
	flag = "0"
	
	for profile_object in json_dict:
		if "Profileflag" in profile_object:
			if profile_object["Profileflag"] is "True":
				profile_object_name = profile_object["name"]
				profile_image, profile_banner = _profile_get_url(profile_object_name)
				if '_normal' in profile_image:
					profile_image = profile_image.replace("_normal", "")
				elif '_mini' in profile_image:
					profile_image = profile_image.replace("_mini", "")
				elif '_bigger' in profile_image:
					profile_image = profile_image.replace("_bigger", "")
				comparison_icon_file = file_path + profile_object_name + "_comparison_icon_" + date + "." + profile_image.rsplit(".", 1)[1]
				_get_img(profile_image, comparison_icon_file)
				comparison_banner_file = file_path + profile_object_name + "_comparison_banner_" + date + ".jpg"
				_get_img(profile_banner, comparison_banner_file)
				if not glob.glob(file_path + profile_object_name + '_base*'):
					base_icon_file = file_path + profile_object_name + "_base_icon." + profile_image.rsplit(".", 1)[1]
					shutil.copyfile(comparison_icon_file, base_icon_file)
					shutil.copyfile(comparison_icon_file, file_path_cap + profile_object_name + "_icon_" + date + "." + profile_image.rsplit(".", 1)[1])
					base_banner_file = file_path + profile_object_name + "_base_banner.jpg"
					shutil.copyfile(comparison_banner_file, base_banner_file)
					shutil.copyfile(comparison_banner_file, file_path_cap + profile_object_name + "_banner_" + date + ".jpg")
					_profile_get_capture_icon(profile_object_name, file_path_cap)
					_profile_get_capture_banner(profile_object_name, file_path_cap)
				base_icon_file = glob.glob(file_path + profile_object_name + '_base_icon*')[0]
				base_banner_file = glob.glob(file_path + profile_object_name + '_base_banner*')[0]
				if filecmp.cmp(base_icon_file, comparison_icon_file) is False :
					shutil.copyfile(comparison_icon_file, file_path_cap + profile_object_name + "_icon_" + date + "." + profile_image.rsplit(".", 1)[1])
					shutil.copyfile(comparison_icon_file, base_icon_file)
					_profile_get_capture_icon(profile_object_name, file_path_cap)
					#api.update_with_media(filename=capture_file)
					flag = "1"
				if filecmp.cmp(base_banner_file, comparison_banner_file) is False:
					shutil.copyfile(comparison_banner_file, file_path_cap + profile_object_name + "_banner_" + date + ".jpg")
					shutil.copyfile(comparison_banner_file, base_banner_file)
					_profile_get_capture_banner(profile_object_name, file_path_cap)
					#api.update_with_media(filename=capture_file)
					flag = "1"
					os.remove(comparison_icon_file)
					os.remove(comparison_banner_file)
				if flag != "0":
					api.update_status("変わったかも_自動投稿")



### search ###

def _search():
	hashtag_json = {}
	retry_count = 0
	for user_object in json_dict:
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
		#os.makedirs(working_directory)
		print("directory is not found.")
		sys.exit()
	if os.path.exists(DB_file) == False:
		print("json-file is not found.")
		print("Do you want to create a file?(y/n)")
		q = input()
		if q == "y":
			f = open(DB_file,'w+')
			f.close()
			json_dict.append({
				"name":"",
				"Query":"",
				"Profileflag":"",
				"TLflag":"",
				"RTflag":"",
				"videoflag":"",
				"gifflag":""
			})
			_edit_json()
			print("result: " + str(os.path.exists(DB_file)))
	print("init done.\n")



### Edit json ###

def _edit_json():
	f = open(DB_file,'w')
	json.dump(json_dict, f)
	f.close()



### add ###

def new_follow_ids_json():
	# 新規フォロー初期化用
	f = open(DB_file,'r')
	my_friends_list_json = json.load(f)
	f.close()
	for new_followuser_screen,new_followuser_detail in my_friends_list_json.items():
		if os.path.exists(working_directory + new_followuser_screen) == False:
			os.makedirs(working_directory + new_followuser_screen)
			f = open(working_directory + new_followuser_screen + "/_maxid.txt" , 'w+')
			f.close()
			my_friends_list_json[new_followuser_screen] = new_followuser_detail
	f = open(DB_file,'w')
	json.dump(my_friends_list_json,f)
	f.close()

def _add_user_list():
	if cmd_args.tl is "False":
		add_tl = "False"
	else:
		add_tl = {"id":"", "date":""}
	if cmd_args.video is "False":
		add_video = "False"
	else:
		add_video = "True"
	if cmd_args.gif is "False":
		add_gif = "False"
	else:
		add_gif = "True"
	for tmp_user in cmd_args.name:
		if not tmp_user in json_dict:
			json_dict.append({
				"name":tmp_user,
				"Query":"",
				"Profileflag":cmd_args.profile,
				"TLflag":add_tl,
				"RTflag":cmd_args.rt,
				"videoflag":add_video,
				"gifflag":add_gif
			})



### follow user get ###

def _follow_user_get(my_id):
	my_friends_ids = []
	follow_user_fault_count = 0
	follow_user_list_fault_count = 0
	def _follow_user_list():
		nonlocal follow_user_list_fault_count
		try:
			for tmp_id in tweepy.Cursor(api.friends_ids, id=my_id).items():
				my_friends_ids.append(tmp_id)
		except tweepy.RateLimitError as err_description:
			if follow_user_list_fault_count < 2:
				follow_user_list_fault_count = follow_user_list_fault_count + 1
				err_subject = "RateLimitError_follow_user_get_1"
				_log(err_subject, err_description)
				sleep(60 * 15)
				_follow_user()
		except Exception as err_description:
			if follow_user_list_fault_count < 2:
				follow_user_list_fault_count = follow_user_list_fault_count + 1
				err_subject = "Exception_follow_user_get_1"
				_log(err_subject, err_description)
				sleep(60)
				_follow_user()
	def _follow_user_description():
		nonlocal my_friends_ids
		nonlocal follow_user_fault_count
		try:
			for tmp_user in api.lookup_users(user_ids=my_friends_ids[i:i+100]):
				if not tmp_user.name in json_dict:
					json_dict.append({
						"name":tmp_user.screen_name,
						"Query":"",
						"Profileflag":"",
						"TLflag":{"id":"", "date":""},
						"RTflag":"",
						"videoflag":"",
						"gifflag":""
					})
		except tweepy.RateLimitError as err_description:
			if follow_user_fault_count < 2:
				follow_user_fault_count = follow_user_fault_count + 1
				err_subject = "RateLimitError_follow_user_get_2"
				_log(err_subject, err_description)
				sleep(60 * 15)
				_follow_user()
		except Exception as err_description:
			if follow_user_fault_count < 2:
				follow_user_fault_count = follow_user_fault_count + 1
				err_subject = "Exception_follow_user_get_2"
				_log(err_subject, err_description)
				sleep(60)
				_follow_user()
	for i in range(0, len(my_friends_ids), 100):
		_follow_user_description()



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
	if hasattr(twi_def, 'retweeted_status') is True and retweet_enable is False:
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
				


### main ###

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		usage=' python3 main.py [json-file] [OPTION]...\n\
	nohup python3 main.py [json-file] [OPTION]... ',
		add_help=True,
		formatter_class=argparse.RawTextHelpFormatter
		)
	parser.add_argument("json_file", help="please set DBfile.json.\n\n", type=str, nargs=1, metavar="[json-file]")

	parser.add_argument("--name", help="select object.", type=str, nargs='*', metavar="<object-name>")
	parser.add_argument("--show",help="show db-objects.\nselect --name, show object summary.")
	parser.add_argument("--add-follow-user", dest=add_follow_user, help="add Screen's follow-user.")
	#parser.add_argument("--add-object", dest=add_object, help="add new-screen or new-search-description.")
	#parser.add_argument("--add-query", dest=add_query, help="add search-query to object.\n\n")

	parser.add_argument("--profile", help="profile-check. (default False)", choices=['True','False'], nargs=1, metavar="<True/False>")
	parser.add_argument("--tl", help="TL-check. (default True)", choices=['True','False'], nargs=1, metavar="<True/False>")
	parser.add_argument("--rt", help="including Retweets at TL-check. (default False)", choices=['True','False'], nargs=1, metavar="<True/False>")
	parser.add_argument("--video", help="including video-file at Search,TL-check. (default True)", choices=['True','False'], nargs=1, metavar="<True/False>")
	parser.add_argument("--gif", help="including gif-file at Search,TL-check. (default True)", choices=['True','False'], nargs=1, metavar="<True/False>")
	cmd_args = parser.parse_args()

	working_directory = os.path.dirname(cmd_args.json_file[0]) + "/"
	DB_file = cmd_args.json_file[0]
	date = datetime.datetime.today().strftime("%Y%m%d_%H%M_%S")
	LOGFILE = working_directory + date + "_log.txt"
	json_dict = []

	if not os.path.exists(DB_file):
		init_start()

	f = open(DB_file,'r')
	json_dict = json.load(f)
	f.close()

	if cmd_args.add_follow_user and cmd_args.name is not "None":
		_add_user_list()
	if len(json_dict) < 1:
		sys.exit()

	api = tweepy_api()

	_TL_search()
	_profile()
	_search()
	
	_edit_json()



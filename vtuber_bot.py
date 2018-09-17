# _*_ coding: utf-8 _*_

'''
wkhtmltoimageは/usr/local/binに入るからcronで動かすときはPATHを通す

flow

アイコン取得
アイコンの変化を確認
キャプチャ&トリミング
投稿

'''

import tweepy
import requests
import os
import datetime
import subprocess
import glob
import shutil
import filecmp


# 認証
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
	return(tweepy_auth)


def get_url(screen_name):
	try:
		img = api.get_user(screen_name)
		return img.profile_image_url_https, img.profile_banner_url
	except Exception as err:
		return None

def get_img(url, file_name):
	res = requests.get(url=url)
	if res.status_code == 200:
		f = open(file_name, 'wb')
		f.write(res.content)
		f.close()

def get_capture_icon(screen_name):
	url_user = "https://twitter.com/" + screen_name
	capture_icon_file = file_path_cap + screen_name + "_capture_icon_" + date + ".jpg"
	cmd_capture_icon = "wkhtmltoimage --crop-h 255 --crop-w 255 --crop-x 50 --crop-y 185 " + url_user + " " + capture_icon_file
	subprocess.call(cmd_capture_icon.split(), shell=False)

def get_capture_banner(screen_name):
	url_user = "https://twitter.com/" + screen_name
	capture_banner_file = file_path_cap + screen_name + "_capture_banner_" + date + ".jpg"
	cmd_capture_banner = "wkhtmltoimage --crop-h 380 --crop-w 1023 --crop-x 1 --crop-y 40 " + url_user + " " + capture_banner_file
	subprocess.call(cmd_capture_banner.split(), shell=False)

### main


screen_names = [
	"screen1", "screen2"
]

screen_and_usernames = [
	{"screen1":"name1"}, {"screen2":"name2"}
]

screen_name = ""
file_path = "./"
file_path_cap = "./"
capture_file = ""
date = datetime.datetime.today().strftime("%Y%m%d_%H%M_%S")
flag = "0"

api = tweepy_api()

for screen_name in screen_names:
	profile_image, profile_banner = get_url(screen_name)
	if '_normal' in profile_image:
		profile_image = profile_image.replace("_normal", "")
	elif '_mini' in profile_image:
		profile_image = profile_image.replace("_mini", "")
	elif '_bigger' in profile_image:
		profile_image = profile_image.replace("_bigger", "")
	comparison_icon_file = file_path + screen_name + "_comparison_icon_" + date + "." + profile_image.rsplit(".", 1)[1]
	get_img(profile_image, comparison_icon_file)
	comparison_banner_file = file_path + screen_name + "_comparison_banner_" + date + ".jpg"
	get_img(profile_banner, comparison_banner_file)

	if not glob.glob(file_path + screen_name + '_base*'):
		base_icon_file = file_path + screen_name + "_base_icon." + profile_image.rsplit(".", 1)[1]
		shutil.copyfile(comparison_icon_file, base_icon_file)
		shutil.copyfile(comparison_icon_file, file_path_cap + screen_name + "_icon_" + date + "." + profile_image.rsplit(".", 1)[1])
		base_banner_file = file_path + screen_name + "_base_banner.jpg"
		shutil.copyfile(comparison_banner_file, base_banner_file)
		shutil.copyfile(comparison_banner_file, file_path_cap + screen_name + "_banner_" + date + ".jpg")
		get_capture_icon(screen_name)
		get_capture_banner(screen_name)

	base_icon_file = glob.glob(file_path + screen_name + '_base_icon*')[0]
	base_banner_file = glob.glob(file_path + screen_name + '_base_banner*')[0]

	if filecmp.cmp(base_icon_file, comparison_icon_file) is False :
		shutil.copyfile(comparison_icon_file, file_path_cap + screen_name + "_icon_" + date + "." + profile_image.rsplit(".", 1)[1])
		shutil.copyfile(comparison_icon_file, base_icon_file)
		get_capture_icon(screen_name)
		#api.update_with_media(filename=capture_file)
		flag = "1"
	if filecmp.cmp(base_banner_file, comparison_banner_file) is False:
		shutil.copyfile(comparison_banner_file, file_path_cap + screen_name + "_banner_" + date + ".jpg")
		shutil.copyfile(comparison_banner_file, base_banner_file)
		get_capture_banner(screen_name)
		#api.update_with_media(filename=capture_file)
		flag = "1"
	os.remove(comparison_icon_file)
	os.remove(comparison_banner_file)

if flag != "0":
	api.update_status("変わったかも_自動投稿")

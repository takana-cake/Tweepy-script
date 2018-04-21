# _*_ coding: utf-8 _*_

# print str(datetime.datetime.now())
# print "--------------------"
# Apr 18 21:12:52 user kernel: [8653289.147897] ieee80211 phy0: rt2800usb_txdone: Warning - Data pending for entry 4 in queue 2
# ���� �G���[�ӏ�: �I�v�V����: �G���[���e\n


import tweepy
import sys
import urllib
import os
import datetime

def limit_handled(h):
	while True:
		try:
			yield h.next()
		except tweepy.RateLimitError, err:
			print str(datetime.datetime.now())
			print "RateLimitError_1"
			print err
			print "--------------------"
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": RateLimitError_1: " + str(err) + "\n")
			time.sleep(60 * 15)
		except tweepy.TweepError, err:
			print str(datetime.datetime.now())
			print "TweepError_1"
			print err
			print "--------------------"
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": TweepError_1: " + str(err) + "\n")
			time.sleep(60 * 15)

# �F��
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
# my_id_select = ���X�gmy_id�����ID���i�[����ꎞ�ϐ�
# tmp_id = api.friends_ids����my_friends_ids�֊i�[����Ƃ��̈ꎞ�ϐ�
my_friends_ids = []		#�t�H���[���Ă���ID�ƃX�N���[����
my_friends_list = {}	#
# i = len(my_friends_ids) , maxid�i�[����Ƃ��̈ꎞ�ϐ�
# tmp_user = ���p�H
# follow_id = �t�H���[���Ă�id
# follow_screen = �t�H���[���Ă�X�N���[����
# err = �G���[
# f = �t�@�C��
# l = 16*200��16
# twi = TL
tmp_count = 0
tmp_count2 = 0
print "--------------------"

for my_id_select in my_id:
	print str(datetime.datetime.now())
	print my_id_select
	print "--------------------"
	file_path = os.getcwd() + "/" + my_id_select
	if os.path.exists(file_path) == False:
		os.makedirs(file_path)
	# ���O�t�@�C���쐬
	with open(file_path + "/_log.txt",'w+') as f:
		f.write(str(datetime.datetime.now()) + ": start: " + str(my_id_select) + "\n")

	## my_id_select�̃t�H���[����ID��my_friends_ids�Ɏ擾
	# Cursor�g���Ƃ��ׂĎ���Ă��Ă���邪�C�z��ł͂Ȃ��Ȃ�̂Ŕz��ɓ����
	for tmp_id in limit_handled(tweepy.Cursor(api.friends_ids, id=my_id_select).items()):
		my_friends_ids.append(tmp_id)
	# 100IDs���ڍׂ�my_friends_list��
	# tmp_count�̓t�H���[���J�E���^�[�Atmp_count2�̓G���[����i�`�F�b�N
	tmp_count = 0
	tmp_count2 = 0
	for i in range(0, len(my_friends_ids), 100):
		try:
			for tmp_user in api.lookup_users(user_ids=my_friends_ids[i:i+100]):
				# tmp_user�̒��g�m�肽���B�����ɓ����\��
				tmp_count = tmp_count + 1
				my_friends_list[unicode(tmp_user.screen_name)] = unicode(tmp_user.name)
			if tmp_count2 == 1:
				print i
				print "--------------------"
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": retry: i=" + str(i) + ": done\n")
		except tweepy.RateLimitError, err:
			print str(datetime.datetime.now())
			print "RateLimitError_2"
			print err
			print i
			print tmp_user
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": RateLimitError_2: i=" + str(i) + ": " + str(err) + "\n")
			tmp_count2 = 1
			time.sleep(60 * 15)
			continue
		except tweepy.TweepError, err:
			print str(datetime.datetime.now())
			print "TweepError_2"
			print err
			print i
			with open(file_path + "/_log.txt",'a') as f:
				f.write(str(datetime.datetime.now()) + ": TweepError_2: i=" + str(i) + ": " + str(err) + "\n")
			tmp_count2 = 1
			time.sleep(60 * 15)
			continue
	print str(datetime.datetime.now()) + ": " + len(my_friends_ids) +"/" + tmp_count
	print "--------------------"
	with open(file_path + "/_log.txt",'a') as f:
		f.write(str(datetime.datetime.now()) + ": " + str(len(my_friends_ids)) + "/" + str(tmp_count) + "\n")

	## �擾�J�n�̃c�C�[�gID��maxid�ւ����
	# tmp_count��API�G���[����MAXID�m�F�p�t���O
	# ./my_id_select/follow_id/_maxid.txt�ɑO����s����MAXID���L�^���Ă���
	# �����ȉ���API�͌��A�J���Ǝ擾�ł��Ȃ��̂ő΃��[�v�p��tmp_count���g�p
	tmp_count = 0
	for follow_id,follow_screen in my_friends_list.items():
		print str(datetime.datetime.now()) + ": " + follow_id
		#follow_id�f�B���N�g����������΍쐬
		if os.path.exists(file_path + "/" + follow_id) == False:
			os.makedirs(file_path + "/" + follow_id)
		#_maxid.txt�t�@�C����������΍쐬
		if os.path.exists(file_path + "/" + follow_id + "/_maxid.txt") == False:
			f = open(file_path + "/" + follow_id + "/_maxid.txt" , 'w+')
			f.close()
		#_maxid.txt�t�@�C������Ȃ�maxid���擾
		if os.path.getsize(file_path + "/" + follow_id + "/_maxid.txt") == 0:
			query = 'max_search'
			try:
				maxid = api.user_timeline(follow_id).max_id
			#API�΍�
			except tweepy.RateLimitError, err:
				print str(datetime.datetime.now())
				print follow_id
				print "RateLimitError_3"
				print err
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + ": " + str(follow_id) + ": RateLimitError_3: " + str(err) + "\n")
				time.sleep(60 * 15)
				continue
			#���̑��A���A�J�΍�
			except tweepy.TweepError, err:
				print str(datetime.datetime.now())
				print follow_id
				print "TweepError_3"
				print err
				print tmp_count
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
		#�O���_maxid.txt��maxid�֓���Č���
		else:
			f = open(file_path + "/" + follow_id + "/_maxid.txt" , 'r')
			for i in f: maxid = i
			f.close()
			query = 'since_search'

		## �摜�擾
		# tmp_count�͗�O���m�p�Atmp_count2��3��܂ōĎ��s����p
		tmp_count = 0
		tmp_count2 = 0
		#01
		for l in range(16):
			#02-1
			#TL���擾_API
			try:
				#02�̃`�F�b�N�㔼
				if tmp_count != 0:
					print str(datetime.datetime.now())
					print follow_id
					print maxid
					tmp_count = 0
					with open(file_path + "/_log.txt",'a') as f:
						f.write(str(datetime.datetime.now()) + str(follow_id) + ": 02-1: " + str(maxid) + " TC=" + str(tmp_count) + "\n")
				if query == 'max_search':
					#03-1
					for twi in api.user_timeline(follow_id, count=200, max_id=maxid):
						# �摜�ۑ�
						if hasattr(twi, "extended_entities"):
							if twi.extended_entities.has_key("media"):
								for index,media in enumerate(twi.extended_entities["media"]):
									img_url = media["media_url"]
									url_orig = img_url + ":orig"
									try:
										with open(file_path + "/" + follow_id + "/" + os.path.basename(img_url), 'wb') as f:
											img = urllib.urlopen(url_orig).read()
											f.write(img)
									except Exception as err:
										print str(datetime.datetime.now())
										print follow_id
										print "img url open fail #03-1"
										print url_orig
										print err
										with open(file_path + "/_log.txt",'a') as f:
											f.write(str(datetime.datetime.now()) + str(follow_id) + ": 03-1: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
										tmp_count2 = tmp_count2 +1
										if tmp_count2 < 3:
											time.sleep(60)
											continue
										else:
											tmp_count2 = 0
									except:
										# �����s���̕s�������
										print str(datetime.datetime.now())
										print "!!!fail!!!"
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
					#03-1 �I��
				elif query == 'since_search':
					#03-2
					for twi in api.user_timeline(follow_id, count=200, since_id=maxid):
						# �摜�ۑ�
						if hasattr(twi, "extended_entities"):
							if twi.extended_entities.has_key("media"):
								for index,media in enumerate(twi.extended_entities["media"]):
									img_url = media["media_url"]
									url_orig = img_url + ":orig"
									try:
										with open(file_path + "/" + follow_id + "/" + os.path.basename(img_url), 'wb') as f:
											img = urllib.urlopen(url_orig).read()
											f.write(img)
									except Exception as err:
										print str(datetime.datetime.now())
										print follow_id
										print "img url open fail #03-2"
										print url_orig
										print err
										with open(file_path + "/_log.txt",'a') as f:
											f.write(str(datetime.datetime.now()) + str(follow_id) + ": 03-2: " + str(url_orig) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
										tmp_count2 = tmp_count2 +1
										if tmp_count2 < 3:
											time.sleep(60)
											continue
										else:
											tmp_count2 = 0
									except:
										# �����s���̕s�������
										print str(datetime.datetime.now())
										print "!!!fail!!!"
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
					#03-2 �I��
					with open(file_path + "/" + follow_id + "/_maxid.txt", 'w+') as f:
						f.write(str(maxid))
			#02-2
			except tweepy.RateLimitError, err:
				print str(datetime.datetime.now())
				print follow_id
				print "RateLimitError_4"
				print err
				print maxid
				tmp_count = 1
				with open(file_path + "/_log.txt",'a') as f:
					f.write(str(datetime.datetime.now()) + str(follow_id) + ": RateLimitError_4: " + str(maxid) + ": TC=" + str(tmp_count2) + ": " + str(err) + "\n")
				time.sleep(60 * 15)
				continue
			#02-3
			except tweepy.TweepError, err:
				print str(datetime.datetime.now())
				print follow_id
				print "TweepError_4"
				print err
				print maxid
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
		#01 �I��
	my_friends_list.clear()
	my_friends_ids = []
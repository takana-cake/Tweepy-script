# _*_ coding: utf-8 _*_

import datetime
import time

### TL chech ###

def _TL_search(api, usr_id, search_id, search_flag):

	def _get_tweetid():
		nonlocal TL_search_fault_count
		try:
			get_id = api.user_timeline(usr_id).max_id
			return get_id
		except tweepy.RateLimitError as err_description:
			if TL_search_fault_count < 2:
				TL_search_fault_count = TL_search_fault_count + 1
				err_subject = usr_id + " : RateLimitError_TL_search"
				print(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description))
				sleep(60 * 15)
				_get_tweetid()
		except Exception as err_description:
			if TL_search_fault_count < 2:
				TL_search_fault_count = TL_search_fault_count + 1
				err_subject = usr_id + " : Exception_TL_search"
				print(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description))
				sleep(60)
				_get_tweetid()
	def _TL_get():
		nonlocal TL_get_fault_count
		nonlocal TL_search_object
		nonlocal search_flag
		try:
			if search_flag == 'max_search':
				for twi in api.user_timeline(usr_id, count=100, max_id=search_id):
					search_id = twi.id
					TL_get_fault_count = 0
			elif search_flag == 'since_search':
				for twi in api.user_timeline(usr_id, count=100, since_id=search_id):
					search_id = twi.id
					TL_get_fault_count = 0
		except tweepy.RateLimitError as err_description:
			if TL_get_fault_count < 2:
				err_subject = str(usr_id) + " : RateLimitError_tweet_get : " + str(search_id)
				_log(err_subject, err_description)
				TL_get_fault_count = TL_get_fault_count +1
				sleep(60 * 15)
				_TL_get()
		except Exception as err_description:
			if TL_get_fault_count < 2:
				err_subject = str(usr_id) + " : Exception_tweet_get : " + str(search_id)
				_log(err_subject, err_description)
				TL_get_fault_count = TL_get_fault_count +1
				sleep(60 * 5)
				_TL_get()

	TL_get_fault_count = 0
	TL_search_fault_count = 0
	if search_id == "":
		search_id = _get_tweetid()
		search_flag = 'max_search'
	else:
		search_flag = 'since_search'
		for l in range(50):
			_TL_get()
	return(search_id)

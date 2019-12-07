# _*_ coding: utf-8 _*_

import datetime
import time

### search ###

def _search(api, screen_name, search_id, search_query):
	search_fault_count = 0
	def _search_start(screen_name):
		nonlocal search_fault_count
		nonlocal search_flag
		nonlocal search_query
		nonlocal search_id
		try:
			if search_flag == 'since_search':
				for twi in api.search(q=search_query, count=100, since_id=search_id):
					if twi:
						#処理
						search_id = twi.id
						search_fault_count = 0
			else:
				for twi in api.search(q=search_query, count=100, max_id=search_id):
					if twi:
						#処理
						search_id = twi.id
						search_fault_count = 0
		except tweepy.RateLimitError as err_description:
			if search_fault_count < 3:
				search_fault_count = search_fault_count +1
				err_subject = screen_name + " : RateLimitError_search_start"
				print(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description))
				sleep(300 * 3)
				_search_start(screen_name)
		except Exception as err_description:
			if search_fault_count < 3:
				search_fault_count = search_fault_count +1
				err_subject = screen_name + " : Exception_search_start"
				print(str(datetime.datetime.now()) + " : " + str(err_subject) + " : " + str(err_description))
				sleep(10)
				_search_start(screen_name)
	if search_id:
		if api.search(q=search_query, since_id=search_id):
			search_flag = 'since_search'
	else:
		search_id_tmp = api.search(q=search_query, count=1)
		if search_id_tmp:
			search_flag = 'max_search'
			search_id = search_id_tmp[0].id
		else:
			return()
	for l in range(50):
		search_fault_count = 0
		_search_start(screen_name)
	return(search_id)

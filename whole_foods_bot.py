import os, time
from selenium import webdriver

import bs4
import slack_bot as sb
import ast


def create_driver():
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	ROOT_DIR = os.path.dirname(BASE_DIR)
	chromedriver = ROOT_DIR + "/chromedriver"
	
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.add_argument('--incognito')
	chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
	return driver


def terminate(driver):
	driver.quit()


def go_delivery_page(driver, credentials):
	# amazon credentials
	amazon_username = credentials['wholefoods']['amazon_username']
	amazon_password = credentials['wholefoods']['amazon_password']
	print('Initiate driver')
	driver = create_driver()
	print('Go to the slots page')
	driver.get('https://www.amazon.com/gp/sign-in.html')
	driver.get('https://www.amazon.com/gp/sign-in.html')
	email_field = driver.find_element_by_css_selector('#ap_email')
	print('Enter Username')
	email_field.send_keys(amazon_username)
	driver.find_element_by_css_selector('#continue').click()
	time.sleep(1.5)
	password_field = driver.find_element_by_css_selector('#ap_password')
	print('Enter Password')
	password_field.send_keys(amazon_password)
	driver.find_element_by_css_selector('#signInSubmit').click()
	print('On Amazon Webpage')
	time.sleep(1.5)
	driver.find_element_by_xpath('//*[@id="nav-cart"]').click()
	print('On Amazon Cart')
	time.sleep(1.5)
	driver.find_element_by_xpath('//*[@id="sc-alm-buy-box-ptc-button-VUZHIFdob2xlIEZvb2Rz"]/span/input').click()
	print('On Amazon Checkout')
	time.sleep(1.5)
	driver.find_element_by_xpath('// *[ @ id = "a-autoid-0"] / span / a').click()
	print('On Amazon Checkout Following')
	time.sleep(1.5)
	print('on substitution page')
	driver.find_element_by_xpath('//*[@id="subsContinueButton"]/span/input').click()
	time.sleep(1.5)
	
	return driver


def check_slots(driver, is_slot, c):
	# increase count
	c += 1
	# refresh the page
	driver.refresh()
	
	html = driver.page_source
	soup = bs4.BeautifulSoup(html, "html.parser")
	
	# first try by finding the "not available" text
	try:
		slot_opened_text = "Not available"
		
		all_dates = soup.findAll("div", {"class": "ufss-date-select-toggle-text-availability"})
		for each_date in all_dates:
			if slot_opened_text not in each_date.text:
				print('SLOTS OPEN !')
				is_slot = True
	except AttributeError:
		pass
	# print('first try done')
	
	if is_slot == True:
		# exit the code
		return is_slot, c
	# else pursue another trial to find slots
	try:
		# this is the list of all the alert messages possible
		alert_messages = soup.findAll('h4', class_='a-alert-heading')
		# convert the list of bs4 object to text
		alert_messages_text = []
		for alert_message in alert_messages:
			alert_messages_text.append(alert_message.text)
		
		# sentence if there is no slot available
		# this is the sentence we try to find
		no_slot_pattern = 'No delivery windows available. New windows are released throughout the day.'
		
		if no_slot_pattern in alert_messages_text:
			print("NO SLOTS AVAILABLE!")
	
	except AttributeError:
		print('SLOTS OPEN 2!')
		
		is_slot = True
	# print('second try done')
	if is_slot:
		# exit the code
		return is_slot, c
	
	return is_slot, c


def loop_slot_check(driver, credentials):
	# initiate counter
	c = 0
	# initiate the is_slot variable
	is_slot = False
	# refresh waiting time if no slot is available
	time_no_slot = credentials['wholefoods']['time_no_slot']
	# refresh time if a slot is available
	time_slot = credentials['wholefoods']['time_slot']
	# sound parameter
	sound_no_slot = ast.literal_eval(credentials['wholefoods']['sound_no_slot'])
	sound_slot = ast.literal_eval(credentials['wholefoods']['sound_slot'])
	
	while not is_slot:
		print('Refresh driver:', c, '-th time. ', end='')
		is_slot, c = check_slots(driver, is_slot, c)
		if not is_slot:
			if sound_no_slot:
				message = credentials['wholefoods']['text_no_slot']
				os.system('say "{}"'.format(message))
			time.sleep(time_no_slot)
		else:
			if sound_slot:
				message = credentials['wholefoods']['text_slot']
				os.system('say "{}"'.format(message))
			# push the notification on slack
			# create the slack bot to send message on slack
			slack = sb.create_bot(credentials)
			# send the message on slack
			channel = credentials['wholefoods']["channel"]
			message = credentials['wholefoods']['text_notification']
			sb.post_message(message, channel, credentials, slack)
			time.sleep(time_slot)

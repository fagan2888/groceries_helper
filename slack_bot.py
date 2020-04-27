from slacker import Slacker
import json




def create_bot(credentials):
	slack_api_token = credentials['slack_api_token']
	# instantiate the connection to workspace
	slack = Slacker(slack_api_token)
	return slack


def test_connectivity(slack):
	# Check for success
	if slack.api.test().successful:
		print(
			f"Connected to {slack.team.info().body['team']['name']}.")
	else:
		print('Try Again!')


def post_message(message, channel, credentials, slack):
	username = credentials[channel]['username']
	icon_emoji = credentials[channel]['icon_emoji']
	
	slack.chat.post_message(channel=channel,
	                        text='<!everyone> *{}*'.format(message),
	                        username=username,
	                        icon_emoji=icon_emoji)
	print('sent: ', message)




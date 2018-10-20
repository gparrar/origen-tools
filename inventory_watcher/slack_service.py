from slackclient import SlackClient

SLACK_TOKEN = 'xoxp-245385053858-244739387712-340297854678-f7a0e2fdafb4f5d655928286ab018010'

def send_slack_message(message, channel):
    sc = SlackClient(SLACK_TOKEN)
    sc.api_call(
      "chat.postMessage",
      channel=channel,
      text=message
    )

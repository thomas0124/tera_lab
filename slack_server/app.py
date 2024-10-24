from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
import json
import os
from datetime import datetime

app = Flask(__name__)

SLACK_TOKEN = os.environ["SLACK_TOKEN"]
client = WebClient(token=SLACK_TOKEN)
signature_verifier = SignatureVerifier(os.environ['SLACK_SIGNING_SECRET'])

server_machines = ["Server A", "Server B", "Server C"]
members = ["User1", "User2", "User3"]
usage_log = []

@app.route('/slack/events', methods=['POST'])
def handle_slack_events():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return jsonify({'status': 'invalid request'}), 400

    data = request.json
    event_type = data.get('event', {}).get('type')

    if event_type == 'app_mention':
        command = data['event']['text'].strip()
        if command == '/start-server':
            show_server_selection(data['event']['channel'])
        elif command == '/end-server':
            show_server_selection(data['event']['channel'])

    return jsonify({'status': 'ok'})

def show_server_selection(channel):
    options = [{'text': {'type': 'plain_text', 'text': server}, 'value': server} for server in server_machines]
    response = client.views_open(
        trigger_id=channel,
        view={
            "type": "modal",
            "callback_id": "server_selection",
            "title": {"type": "plain_text", "text": "Select Server"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "server_block",
                    "label": {"type": "plain_text", "text": "Choose a server"},
                    "element": {
                        "type": "static_select",
                        "action_id": "server_select",
                        "options": options
                    }
                },
                {
                    "type": "input",
                    "block_id": "member_block",
                    "label": {"type": "plain_text", "text": "Select Member"},
                    "element": {
                        "type": "static_select",
                        "action_id": "member_select",
                        "options": [{'text': {'type': 'plain_text', 'text': member}, 'value': member} for member in members]
                    }
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Submit"},
                    "action_id": "submit_selection"
                }
            ]
        }
    )

@app.route('/slack/actions', methods=['POST'])
def handle_actions():
    payload = json.loads(request.form['payload'])
    actions = payload['actions']
    channel_id = payload['channel']['id']
    user = payload['user']['name']

    if payload['type'] == 'view_submission':
        server = payload['view']['state']['values']['server_block']['server_select']['selected_option']['value']
        member = payload['view']['state']['values']['member_block']['member_select']['selected_option']['value']
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        usage_log.append({
            "user": user,
            "server": server,
            "start_time": start_time
        })
        notify_usage_start(user, server, start_time)

    return jsonify({'status': 'ok'})

def notify_usage_start(user, server, start_time):
    message = f"<@{user}> has started using {server} at {start_time}."
    client.chat_postMessage(channel='your-channel-id', text=message)

if __name__ == '__main__':
    app.run(port=3000)

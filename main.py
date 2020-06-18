# Copyright 2019 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The code in this module is based on
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/run/pubsub/main.py.
# See https://cloud.google.com/run/docs/tutorials/pubsub for the accompanying
# Cloud Run/PubSub solutions guide.

"""Runs Cloud Monitoring Notification Integration app with Flask."""

# [START run_pubsub_server_setup]
import os
import json

from flask import Flask, request
from dotenv import load_dotenv

import philips_hue
from config import configs
import pubsub


load_dotenv()

app = Flask(__name__)
env = os.environ.get('FLASK_APP_ENV', 'default')
app.config.from_object(configs[env])
# [END run_pubsub_server_setup]


# [START run_pubsub_handler]
@app.route('/', methods=['POST'])
def index():
    pubsub_received_message = request.get_json()

    # parse the Pub/Sub data
    try:
        pubsub_data_string = pubsub.parse_data_from_message(pubsub_received_message)
    except pubsub.DataParseError as e:
        print(e)
        return (e.message, 400)

    # load the notification from the data
    try:
        monitoring_notification_dict = json.loads(pubsub_data_string)
    except json.JSONDecodeError as e:
        msg = 'notification could not be decoded to a JSON'
        print(msg)
        return (msg, 400)


    philips_hue_client = philips_hue.PhilipsHueClient(app.config['BRIDGE_IP_ADDRESS'],
                                                      app.config['USERNAME'])

    try:
        response = philips_hue.trigger_light_from_monitoring_notification(
            philips_hue_client, monitoring_notification_dict, app.config['LIGHT_ID'])
    except philips_hue.Error as e:
        print(e)
        return (e.message, 400)


    return (response.text, 200)
# [END run_pubsub_handler]


if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
import json
import arrow

#URL to data publication in server
pub_url = 'https://data.demo.konkerlabs.net/pub/'
#Url of API
base_api = 'https://api.demo.konkerlabs.net'
#Application deafault
application = 'default'

# Replace with login `username` and `password` with the credentials that you obtained when you registered your application with Konker.
username = 'projetos.vision.ai@gmail.com'
password = '#python%SI98'


# Create the Konker OAuth2 client object.
client = BackendApplicationClient(client_id=username)

# Create the OAuth2 session object.
oauth = OAuth2Session(client=client)


def find_all_devices():
    devices = oauth.get("https://api.demo.konkerlabs.net/v1/{}/devices/".format(application)).json()
    return devices['result']

def find_device_by_name(device_name):
  devices = find_all_devices()
  guid_term=""
  for dev in devices:
      if dev['name'] == device_name:
          guid_term = dev['guid']

  return guid_term

def print_json(inp):

    output = json.dumps(inp, indent=2)

    line_list = output.split("\n")  # Sort of line replacing "\n" with a new line

    # Now that our obj is a list of strings leverage print's automatic newline
    for line in line_list:
        print(line)


def fetch_connection_konker(return_token=False):
    # Try to fetch the Konker OAuth2 access token.
    try:
        token = oauth.fetch_token(token_url=f'{base_api}/v1/oauth/token',
                                client_id=client.client_id,
                                client_secret=password)
    except MissingTokenError as e:
        # If the fetch_token() method raises a MissingTokenError exception, try the following troubleshooting steps:
        # 1. Make sure that you are using the correct client ID and client secret.
        # 2. Make sure that you are using the correct token URL.
        # 3. Try restarting the Konker OAuth2 server.
        # 4. Contact Konker support for assistance.
        print("Error fetching Konker OAuth2 access token:", e)
    else:
        # If the fetch_token() method succeeds, use the access token to make authenticated requests to the Konker API.
        print("Successfully fetched Konker OAuth2 access token!")
        
        if return_token:        
            return token
    

def get_data_from_channel(channel, device_name, shift_days=-1):
    guid_term = find_device_by_name(device_name)

    utc = arrow.utcnow()
    utc = utc.to('America/Sao_Paulo') # or 'local'
    #print(utc.format())
    #dt_start = utc.floor(
        #'day'
    #)
    #dt_start = dt_start.shift(days=shift_days)
    uri = "https://api.demo.konkerlabs.net/v1/{}/incomingEvents?q=device:{} channel:{}" #timestamp:>{}&sort=oldest&limit=10000"
    stats = oauth.get(uri.format(application,
                                 guid_term,
                                 channel,
                                 #dt_start.isoformat()
                                 #utc.isoformat()

                                 ))
    stats = stats.json()
    return stats



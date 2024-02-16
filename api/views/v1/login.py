from oauthlib.oauth2 import WebApplicationClient as WAC
import requests
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from rest_framework.response import Response

def login(request):
    clientID = '43241fcee91b3eb3cd53'
    client = WAC(clientID)
    
    authorization_url = 'https://github.com/login/oauth/authorize'
    
    
    url = client.prepare_request_uri(
        authorization_url,
        redirectURL = 'http://127.0.0.1:8000',
        scope =[],
        state = '1234-zyxa-9134-wpst'
    )
    
    return Response(url)

class Callback():
    def get(self, request):
        data = self.request.GET
        authcode = data['code']
        state = data['state']
        print(authcode)
        print(state)
        
        #Get API token
        
        token_url = 'https://github.com/login/oauth/access_token'
        clientID = '43241fcee91b3eb3cd53'
        clientSecret = '73931e1ea1bf97ccfd52d92560dd7ffa15857f99'
        
        client = WAC(clientID)
        
        data = client.prepare_request_body(
            code = authcode,
            redirect_uri = 'http://127.0.0.1:8000',
            client_id = clientID,
            client_secret = clientSecret
        )
        
        response = requests.post(token_url, data = data)
        
        client.parse_request_body_response(response.text)
        
        header = {'Authorization': 'token {}'.format(client.token['access_token'])}
        
        response = requests.get('https://api.github.com/user', headers=header)
        
        json_dict  = response.json()
        
        print(json_dict['email'])
    
        
        
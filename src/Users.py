import urllib, urllib2, socket, cookielib, requests 
from requests.auth import AuthBase
import json
import re

class KongUser:
	USER_INFO_URL = 'http://www.kongregate.com/api/user_info.json?username='
	ACCOUNT_URL = 'http://www.kongregate.com/accounts/'

	def __init__(self, username):
		self._username = username
		self._session = requests.Session()
	
	# Return username
	def username(self):
		return self._username
	
	# Return user info
	def userInfo(self):
		return self._userInfo
	
	# Get user info (without auth)
	def loadInfo(self):
		url = KongUser.USER_INFO_URL + self.username()
		req = self._session.get(url)
		self._userInfo = req.json()
		return self._userInfo
	
	# Get instance profile shouts
	def getShouts(self, params=None):
		if params == None:
			params = {'format': 'json'}

		url = KongUser.ACCOUNT_URL + self.username() + '/messages.json'
		req = self._session.get(url, params=params)
		return req.json()
		
class KongAuthUser(KongUser):
	HTML_SCRAP_URL = 'http://www.kongregate.com/community'
	LOGIN_URL = 'https://www.kongregate.com/session'
		
	# Log the user, provided a password, and creates a new Kongregate session
	def login(self, password):
		self._authToken = self.__getAuthToken()
		
		data = {
			'utf8': '%E2%9C%93',
			'authenticity_token': self._authToken,
			'from_welcome_box': 'false',
			'username': self.username(),
			'password': password
		}
		
		resp = self._session.post(KongAuthUser.LOGIN_URL, data=data)
		return resp.json()
	
	# Retrieve the authenticity token
	def __getAuthToken(self):
		conn = self._session.get(KongAuthUser.HTML_SCRAP_URL)
		response = conn.text
		m = re.search('<meta content="(.*)" name="csrf-token"', response)
		return m.group(1)
		
	# Send a shout
	def shout(self, to, msg):
		url = KongUser.ACCOUNT_URL + to + '/messages.json'
		data = 'utf8=%E2%9C%93&authenticity_token='\
				+ self._authToken + '&shout%5Bcontent%5D='\
				+ msg + '&_='
				
		self._session.headers.update({
			'X-Requested-With': 'XMLHttpRequest',
			'X-Prototype-Version': '1.7_rc3',
			'X-CSRF-Token': self._authToken,
			'Content-Length': len(data)
		})
		
		resp = self._session.post(url, data=data)
		return resp.text
	
	# Send a whisper
	def whisper(self, to, msg):
		url = KongUser.ACCOUNT_URL + to + '/messages.json'
		data = 'utf8=%E2%9C%93&authenticity_token='\
				+ self._authToken + '&shout%5Bprivate%5D=true'\
				+'&shout%5Bcontent%5D=' + msg
				
		self._session.headers.update({
			'X-Requested-With': 'XMLHttpRequest',
			'X-Prototype-Version': '1.7_rc3',
			'X-CSRF-Token': self._authToken,
			'Content-Length': len(data)
		})
		
		resp = self._session.post(url, data=data)
		return resp.text
		
	# Get user whispers
	def getWhispers(self, params=None):
		if params == None:
			params = {'format': 'json', 'authenticity_token': self._authToken}

		url = KongUser.ACCOUNT_URL + self.username() + '/private_messages.json'
		req = self._session.get(url, params=params)
		return req.json()
		
	# Get whispers sent and recieved with another username
	def getWhispersWith(self, username, params=None):
		if params == None:
			params = {'format': 'json', 'authenticity_token': self._authToken}
			
		url = KongUser.ACCOUNT_URL + username + '/private_messages.json'
		req = self._session.get(url, params=params)
		return req.json()
	
	# Get user messages sent
	def getSentMessages(self, params=None):
		if params == None:
			params = {'format': 'json', 'authenticity_token': self._authToken}
			
		url = KongUser.ACCOUNT_URL + self.username() + '/sent_messages.json'
		req = self._session.get(url, params=params)
		return req.json()



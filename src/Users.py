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
		self.loadInfo()
	
	# Return username
	def username(self):
		return self._username
	
	# Return user info
	def userInfo(self):
		return self._userInfo
		
	def userId(self):			
		return self.userInfo()['user_id']
	
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
	
	# Get user's badges
	def getBadges(self):
		url = KongUser.ACCOUNT_URL + self.username() + '/badges.json'
		req = self._session.get(url)
		return req.json()
		
class KongAuthUser(KongUser):
	HTML_SCRAP_URL = 'http://www.kongregate.com/community'
	LOGIN_URL = 'https://www.kongregate.com/session'
	GAME_RATING_URL = 'http://www.kongregate.com/game_ratings.json'
		
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
		
	# Set the header to send a post request
	def __setHeader(self, data):
		self._session.headers.update({
			'X-Requested-With': 'XMLHttpRequest',
			'X-Prototype-Version': '1.7_rc3',
			'X-CSRF-Token': self._authToken,
			'Content-Length': len(data)
		})
		
	# Send a shout
	def shout(self, to, msg):
		url = KongUser.ACCOUNT_URL + to + '/messages.json'
		data = 'utf8=%E2%9C%93&authenticity_token='\
				+ self._authToken + '&shout%5Bcontent%5D='\
				+ msg + '&_='
		
		self.__setHeader(data)
		
		resp = self._session.post(url, data=data)
		return resp.text
	
	# Send a whisper
	def whisper(self, to, msg):
		url = KongUser.ACCOUNT_URL + to + '/messages.json'
		data = 'utf8=%E2%9C%93&authenticity_token='\
				+ self._authToken + '&shout%5Bprivate%5D=true'\
				+'&shout%5Bcontent%5D=' + msg
		
		self.__setHeader(data)
		
		resp = self._session.post(url, data=data)
		return resp.text
	
	# Deletes a message by ID in the specified profile
	def deleteMessage(self, msgId, username=None):
		if username == None:
			username = self.username()
			
		url = KongUser.ACCOUNT_URL + username + '/messages/' + str(msgId) + '.js'
		data = 'utf8=%E2%9C%93&authenticity_token=' + self._authToken\
				+ '&_method=delete&_='
		
		self.__setHeader(data)
		
		resp = self._session.post(url, data=data)
		return resp.text
		
	# Get user's whispers
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
	
	# Add a friend
	def friend(self, username):
		url = KongUser.ACCOUNT_URL + self.username() + '/friends/' + username
		data = 'authenticity_token=' + self._authToken + '&_method=put&_='
		url += '?friend_from=new_profile&masthead=true'
		
		self.__setHeader(data)
		
		req = self._session.post(url, data=data)
		return req.text
		
	def unfriend(self, username):
		url = KongUser.ACCOUNT_URL + self.username() + '/friends/' + username
		data = 'authenticity_token=' + self._authToken + '&_method=put&_='
		url += '?masthead=true&unfriend_from=new_profile'
		
		self.__setHeader(data)
		
		req = self._session.post(url, data=data)
		return req.text
		
	# Rate a game
	def rate(self, gameId, rating):
		data = 'user_id=' + str(self.userId()) + '&game_id=' + str(gameId)\
					+ '&rating=' + str(rating)
		
		self._session.headers.update({
			'Content-Length': len(data)
		})
		
		req = self._session.post(KongAuthUser.GAME_RATING_URL, data=data)
		return req.json()


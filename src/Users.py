import urllib, urllib2, socket, cookielib, requests 
from requests.auth import AuthBase
import json
import re

class KongUser:
        USER_INFO_URL = 'http://www.kongregate.com/api/user_info.json?username='

        def __init__(self, username):
                self._username = username

        def username(self):
                return self._username

        def userInfo(self):
                return self._userInfo
        
        def loadInfo(self):
                conn = urllib2.urlopen(KongUser.USER_INFO_URL + self.username())
                self._userInfo = json.loads(conn.read())
                return self._userInfo


class KongAuthUser(KongUser):
        HTML_SCRAP_URL = 'http://www.kongregate.com/community'
        LOGIN_URL = 'https://www.kongregate.com/session'
        ACCOUNT_URL = 'http://www.kongregate.com/accounts/'
       
	def __init__(self, username, password):
		KongUser.__init__(self, username)
		self.login(password)
		

        # Logs the user, provided a password, and creates a new Kongregate session
        def login(self, password):
                self._session = requests.Session()
                self._authToken = self.getAuthToken()
        
                data = {
                        'utf8': '%E2%9C%93',
                        'authenticity_token': self._authToken, 
                        'from_welcome_box': 'false',
                        'username': self.username(),
                        'password': password
                }
        
                resp = self._session.post(KongAuthUser.LOGIN_URL, data=data)

                return resp.json()
                
        # Shouts another user
	def shout(self, to, msg):
                url = KongAuthUser.ACCOUNT_URL + to + '/messages.json'
                
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
                        
        def whisper(self, to, msg):
                url = KongAuthUser.ACCOUNT_URL + to + '/messages.json'
                data = 'utf8=%E2%9C%93&authenticity_token=' +\
                        self._authToken + '&shout%5Bprivate%5D=true' +\
                        '&shout%5Bcontent%5D=' + msg
                
                self._session.headers.update({
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-Prototype-Version': '1.7_rc3',
                        'X-CSRF-Token': self._authToken,
                        'Content-Length': len(data)
                })
                
                resp = self._session.post(url, data=data)

                return resp.text



        def getAuthToken(self):
                conn = self._session.get(KongAuthUser.HTML_SCRAP_URL)
                response = conn.text
                m = re.search('<meta content="(.*)" name="csrf-token"', response)
                return m.group(1)



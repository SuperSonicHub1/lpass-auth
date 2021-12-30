import base64
import binascii
import hashlib
import json
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from requests import Session

BASE = "https://lastpass.com"
USER_AGENT = 'lastpass-python/{}'.format('0.3.2')

def create_default_session() -> Session:
	session = Session()
	session.headers.update({"user-agent": USER_AGENT})
	return session

class LoginException(Exception):
	pass

class LastpassAuthClient:
	def __init__(
		self,
		email: str,
		password: str,
		otp: Optional[str] = None,
		session: Session = create_default_session()
	) -> None:
		self.email = email
		self.password = password
		self.session = session
		self.authenticate(otp)

	@staticmethod
	def create_hash(username: str, password: str, iteration_count: int) -> tuple:
		key = hashlib.pbkdf2_hmac(
			'sha256',
			password.encode('utf-8'),
			username.encode('utf-8'),
			iteration_count,
			32
		)

		login_hash = binascii.hexlify(
			hashlib.pbkdf2_hmac(
				'sha256',
				key,
				password.encode('utf-8'),
				1,
				32
			)
		)

		return key, login_hash

	def iterations(self) -> int:
		url = BASE + '/iterations.php'
		params = {'email': self.email}

		res = self.session.get(
			url,
			params=params,
			verify=True,
		)

		try:
			iterations = int(res.text)
		except ValueError:
			iterations = 5000

		return iterations

	def authenticate(self, otp: Optional[int] = None) -> None:
		url = BASE + '/login.php'
		iteration_count = self.iterations()
		key, login_hash = LastpassAuthClient.create_hash(
			self.email,
			self.password,
			iteration_count
		)

		self.key = key

		data = {
			'method': 'mobile',
			'web': 1,
			'xml': 1,
			'username': self.email,
			'hash': login_hash,
			'iterations': iteration_count,
		}

		if otp:
			data.update({'otp': otp})

		res = self.session.post(
			url,
			data=data,
			verify=True
		)

		if not res.text.startswith('<ok'):
			raise LoginException(res.text)
		else:
			res = self.session.post(
				BASE + '/getCSRFToken.php',
				verify=True
			)
			self.csrf = res.text

	def backups(self) -> dict:
		# Download the user data
		url = BASE + '/lmiapi/authenticator/backup'
		headers = {
			'X-CSRF-TOKEN': self.csrf,
			'X-SESSION-ID': self.session.cookies.get("PHPSESSID"),
		}

		res = self.session.get(
        		url,
			headers=headers,
			verify=True
		)

		raw_backup = res.json()['userData']

		# Decrypt it
		data_parts = raw_backup.split('|')
		iv = base64.b64decode(data_parts[0].split('!')[1])
		ciphertext = base64.b64decode(data_parts[1])

		cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
		plaintext = unpad(
			cipher.decrypt(ciphertext),
			AES.block_size
		)

		mfa_data = json.loads(plaintext)
		return mfa_data

if __name__ == "__main__":
	import getpass
	from pprint import pprint as print

	email = input("> ")
	otp = input("> ") or None
	if otp:
		otp = int(otp)
	password = getpass.getpass()
	client = LastpassAuthClient(email, password, otp=otp)
	backups = client.backups()
	print(backups)


from .api import LastpassAuthClient
from argparse import ArgumentParser
from getpass import getpass
import json
import keyring
from pyotp import TOTP

def main():
	parser = ArgumentParser(
		prog="lpass-auth",
		description="Get authentication codes from your LastPass account.",
	)

	subparsers = parser.add_subparsers(help='Sub-command help', dest='command', required=True)

	parser_sync = subparsers.add_parser("sync", help="Sync your collection of accounts to your keychain.")
	parser_sync.add_argument("-o", "--one-time-password", dest="otp", help="Your one-time password (default: collected interactively)")
	parser_sync.add_argument("-u", "--username", help="Your email/username (default: collected interactively)")

	parser_ls = subparsers.add_parser("ls", help="View your collection of accounts.")

	parser_show = subparsers.add_parser("show", help="Show an authenication code.")

	lookup = parser_show.add_mutually_exclusive_group(required=True)
	lookup.add_argument("-s", "--issuer", help="The issuer an account belongs to.")
	lookup.add_argument("-i", "--id", help="The UUID an account belongs to.")

	parser_show.add_argument(
		"-f",
		"--format",
		help="Format this command's output using Python's format string syntax (https://docs.python.org/3/library/string.html#formatstrings); useful for command line parsing."
	)

	args = parser.parse_args()

	if args.command == "sync":
		username = args.username or input("Username: ")
		password = getpass("Master Password: ")
		otp = args.otp or input("OTP (if applicable): ")
		try:
			# Verify it's an integer but don't change anything
			int(otp)
		except ValueError:
			otp = None

		client = LastpassAuthClient(username, password, otp=otp)
		backups = client.backups()
		keyring.set_password("lpass-auth", "backups", json.dumps(backups))
		return

	backups = json.loads(keyring.get_password("lpass-auth", "backups"))
	accounts = backups["accounts"]

	HEADER_STRING="{issuerName} [id: {accountID}]"

	if args.command == "ls":
		for account in accounts:
			string = HEADER_STRING.format(**account)
			print(string)
	elif args.command == "show":
		if args.issuer:
			account = [account for account in accounts if account["issuerName"] == args.issuer][0]
		elif args.id:
			account = [account for account in accounts if account["accountID"] == args.id][0]

		password = TOTP(account['secret'].replace(' ', '')).now()
		account.update({"password": password})

		if args.format:
			print(args.format.format(**account))
		else:
			print(HEADER_STRING.format(**account))
			print("Login:",account["userName"])
			print("Password:", account["password"])

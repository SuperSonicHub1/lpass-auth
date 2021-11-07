# lpass-auth

> A [LastPass Authenticator][authenticator] client written in Python
heavily inspired by [lastpass-cli][lastpass-cli] and based on 
[code by Donny Maasland][export].

## Installation

### Git
```bash
git clone https://github.com/supersonichub1/lpass-auth
cd lpass-auth
poetry install
```

### pip
```bash
pip install -U lpass-auth
```

## Help
Run `lpass-auth --help` for the most up-to-date information.

### `show --format`
The `show` subcommand allows for the customization of the command's output
through the `--format` option, a la `lpass show --format`. 
Instead of using `printf`-like formatting, `lpass-auth` instead uses 
[Python's format string syntax][format-string], which I believe is much
more intuitive and user friendly.

The format string supplies the following values:
* accountID
* digits
* issuerName
* lmiUserId
* originaIssuerName
* originalUserName
* pushNotification
* secret
* timeStep
* userName

For example:
```bash
$ lpass-auth show --issuer LastPass \
--format "{accountID} ({login}): {password}" \
LastPass (example@example.com): 690420
```

## Caveots
* only supports no authentication or TOTP authentication; sorry Yubikey users!
* cannot add or remove passwords due to lack of API knowledge

## TODO
* error handling
* dump/export passwords a la [lastpass-authenticator-export][export]

[authenticator]: https://www.lastpass.com/solutions/authentication/two-factor-authentication
[lastpass-cli]: https://github.com/lastpass/lastpass-cli
[export]: https://github.com/dmaasland/lastpass-authenticator-export
[format-string]: https://docs.python.org/3/library/string.html#format-string-syntax

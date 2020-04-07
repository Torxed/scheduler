import json, time
from hashlib import sha512
from mailer import email

TEXT_TEMPLATE = """
Click here to download your encrypted file: https://drop-corp.hvornum.se/#download={link}.

Best wishes //Hvornum.se
"""

HTML_TEMPLATE = """
<html>
	<head>
		<title>Secure download link</title>
	</head>
	<body>
		<div>
			<p>
				Click here to download your encrypted file: <a href="https://drop-corp.hvornum.se/#download={link}">https://drop-corp.hvornum.se/#download={link}</a>
			</p>
			<br>
			<p>
				Best wishes //Hvornum.se
			</p>
		</div>
	</body>
</html>
"""

class parser():
	def process(path, client, data, headers, fileno, addr, *args, **kwargs):
		_id_ = gen_id()
	#	mail_config = {
	#		'SSH_MAIL_USER_FROM' : 'no-reply', # without @
	#		'SSH_MAIL_USER_FROMDOMAIN' : 'hvornum.se', # without @
	#		'SSH_MAIL_USER_TO' : recipient.split('@',1)[0],
	#		'SSH_MAIL_USER_TODOMAIN' : recipient.split('@',1)[1],
	#		'RAW_TIME' : time.time(),
	#		'SUBJECT' : f'Secure download link',
	#		'TRY_ONE_MAILSERVER' : False,
	#		'TEXT_TEMPLATE' : TEXT_TEMPLATE.format(link=mapped_transfer_ids[_REQUEST_MAP]),
	#		'HTML_TEMPLATE' : HTML_TEMPLATE.format(link=mapped_transfer_ids[_REQUEST_MAP]),
	#		'DKIM_KEY' : "/etc/sshmailer/sshmailer.pem",
	#		'SIGN_DOMAIN' : 'obtain.life'
	#	}
	#	email(mail_config)

		return {'status' : 'success'}


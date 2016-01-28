

SMSserver

Author: Bernhard Erren bernhard.erren@googlemail.com URL: https://github.com/pjfrey3000/SMSserver

Many thanks to Stuart Rackham, srackham@gmail.com for the clickatell library.

SMSserver fetches emails from a POP3 account, parses the content and creates a request for Clickatel for SMS sending. The result is mailed to the sender of the email request.

The configuration file is a json file:

{

"USERNAME": "your clickatell username",

"PASSWORD": "your clickatell password",

"API_ID": "the http api id",

"SENDER_ID": "+4412312345678",

"PHONE_BOOK": {

"myself":   "4412334567890"

},

"ALLOWED_RECIPIENT": {

"smsmaker@wahtever.com": "smsmaker@whatever.com"

},

"ALLOWED_SENDER": {

"first.user@domain.com": "first.user@domain.com",

"second.user@domain.com": "second.user@domain.com",

"third.user@domain.com": "third.user@domain.com",

"fourth.user@domain.com": "fourth.user@domain.com"

},

"MAILUSER": "your email user",

"MAILPASS": "your email password",

"MAILHOST": "your pop3 server",

"MAILPORT": "110",

"MAILTIME": "240",

"POPLOOP": "300",

"SMTPUSER": "your smtp user",

"SMTPPASS": "your smtp password",

"SMTPHOST": "your smtp server",

"SMTPSENDER": "the sender of the ack email",

"SMTPPORT": "25",

"SMTPTIME": "240"

}

You can define a set ofallowed recipients of the email (usually the email address of the POP3 account receiving the email requests) and a set of allowed sender email addresses.

The recipients phone number has to be in the subject line, i.e. 4412334567890, preceded by a + or not. You may also provide a name which is contained in the section PHONE_BOOK of the json.

The subject of the email is ignored. The content is sent as the SMS text.


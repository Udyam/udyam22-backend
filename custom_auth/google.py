from email.mime.text import MIMEText
from datetime import datetime
import base64
from googleapiclient import errors
import os
import oauth2client
from oauth2client import client, tools, file


SCOPES = "https://www.googleapis.com/auth/gmail.send"
CLIENT_SECRET_FILE = "credentials.json"
APPLICATION_NAME = "Udyam Backend"

part1 = """<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verification</title>
    <style>
    div{
        border: 2px solid black;
        text-align: center;
    }
    h1{
        background-color: black;
        color:rgb(55, 199, 204);
        font-size: 40px;
        margin-top: 0px;
    }
    h3{
        font-weight: 100;
    }
    a{
        background-color: blue;
        border-radius: 10px;
        font-size: 18px;
        color: rgb(248, 240, 240)!important;
        text-decoration: none;
        padding: 5px 10px;
        font-weight: 600;
    }
    </style>
</head>
<body>
    <div>
    <h1>UDYAM22</h1>
    <h3>Hi """

part2 = """!</h3><h3>"""
part3 = """</h3>
    <a href='"""
part4 = (
    """'>Verify Now</a>
    <h3>Please ignore if not filled by you.</h3>
    </div>
    <span style="color: #FFF; display: none; font-size: 8px;">"""
    + str(datetime.now())
    + """</span>
</body>
</html>"""
)


class gmail:
    def get_credentials():
        home_dir = os.path.expanduser("~")
        credential_dir = os.path.join(home_dir, ".credentials")
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, "gmail-python-email-send.json")
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print("Storing credentials to " + credential_path)
        return credentials

    def create_message(sender, to, subject, message_text):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject
        return {"raw": base64.urlsafe_b64encode(message.as_bytes())}

    def create_draft(service, user_id, message_body):
        """Create and insert a draft email. Print the returned draft's message and id.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message_body: The body of the email message, including headers.

        Returns:
          Draft object, including draft id and message meta data.
        """
        try:
            message = {"message": message_body}
            draft = (
                service.users().drafts().create(userId=user_id, body=message).execute()
            )

            print("Draft id: " + draft["id"] + "Draft message: " + draft["message"])

            return draft
        except errors.HttpError as error:
            print("An error occurred: " + error)
            return None

    def send_message(service, user_id, message):
        """Send an email message.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (
                service.users().messages().send(userId=user_id, body=message).execute()
            )
            print("Message Id: " + message["id"])
            return message
        except errors.HttpError as error:
            print("An error occurred: " + error)

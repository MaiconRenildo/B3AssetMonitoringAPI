import os,dotenv
dotenv.load_dotenv(dotenv.find_dotenv())


def send(to:str,subject:str,msg:str):
    from email.message import EmailMessage
    import smtplib

    email = EmailMessage()

    email['From'] = os.getenv("EMAIL_SENDER_NAME") + " <" + os.getenv("EMAIL_SENDER_EMAIL") + ">"
    email['Subject'] = subject
    email['To'] = to

    email.set_content(msg)

    with smtplib.SMTP(os.getenv("EMAIL_HOST"),int(os.getenv("EMAIL_PORT"))) as server:
        server.login(os.getenv("EMAIL_LOGIN"),os.getenv("EMAIL_PASSWORD"))
        return server.send_message(email)


def is_valid(email:str):
    import re
    regex_result = re.match(r'^([a-z]){1,}([a-z0-9._-]){1,}([@]){1}([a-z]){2,}([.]){1}([a-z]){2,}([.]?){1}([a-z]?){2,}$',email)
    return True if regex_result else False
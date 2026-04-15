from celery import Celery # class to create c_app instance
from src.mail import mail, create_message
from asgiref.sync import async_to_sync

c_app = Celery()

c_app.config_from_object("src.config")




@c_app.task() # worker doing task of sending emails
def send_email(recipients: list[str], subject: str, body: str): #we saw this earlier

    message = create_message(recipients=recipients, subject=subject, body=body)
# create_message is another func used here
    async_to_sync(mail.send_message)(message) # this is where we mostly change, it was await send_message(message) in normal
    # in bgtask we did not await, we did bgtask.add_task(mail.send_message, message)
    # async_to_sync(function from 'ASGIRef'=import it) allows us to execute the async mail.send_message method in a synchronous context, making it compatible with Celery tasks.

    print("Email sent")
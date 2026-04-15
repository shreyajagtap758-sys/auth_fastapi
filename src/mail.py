# me verification bhej sakti hu password reset krne through user email
# fastmail engine he mail send krne ka,backgorundtask bas mail ko fast send krta await kiye bina
#fastmail ek package he= install kro pehle


from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.config import Config
from pathlib import Path # python tool file/folder handle krne

#base dir = jaha ye mail.py he uska folder
BASE_DIR = Path(__file__).resolve().parent # Path(__file__)= curr file ka path(src/mail.py)
#.resolve() path banata he src/mail.py se sidha C:/Users/Admin/project/src/mail.py ye kr dega
#.parent curr file ka folder deta= project/src

mail_config = ConnectionConfig(  #
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_FROM_NAME = Config.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS  = False,
    USE_CREDENTIALS  = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = Path(BASE_DIR, 'templates') #ye rha base dir src/templates
) # templlate file me apan har html code likh denge jo route se ara(email design)


mail = FastMail(  # ready-made email sender engine
    config = mail_config
)

def create_message(recipients : list[str], subject : str, body : str):

    message = MessageSchema(  # email ka structure jo hum route me pass krenge
        recipients = recipients,
        subject = subject,
        body = body,
        subtype = MessageType.html  #ye body ka hi type btayega=html he
    )

    return message

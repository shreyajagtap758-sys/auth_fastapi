from fastapi import APIRouter, Depends, status

from src.config import Config
from src.exceptions.auth.exceptions import UserNotFound
from .schemas import UserCreateModel, UserLoginModel, UserBooks, EmailModel
from .service import UserService
from src.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token, verify_password, create_url_safe_token, decode_url_safe_token, generate_passwd_hash
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from .dependencies import refreshtokenbearer, accesstokenbearer, get_current_user, rolechecker
from src.db.redis import add_jti_to_blocklist
from src.exceptions.auth.exceptions import UserAlreadyExists, InvalidCredentials, InvalidToken
from src.auth.schemas import PasswordReset, PasswordResetConfirm
from fastapi import BackgroundTasks
from src.celery_tasks import send_email

from src.mail import mail, create_message


auth_router = APIRouter() # route for auth file
user_service = UserService()  # userservice() from service file to use here
role_checker = rolechecker(['admin', "user"])


# bgtask= servercrash=taskgone,highload=cant handle,its sync like infrastructure
# use= task tiny, it can fail

# celery= survive server restart,handle high load, its async processing
# use= task is important(payment,email), task slow/heavy, retry may happen(time consuming operations)


#1= celery client: ye ek python function hi he jisme operations jese send email,data process, interact with other api.
#2= broker: works as message queue jo celery client(task banata) or workers(task execute) ke bich rehta.
# The broker holds tasks until they are picked up by a worker. Celery supports various brokers, with RabbitMQ and Redis
#3= worker:  process that runs in the background and is responsible for executing tasks
# Celery can manage multiple workers simultaneously, even across different machines
#4= result: Once a worker completes a task, its result is stored in the result backend. This is an optional component that keeps track of task outcomes, allowing you to check task status and retrieve results later
#  Common backends include Redis, RabbitMQ, or databases like PostgreSQL


REFRESH_TOKEN_EXPIRY=True

#req ai- schema validate- email extract- message bana- send trigger
@auth_router.post('/send_mail')
async def send_mail(emails: EmailModel):

    recipients = emails.addresses

    html = "<h1>Welcome to the app</h1>"

    subject = "Welcome to our app"

    #message = create_message(
    #    recipients=recipients,  #addressess honge
    #    subject="Welcome",  # ye dikhega
    #    body=html  # html body me dikhega
    #)

    #await mail.send_message(message)

    send_email.delay(recipients, subject, html)
    return {"message": "Email queued successfully"}


@auth_router.post(
    '/signup',
    status_code=status.HTTP_201_CREATED,
)
async def create_user_account(
        user_data: UserCreateModel,
        session:AsyncSession = Depends(get_session),
        bg_tasks = BackgroundTasks
):
    email = user_data.email # see if user already exist using same email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})


    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    subject = "verify your email"

    #message = create_message(
        #recipients=[email],
        #subject="verify your email",
        #body=html_message
    #)  # celeryme already ye input leliya to function call hote hi ye info chale jayegi udhr, no need for create_message here

# await mail.send_message(message) ye time leta he execute krne me, to apan bgtask use krte fast banane(non-bloacking)
# ye imidiate answer deta jese create user ka data send kr dega immidiate while link send hori hogi in background

    #bg_tasks.add_task(mail.send_message, message)

    # ab apun celery use krega
    send_email.delay(email, subject, html_message)


    return {
        "message" : "Account created! check email to verify your account",
        "user": new_user
    }


@auth_router.get('/verify/{token}')
async def verify_user_acct(token:str, session : AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    if not token_data:
        return JSONResponse(
            content={"message": "Invalid or expired token"},
            status_code=400
        )

    user_email = token_data.get('email')
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        await user_service.update_user(user, {'is_verified': True}, session)

        return JSONResponse(
            content={
                "message": "account verified successfully"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(content={
        "message": "error during verification"
    }, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post('/login')
async def login_users(
        login_data: UserLoginModel, session:AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user  = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.hashed_password)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    "role": user.role
                }
            )
            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )


    raise InvalidCredentials()

@auth_router.get('/refresh_token')  # depends(refre..()) calls the __call__ method in refre.. it reads token, decode jwt to token_data, verify refresh token, valid
async def get_new_access(token_detail : dict= Depends(refreshtokenbearer())):
# access expiry of token, if expired then create new access token
    expiry_timestamp = token_detail['exp']  # take token expiry
# refresh token has longer time to get expired like days, within those days user gets the new access toke, else error comes that refresh is expired
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():   # fromtimestamp convert numeric to python object
        new_access_token = create_access_token(  # call to jwt access token for new access token
            user_data=token_detail['user']
        )
        return JSONResponse(content={  #return json to user with new access token
            "access_token": new_access_token
        })

    raise InvalidToken # if token expired, user must login again

@auth_router.get('/me', response_model=UserBooks)  # user ka token verify, check user role, _ just validation
async def current_user(user = Depends(get_current_user), _: bool=Depends(role_checker)):

    return {"user" : user, "books" : user.books, "reviews": user.reviews}

@auth_router.get('/logout')
async def revoke_token(token_details: dict=Depends(accesstokenbearer())):

    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "logged out successfully"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/password_reset_request')
async def password_reset_request(email_data : PasswordReset):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password_reset_confirm/{token}"

    html = f"""
        <h1>reset your password</h1>
        <p>Please click this <a href="{link}">link</a> to reset your password</p>
        """

    subject = "verify your email"

    send_email.delay(email, subject, html)

    return JSONResponse(
        content={
            "message" : "please check your email for instructions to reset your password"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/password_reset_confirm/{token}')
async def confirm_password(token:str, passwords : PasswordResetConfirm, session:AsyncSession=Depends(get_session)):

    new_password = passwords.new_password

    if new_password != passwords.confirm_new_password:
        raise HTTPException(detail="passwords do not match!", status_code=status.HTTP_400_BAD_REQUEST)

    token_data = decode_url_safe_token(token)

    if not token_data:
        return JSONResponse(
            content={"message": "Invalid or expired token"},
            status_code=400
        )

    user_email = token_data.get('email')

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        pass_hash = generate_passwd_hash(new_password)
        await user_service.update_user(user, {"hashed_password": pass_hash}, session)

        return JSONResponse(
            content={
                "message": "password reset success"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(content={
        "message": "error during password reset"
    }, status_code = status.HTTP_500_INTERNAL_SERVER_ERROR)

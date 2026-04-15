# user request-> middleware request-> handlers
# handlers response-> middleware response-> user
# ye kaam ata he logging krne , mtlab user ka kaam pehla step route pe request jaati
#toh route tk pohchne se pehle hi decide ye krega ki user allowed he ya trusted he
# fail hua to agge jayega warna block ho jayega
# eg= user bina token banking system pr transfer money hit kre,
#agar middleware nhi he to route tk jayega thoda chalega fir error(risk), lekin middleware pehle hi dekehega hi allow kre ya nai
#agar 1000 fake req ai, db call processing sb route krega heavy, middle ware ye bacha lega


from fastapi import FastAPI, Request, status
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app:FastAPI):


    @app.middleware('http')
    async def custom_logging(request: Request, call_next): # koi req hit hogi to terminal me kya chalega wo dikhayega
        start_time = time.time() # current time

        response = await call_next(request)

        processing_time = time.time() - start_time # kitna time laga process hone
# database file me echo bandh kr diya to ab full message terminal me apna jayega ye wala
        # request bhejne wale clinet ki details, fir method(get/post), fir path(/books/auth), fir response status(500,200), or jitne time me ye sb process hua wo humne diya

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"
        print("processed after", processing_time)

        print(message)

        return response


# corsemiddleware : kisi b browser me frontend backend ko direct call nhi kr sakta, warna block by cors policy
# backend browser ko permission deta he konsi website ko allow he(browser access security)

    app.add_middleware(
        CORSMiddleware,
        allow_origins = ["*"], # only for learning
        allow_methods = ["*"],
        allow_headers = ["*"],
        allow_credentials = True
    )

#attackers fake domain se req bhej sakte, toh ytrusted host sirf allowed domain ko accept krega
# mtlab kon mere server pr anne allowed he(server domain security)

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts = ["localhost", "127.0.0.1"]
    )


import os
from datetime import datetime

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
from fastapi import Request


from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware


from apps.jwt import create_refresh_token
from apps.jwt import create_token
from apps.jwt import CREDENTIALS_EXCEPTION
from apps.jwt import decode_token
from apps.jwt import valid_email_from_db
# Create the auth app

from dotenv import load_dotenv
load_dotenv()

auth_app = FastAPI()

# @app.post("/cr")

# @auth_app.get('/login', tags=['authentication'])  # Tag it as "authentication" for our docs 
# async def login(request: Request):    # Redirect Google OAuth back to our application    
#     redirect_uri = request.url_for('auth')
#     return await oauth.google.authorize_redirect(request, redirect_uri)



# @auth_app.route('/login')
# async def login(request: Request):
#     # redirect_uri = FRONTEND_URL  # This creates the url for our /auth endpoint
#     # return await oauth.google.authorize_redirect(request, redirect_uri)

#     # google = oauth.create_client('google')
#     redirect_uri = request.url_for('auth')
#     return await oauth.google.authorize_redirect(request, redirect_uri)


# @auth_app.route('/token')
# async def auth(request: Request):
#     try:
#         access_token = await oauth.google.authorize_access_token(request)
#     except OAuthError:
#         raise CREDENTIALS_EXCEPTION
#     user_data = await oauth.google.parse_id_token(request, access_token)
#     if valid_email_from_db(user_data['email']):
#         return JSONResponse({
#             'result': True,
#             'access_token': create_token(user_data['email']),
#             'refresh_token': create_refresh_token(user_data['email']),
#         })
#     raise CREDENTIALS_EXCEPTION


# @auth_app.post('/refresh')
# async def refresh(request: Request):
#     try:
#         # Only accept post requests
#         if request.method == 'POST':
#             form = await request.json()
#             if form.get('grant_type') == 'refresh_token':
#                 token = form.get('refresh_token')
#                 payload = decode_token(token)
#                 # Check if token is not expired
#                 if datetime.utcfromtimestamp(payload.get('exp')) > datetime.utcnow():
#                     email = payload.get('sub')
#                     # Validate email
#                     if valid_email_from_db(email):
#                         # Create and return token
#                         return JSONResponse({'result': True, 'access_token': create_token(email)})

#     except Exception:
#         raise CREDENTIALS_EXCEPTION
#     raise CREDENTIALS_EXCEPTION

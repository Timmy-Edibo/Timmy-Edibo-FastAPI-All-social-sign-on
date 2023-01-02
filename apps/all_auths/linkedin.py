# Imports
from fastapi import APIRouter, Depends, HTTPException

from apps.jwt import create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES

from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse


from apps import models
from apps.database import get_db, engine
from sqlalchemy.orm import Session
models.Base.metadata.create_all(bind=engine)

import oauthlib, requests_oauthlib
from authlib.integrations.starlette_client import OAuth

linkedin_route = APIRouter(tags=['linkedin_auth'])


import os
from dotenv import load_dotenv
load_dotenv()


from requests_oauthlib import OAuth2Session

# Set environment variables
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Credentials you get from registering a new application
LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET')
LINKEDIN_SCOPE = ['r_liteprofile', 'r_emailaddress']
LINKEDIN_AUTHORIZATION_BASE_URL =os.environ.get('LINKEDIN_AUTHORIZATION_BASE_URL')
LINKEDIN_TOKEN_URL = os.environ.get('LINKEDIN_TOKEN_URL')
LINKEDIN_GET_USER_INFO = os.environ.get('LINKEDIN_GET_USER_INFO')
LINKEDIN_REDIRECT_URL = os.environ.get('LINKEDIN_REDIRECT_URL')

if LINKEDIN_CLIENT_ID is None or  LINKEDIN_CLIENT_SECRET is None or LINKEDIN_AUTHORIZATION_BASE_URL is None or LINKEDIN_TOKEN_URL is None:
    print("Enviroment variables not been loaded ")

@linkedin_route.get('/linkedin', tags=['authentication'])  # Tag it as "authentication" for our docs
async def login(request: Request):
    linkedin = OAuth2Session(LINKEDIN_CLIENT_ID, redirect_uri=LINKEDIN_REDIRECT_URL, scope=LINKEDIN_SCOPE)
    authorization_url, state = linkedin.authorization_url(url=LINKEDIN_AUTHORIZATION_BASE_URL)

     # State is used to prevent CSRF, keep this for later.
    request.session['oauth_state'] = state
    return RedirectResponse(authorization_url)

@linkedin_route.get('/linkedin_auth', tags=['authentication'])  # Tag it as "authentication" for our docs
async def auth(request: Request, db:Session= Depends(get_db)):
    try:
        linkedin = requests_oauthlib.OAuth2Session(LINKEDIN_CLIENT_ID, 
                                        state=request.session['oauth_state'], 
                                        redirect_uri=LINKEDIN_REDIRECT_URL)
        
        linkedin.fetch_token(LINKEDIN_TOKEN_URL, client_secret=LINKEDIN_CLIENT_SECRET,
                                        include_client_id=True,
                                        authorization_response=str(request.url))
        
    #     # Fetch a protected resource, i.e. user profile
        response_email = linkedin.get(LINKEDIN_GET_USER_INFO).json()
        response_profile = linkedin.get('https://api.linkedin.com/v2/me').json()
        
        email = str(response_email['elements'][0]['handle~']['emailAddress']).lower()
        
        fetch_email = db.query(models.Users).filter(models.Users.email == email).first()
                
        if not fetch_email:
            raise HTTPException(status_code=400, detail="Incorrect email address")
        access_token = create_access_token(data={"data": fetch_email.email})
        refresh_token = create_refresh_token(fetch_email.email)
        return JSONResponse(content={"status":200, "access_token":access_token, "refresh_token": refresh_token})

    except  BaseException as e:
        if "oauthlib.oauth2.rfc6749.errors.InvalidClientIdError" in str(e):
            raise HTTPException(status_code=403, detail='This authorization code has been used.')
        elif "oauth_state" in str(e):
            raise HTTPException(status_code=404, detail='authorization token not found or deleted')


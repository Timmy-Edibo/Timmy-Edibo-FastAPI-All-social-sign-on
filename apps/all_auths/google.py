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

import requests_oauthlib
from authlib.integrations.starlette_client import OAuth

google_route = APIRouter(tags=['google_auth'])


# Initialize our OAuth instance from the client ID and client secret specified in our .env file
config = Config('.env')
oauth = OAuth(config)


import os
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_TOKEN_URL  = os.environ.get('GOOGLE_TOKEN_URL')
GOOGLE_AUTHORIZATION_BASE_URL = os.environ.get('GOOGLE_AUTHORIZATION_BASE_URL')
SCOPE = ['openid', 'email', 'profile']

@google_route.get('/login', tags=['authentication'])  # Tag it as "authentication" for our docs
async def login(request: Request):

    google = requests_oauthlib.OAuth2Session(GOOGLE_CLIENT_ID, 
                                            redirect_uri=request.url_for('auth'), 
                                            scope=SCOPE)
    authorization_url, state = google.authorization_url(GOOGLE_AUTHORIZATION_BASE_URL)

    # State is used to prevent CSRF, keep this for later.
    request.session['oauth_state'] = state
    print(authorization_url)
    return RedirectResponse(authorization_url)


@google_route.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):

    try:
        google = requests_oauthlib.OAuth2Session(GOOGLE_CLIENT_ID, 
                                                redirect_uri=request.url_for('auth'),
                                                state=request.session['oauth_state'])
            
        google.fetch_token(GOOGLE_TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET,
                                    authorization_response=str(request.url))

        response = (google.get('https://www.googleapis.com/oauth2/v3/userinfo').json())

        fetch_email = db.query(models.Users).filter(models.Users.email == str(response["email"]).lower()).first()
            
        if not fetch_email:
            raise HTTPException(status_code=404, detail='Incorrect email address')
        access_token = create_access_token(data={"data": fetch_email.email})
        refresh_token = create_refresh_token(fetch_email.email)
        return JSONResponse(content={"status":200, "access_token":access_token, "refresh_token": refresh_token})

    except BaseException as e:
        if "oauthlib.oauth2.rfc6749.errors.CustomOAuth2Error" in str(e):
            raise HTTPException(status_code=403, detail='This authorization code has been used.') 
        if "oauth_state" in str(e):
            raise HTTPException(status_code=403, detail='This authorization code has been deleted.') 

    
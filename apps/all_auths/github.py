from fastapi import APIRouter, Depends, HTTPException

import requests_oauthlib, oauthlib
from apps.jwt import create_access_token, create_refresh_token

from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse


from apps import models
from apps.database import get_db, engine
from sqlalchemy.orm import Session
models.Base.metadata.create_all(bind=engine)


from authlib.integrations.starlette_client import OAuth

URL = "http://localhost:8000"

git_route= APIRouter(tags=['facebook'])


config = Config('.env')
oauth = OAuth(config)

import os
from dotenv import load_dotenv
load_dotenv()


# This information is obtained upon registration of a new GitHub
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GIT_AUTHORIZATION_BASE_URL = os.environ.get('GIT_AUTHORIZATION_BASE_URL')
GIT_TOKEN_URL = os.environ.get('GIT_TOKEN_URL')

@git_route.get("/github")
async def login(request: Request):
    github = requests_oauthlib.OAuth2Session(GITHUB_CLIENT_ID, redirect_uri=URL + "/callback",)
    authorization_url, state = github.authorization_url(GIT_AUTHORIZATION_BASE_URL)

    # State is used to prevent CSRF, keep this for later.
    request.session['oauth_state'] = state
    return RedirectResponse(authorization_url)

@git_route.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):

    try:
        github = requests_oauthlib.OAuth2Session(GITHUB_CLIENT_ID, state=request.session['oauth_state'])

        github.fetch_token(GIT_TOKEN_URL, client_secret=GITHUB_CLIENT_SECRET, authorization_response=str(request.url))

        response = (github.get('https://api.github.com/user').json())

        name, picture_url, email = response["login"], response['avatar_url'],  response["email"]
        
        fetch_email = db.query(models.Users).filter(models.Users.email == str(email).lower()).first()
            
        if fetch_email:
            access_token = create_access_token(data={"data": fetch_email.email})
            refresh_token = create_refresh_token(fetch_email.email)
            return JSONResponse(content={"status":200, "access_token":access_token, "refresh_token": refresh_token})

        # Show the login link
        raise HTTPException(status_code=400, detail="Incorrect email address")
    
    except BaseException as e:
        if "oauth_state" in str(e):
            raise HTTPException(status_code=403, detail="Authorization token could not be found")
        if oauthlib.oauth2.rfc6749.errors.CustomOAuth2Error in str(e):
            raise HTTPException(status_code=403, detail='The code passed is incorrect or expired')

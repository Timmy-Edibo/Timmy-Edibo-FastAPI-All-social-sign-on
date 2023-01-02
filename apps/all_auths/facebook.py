import os
from fastapi import APIRouter, Depends, HTTPException


import requests_oauthlib, oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from apps.jwt import create_access_token, create_refresh_token

from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse


from apps import models
from apps.database import get_db, engine
from sqlalchemy.orm import Session
models.Base.metadata.create_all(bind=engine)


from authlib.integrations.starlette_client import OAuth

fb = APIRouter(tags=['facebook'])

# Initialize our OAuth instance from the client ID and client secret specified in our .env file
config = Config('.env')
oauth = OAuth(config)

# --- Google OAuth ---
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
FB_AUTHORIZATION_BASE_URL = os.environ.get('FB_AUTHORIZATION_BASE_URL')
FB_TOKEN_URL = os.environ.get('FB_TOKEN_URL')
FB_SCOPE = ['email']
URL = "http://localhost:8000"


import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

@fb.get('/facebook')
async def facebook_login(request: Request):
    facebook = requests_oauthlib.OAuth2Session(
        FACEBOOK_CLIENT_ID, redirect_uri=URL + "/facebook_auth", scope=FB_SCOPE
    )
    authorization_url, state = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)
    request.session['oauth_state'] = state

    return RedirectResponse(authorization_url)


@fb.get('/facebook_auth')
async def facebook_auth(request: Request, db:Session=Depends(get_db)):
    try:
        facebook = requests_oauthlib.OAuth2Session(
            FACEBOOK_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/facebook_auth"
        )

        # we need to apply a fix for Facebook here
        facebook = facebook_compliance_fix(facebook)

        facebook.fetch_token(
            FB_TOKEN_URL,
            client_secret=FACEBOOK_CLIENT_SECRET,
            authorization_response=str(request.url)
        )

        # Fetch a protected resource, i.e. user profile, via Graph API
        facebook_user_data = facebook.get(
            "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
        ).json()
        request.session['oauth_state'] = dict(facebook_user_data)

        name, email = facebook_user_data["name"], facebook_user_data["email"]
        picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")

        fetch_email = db.query(models.Users).filter(models.Users.email == email).first()
            
        if fetch_email:
            access_token = create_access_token(data={"data": fetch_email.email})
            refresh_token = create_refresh_token(fetch_email.email)
            return JSONResponse(content={"status":200, "access_token":access_token, "refresh_token": refresh_token})
            # return HTMLResponse(html)

        # Show the login link
        raise HTTPException(status_code=400, detail="Incorrect email address")

   
    except oauthlib.oauth2.rfc6749.errors.CustomOAuth2Error:
        raise HTTPException(status_code=403, detail='This authorization code has been used.')
        # return RedirectResponse(f"{URL}/facebook")

# FastAPI and Google Login (OAuth)
This is an example following the tutorials:
- [Guide 1 - Google OAuth Login with FastAPI](https://blog.hanchon.live/guides/google-login-with-fastapi/)
- [Guide 2 - Google OAuth and FastAPI JWT](https://blog.hanchon.live/guides/google-login-with-fastapi-and-jwt/)
- [Guide 3 - JWT blacklist and refresh tokens](https://blog.hanchon.live/guides/jwt-tokens-and-fastapi/)

## Requirements:
- Python3.6+

## How to run the example:
- Create a virtualenv `python3 -m venv .venv`
- Activate the virtualenv `. .venv/bin/activate`
- Install the requirements `pip install -r requirements.txt`
- Set up the env vars:
    # OAuth settings
    - GOOGLE_CLIENT_ID=''
    - GOOGLE_CLIENT_SECRET=''
    - GOOGLE_TOKEN_URL=''
    - GOOGLE_AUTHORIZATION_BASE_URL=''

    - SECRET_KEY=''
    - API_SECRET_KEY=''

    - FACEBOOK_CLIENT_ID = ''
    - FACEBOOK_CLIENT_SECRET = ''
    - FB_AUTHORIZATION_BASE_URL =''
    - FB_TOKEN_URL = ''

    - GITHUB_CLIENT_ID = ''
    - GITHUB_CLIENT_SECRET = ''
    - GIT_AUTHORIZATION_BASE_URL = ''
    - GIT_TOKEN_URL = ''

    - LINKEDIN_CLIENT_ID = ''
    - LINKEDIN_CLIENT_SECRET = ''
    - LINKEDIN_AUTHORIZATION_BASE_URL = ''
    - LINKEDIN_TOKEN_URL = ''
    - LINKEDIN_GET_USER_INFO =''
    - LINKEDIN_REDIRECT_URL = ''
    
- Run the app:
    - Guide 1: `python run.py`
    - Guide 2 and 3: `python main.py`

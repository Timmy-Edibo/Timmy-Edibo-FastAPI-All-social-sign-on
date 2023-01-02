from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi


from apps.jwt import create_access_token, create_refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES

from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse


from apps import models
from apps.database import get_db, engine
from sqlalchemy.orm import Session
models.Base.metadata.create_all(bind=engine)


from authlib.integrations.starlette_client import OAuth
from apps.users import router
from apps.facebook import fb
from apps.github import git_route
from apps.google import google_route
# Initialize FastAPI

app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key='!secret')

app.include_router(router)
app.include_router(fb)
app.include_router(git_route)
app.include_router(google_route)



# Initialize our OAuth instance from the client ID and client secret specified in our .env file
config = Config('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.get('/')
async def home(request: Request, db: Session = Depends(get_db)):
    # Try to get the user
    # user = request.session.get('user')
    # print(user)
    # if user is not None:
    #     html = (
    #     f"<p>Hello, {user['name']}! You're logged in! Email: {user['email']}</p>"
    #        "<div><p>Google Profile Picture:</p>"
    #         f'<img src="{user["picture"]}" alt="Google profile pic" referrerpolicy="no-referrer"></img></div>'
    #         '<a href="/docs">documentation</a><br>'
    #         '<a href="/logout">logout</a>'
    #     )
        
    #     fetch_email = db.query(models.Users).filter(models.Users.email == user["email"]).first()
        
    #     if fetch_email:
    #         print(fetch_email.email, fetch_email.username)
    #         # and user['email_verified'] ==True
    #         access_token = create_access_token(data={"data": fetch_email.email})
    #         refresh_token = create_refresh_token(fetch_email.email)

    #     return JSONResponse(content={"status":200, "access_token":access_token, "refresh_token": refresh_token})
        # return HTMLResponse(html)

    # Show the login link
    urls = """
    <div>
    <a href="/github">login with Github</a><br>
    <a href="/login">login with Google</a><br>
    <a href="/facebook">login with Facebook</a><br

    </div>
    """
    return HTMLResponse(urls)


# --- Google OAuth ---

# @app.get('/login', tags=['authentication'])  # Tag it as "authentication" for our docs
# async def login(request: Request):
#     # Redirect Google OAuth back to our application
#     redirect_uri = request.url_for('auth')
    # return await oauth.google.authorize_redirect(request, redirect_uri)


# @app.get('/auth')
# async def auth(request: Request, db: Session = Depends(get_db)):
#     # Perform Google OAuth
#     token = await oauth.google.authorize_access_token(request)
#     user = await oauth.google.parse_id_token(request, token)
#     # Save the user
#     request.session['user'] = dict(user)

#     # print(dict(user))
#     response = dict(user)
#     return RedirectResponse(url='/')
    

@app.get('/logout', tags=['authentication'])  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop('user', None)
    return RedirectResponse(url='/')


# Try to get the logged in user
async def get_user(request: Request) -> Optional[dict]:
    user = request.session.get('user')
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials.')
    return None

# --- Documentation ---

@app.get('/openapi.json')
async def get_open_api_endpoint(request: Request, user: Optional[dict] = Depends(get_user)):  # This dependency protects our endpoint!
    response = JSONResponse(get_openapi(title='FastAPI', version=1, routes=app.routes))
    return response


@app.get('/docs', tags=['documentation'])  # Tag it as "documentation" for our docs
async def get_documentation(request: Request, user: Optional[dict] = Depends(get_user)):  # This dependency protects our endpoint!
    response = get_swagger_ui_html(openapi_url='/openapi.json', title='Documentation')
    return response


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='localhost', port=8000, log_level='debug', reload=True)
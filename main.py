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
from apps.all_auths.facebook import fb
from apps.all_auths.github import git_route
from apps.all_auths.google import google_route
from apps.all_auths.linkedin import linkedin_route
# Initialize FastAPI

app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key='!secret')

app.include_router(router)
app.include_router(fb)
app.include_router(git_route)
app.include_router(google_route)
app.include_router(linkedin_route)


@app.get('/')
async def home(request: Request, db: Session = Depends(get_db)):
    urls = """
    <div>
    <div><a href="/linkedin">login with Linkedin</a><div><br
    <div><a href="/github">login with Github</a></div><br>
    <div><a href="/login">login with Google</a></div><br>
    <div><a href="/facebook">login with Facebook</a></div><br>
    </div>
    """
    return HTMLResponse(urls)


@app.get('/logout', tags=['authentication'])  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop('user', None)
    return RedirectResponse(url='/')


# Try to get the logged in user
async def get_user(request: Request) -> Optional[dict]:
    user = request.session.get('oauth_state')
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
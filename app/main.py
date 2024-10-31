import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import routes as auth_router
from app.api.todos import routes as todo_router
from app.config import config
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Set the timezone based on the app configuration
os.environ["TZ"] = config.APP_TZ
time.tzset()

# Initialize the FastAPI app
app = FastAPI(
    docs_url=config.docs_url,  # URL for Swagger UI documentation
    debug=not config.production,  # Debug mode based on production configuration
    openapi_url=config.openapi_url,  # URL for OpenAPI schema
)

# Add middleware to handle proxy headers and trusted hosts
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=config.FORWARDED_ALLOW_IPS)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allow_hosts)

# Add GZip middleware for response compression

# Add CORS middleware to handle Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,  # Allow credentials like cookies
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Include routers for todos and users

# TODO: Comment on the purpose of the commented-out code below
# if config.ENVIRONMENT in ["staging", "prod"]:
#     app.on_event("startup")(add_groups_and_roles)


routes = [
    todo_router,
    auth_router
    # Add other routers as needed
]
# Loop through the routes list and include routers in the FastAPI app
for router_model in routes:
    app.include_router(
        router_model.router
    )
    

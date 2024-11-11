import uvicorn

if __name__ == "__main__":
    """
    Entry point for starting the FastAPI application using Uvicorn.

    This script runs the FastAPI application with Uvicorn, which is an ASGI server. 
    The application will be hosted at http://127.0.0.1:8000 by default, with hot reloading enabled 
    for development purposes. The API is defined in 'src.api.api:api'.
    """
    uvicorn.run(
        "src.api.api:api",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
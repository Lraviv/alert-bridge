# main.py
import uvicorn
from api.api import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # set True for local dev
        log_level="info",
    )

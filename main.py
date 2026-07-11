import uvicorn
from api.server import app
from config import settings

if __name__ == "__main__":
    if settings.API_ENABLED:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        from scripts.run_simulation import main
        main()

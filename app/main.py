import uvicorn
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../.env'))

# Invoke-RestMethod -Uri "http://127.0.0.1:5000/test" -Method Get
if __name__ == '__main__':
    env = os.getenv("ENV")
    if (env == 'dev'):
        uvicorn.run("api:app", host="127.0.0.1", port=5000, reload=True)
    else:
        uvicorn.run("api:app", host="0.0.0.0", port=5000)

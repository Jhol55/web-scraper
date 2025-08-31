import uvicorn
import os
from dotenv import load_dotenv


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../.env'))


if __name__ == '__main__':
    env = os.getenv("ENV")
    if (env == 'dev'):
        uvicorn.run("api:api", host="127.0.0.1", port=8000, reload=True)
    else:
        # from waitress import serve
        print("✅ Aplicação iniciada com sucesso!")
        # serve(app, host="0.0.0.0", port=5000)

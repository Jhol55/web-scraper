from fastapi import FastAPI
import os
import importlib.util

app = FastAPI()

directory = os.path.join(os.path.dirname(__file__), 'routes')
ignore = ['__pycache__']

folders = list(filter(lambda filename: os.path.isdir(os.path.join(directory, filename)) and filename not in ignore, os.listdir(directory)))

for folder in folders:
    folder_path = os.path.join(directory, folder)
    for filename in os.listdir(folder_path):
        if filename == 'routes.py':
            file_path = os.path.join(directory, folder_path, filename)    
            module_name = filename[:-3]  
            spec = importlib.util.spec_from_file_location(module_name, file_path)   
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            try:
                app.include_router(module.router)
            except AttributeError:
                pass
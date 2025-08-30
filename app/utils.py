from functools import wraps
import time

def retry_on_exception(max_tries=2, wait_time=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            tries = max_tries
            while tries > 0:
                try:
                    return func(self, *args, **kwargs)
                except:
                    if not self.retry:
                        break
                    
                    tries -= 1
                    time.sleep(wait_time)
                
        return wrapper
    return decorator

def retry_on_exception_and_not_result(max_tries=2, wait_time=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            tries = max_tries
            result = None

            while tries > 0 and not result:
                try:
                    result = func(self, *args, **kwargs)

                    if not result:
                        raise Exception()
                except:
                    if not self.retry:
                        break

                    tries -= 1
                    time.sleep(wait_time)

            return result
        return wrapper
    return decorator

import os
import winreg

def get_chrome_path_windows():
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        chrome_path, _ = winreg.QueryValueEx(key, None)
        return chrome_path
    except FileNotFoundError:
        return None

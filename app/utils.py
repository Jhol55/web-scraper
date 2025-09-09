from functools import wraps
import time

def retry():
    """
    ✨ Decorator to retry a function's execution in case of an exception.

    Args:
        max_retries (int): The maximum number of attempts before failing.
        wait_time (int): The waiting time in seconds between attempts.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            max_retries = self.max_retries
            wait_time = self.wait_time
            last_exception = None

            for attempt in range(max_retries):
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    print(f"❌ Tentativa {attempt + 1}/{max_retries} erro: {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator
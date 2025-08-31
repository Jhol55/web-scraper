from functools import wraps
import time

def retry():
    """
    Decorador para repetir a execução de um método em caso de exceção
    ou resultado inválido (falsy).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            tries = self.max_tries
            check_result = self.check_result
            wait_time = self.wait_time
            last_exception = None

            while tries > 0:
                try:
                    result = func(self, *args, **kwargs)
                    if check_result and not result:
                        raise ValueError("Resultado inválido (falsy)")
                    return result
                except Exception as e:
                    last_exception = e
                    tries -= 1
                    if tries > 0:
                        time.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator

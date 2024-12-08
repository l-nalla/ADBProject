import random
import string

def generate_session_cookie():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=24))
# MIT License
# Copyright (c) 2025 JinxedUp
import os, json

def load_cookies():
    if os.path.exists("cookies.json"):
        with open("cookies.json", 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_cookies(cookies):
    with open("cookies.json", 'w') as f:
        json.dump(cookies, f)

from modules.headless.render import render_url

from lib.config import Config

if __name__ == "__main__":
    import json
    # For testing
    #print(json.dumps(render_url('https://gofishdigital.com/'), indent=2))
    print(json.dumps(Config(module='headless').headless.ignore, indent=2))

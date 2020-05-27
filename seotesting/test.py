from modules.headless.render import render_url


if __name__ == "__main__":
    import json
    # For testing
    print(json.dumps(render_url('https://locomotive.agency/'), indent=2))

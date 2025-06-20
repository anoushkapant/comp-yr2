import requests

HOST = "http://127.0.0.1:8080"

test_cases = [
    ("Existing file", f"{HOST}/index.html"),
    ("Non-existent file", f"{HOST}/doesnotexist.html"),
    ("Forbidden file (if applicable)", f"{HOST}/protected_file.html"),
    ("Invalid HTTP method", f"{HOST}/index.html", "POST"),
    ("Unsupported media type", f"{HOST}/unknown.xyz"),
    ("Conditional GET - If-Modified-Since", f"{HOST}/index.html", "GET", {"If-Modified-Since": "Tue, 30 Apr 2024 20:53:00 GMT"}),
]
for test_case in test_cases:
        name = test_case[0]
        url = test_case[1]
        method = test_case[2] if len(test_case) > 2 else "GET"
        headers = test_case[3] if len(test_case) > 3 else None

        try:
            response = requests.request(method, url, headers=headers)
            print(f"{name}: {response.status_code} {response.reason}")
        except requests.exceptions.RequestException as e:
            print(f"{name}: Failed - {e}")

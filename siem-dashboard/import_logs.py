import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def import_logs():
    # The example file contains a list of events.
    filename = Path(__file__).parent / "sample_logs.json"
    with filename.open() as file:
        events = json.load(file)

    imported = 0
    for event in events:
        # Convert a Python dictionary into JSON bytes for the HTTP request.
        data = json.dumps(event).encode("utf-8")
        request = Request(
            "http://127.0.0.1:8000/api/events",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                response.read()
            imported += 1
        except HTTPError as error:
            print(f"Import stopped: HTTP {error.code}. Check event {imported + 1}.")
            return
        except URLError:
            print("Cannot reach the server. Start it with: python app.py")
            return

    print(f"Imported {imported} events. Click Refresh in the dashboard.")


if __name__ == "__main__":
    import_logs()

#Run the Project

You’ve already set everything up. To run the servers:

##Terminal 1 — start the API
cd "C:\xampp\htdocs\Employee Suggestion System - Resume Based\employee-suggester"
uvicorn backend.app:app --host 127.0.0.1 --port 8002


Check the API docs at:
http://127.0.0.1:8002/docs

##Terminal 2 — start the web page
cd "C:\xampp\htdocs\Employee Suggestion System - Resume Based\employee-suggester"
python -m http.server 8080 -d ui


##Open the UI at:
http://127.0.0.1:8080/


##Notes

Stop either server with Ctrl+C.

To expose the API on your LAN, use:

uvicorn backend.app:app --host 0.0.0.0 --port 8001

from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import websockets
import asyncio
import websockets.asyncio.server
from threading import Thread
import socket

CLIENTS = set()

try:
    host = socket.gethostbyname(socket.gethostname())
except:
    print("failed to resolve hostname...")
    input()

print(f"Host name resolved: '{host}'")

port = 8000

try:

    with open("messages.json", "r") as f:
        messages = json.load(f)

except:
    messages = {}

with open("linkage/linkage.html", "b+r") as f:
    website_data = f.read()


class MyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):  # GET

        print(f"\nGET REQUEST: {self.request}")

        # Serve the main HTML file
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open("linkage/linkage.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/api?type=get_messages":

            try:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                self.wfile.write(bytes(str(json.dumps(messages)), "utf-8"))

                print("Succsessfull")

            except Exception as e:
                self.send_error(400, "Internal Server Error")
                print(f"ERROR IN /api?type=get_messages: {e}")

        elif self.path.endswith(".css"):  # serve css
            try:

                self.send_response(200)
                self.send_header("Content-type", "text/css")
                self.end_headers()
                with open("linkage" + self.path, "rb") as f:
                    self.wfile.write(f.read())

            except FileNotFoundError:
                self.send_error(404, "CSS file not found")

        elif self.path.endswith(".js"):  # serve js
            try:
                self.send_response(200)
                self.send_header("Content-type", "application/javascript")
                self.end_headers()
                with open("linkage" + self.path, "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "JS file not found")

        elif self.path.endswith((".svg", ".png", ".ico")):  # Images
            try:

                if self.path.endswith(".svg"):
                    content_type = "svg+xml"

                elif self.path.endswith(".png"):
                    content_type = "png"

                elif self.path.endswith(".ico"):
                    content_type = "x-icon"

                self.send_response(200)
                self.send_header("Content-type", f"image/{content_type}")
                self.end_headers()
                with open("linkage" + self.path, "rb") as f:
                    self.wfile.write(f.read())

            except FileNotFoundError:
                self.send_error(404, "CSS file not found")

        else:
            self.send_error(404, "File not found")  # handle unknown file type

    def do_POST(self):  # POST

        pass  # n


async def handler(websocket: websockets.ServerConnection):  # WEBSOCKET SERVER

    CLIENTS.add(websocket)

    try:
        await websocket.send(json.dumps({"type": "msg_send", "msg": messages}))

        async for message in websocket:

            json_message = json.loads(message)

            if json_message["type"] == "msg_send":

                temp = {}
                temp.update({"username": json_message["username"]})
                temp.update({"msg": json_message["msg"]})

                messages.update({len(messages): temp})

                with open("messages.json", "w") as f:
                    f.write(json.dumps(messages))

                message = messages[len(messages) - 1]

                packet = {
                    "type": "msg_update",
                    "msg": message["msg"],
                    "username": message["username"],
                }

                try:
                    await websockets.asyncio.server.broadcast(
                        CLIENTS, message=json.dumps(packet)
                    )
                except TypeError:
                    pass

    finally:
        CLIENTS.remove(websocket)


# --- HTTP Server Thread ---
def run_http_server():
    with HTTPServer((host, port), MyHandler) as server:
        print(f"HTTP server running at http://{host}:{port}")
        server.serve_forever()


async def ws_server():
    # Start WebSocket server
    print(f"WebSocket server running at ws://{host}:8001")

    async with websockets.serve(handler, host, 8001):
        await asyncio.Future()  # keep running forever


if __name__ == "__main__":

    # Start HTTP server in another thread
    Thread(target=run_http_server, daemon=True).start()

    # Run WebSocket server in main async loop
    asyncio.run(ws_server())

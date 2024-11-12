from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

import socketserver
from http import server

from threading import Condition
 
import io

# Reads html file and allows its utilization for the website
leHtml = open("pageHtml.html", "r")
pagecode = leHtml.read()

class VideoOut(io.BufferedIOBase): # Video feed 
    # Utilizes threading to move frames along efficently
    def __init__(self):
        self.frame = None
        self.condition = Condition() # Creates a condition based on the frame input

    def write(self, buffer):
        with self.condition:
            self.frame = buffer
            self.condition.notify_all()

# https://docs.python.org/3/library/http.server.html#http.server.HTTPServer
class HttpHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if (self.path == "/"): # Auto redirects into stream feed
            self.send_response(301)
            self.send_header("Redirect Location", "/index.html")
            self.end_headers()

        elif (self.path == "/index.html"): # Shows the stream feed
            webContent = pagecode.encode("utf-8")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(webContent)

        elif (self.path == "/stream.mjpg"): # Is the stream feed
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()

            try: # Sends out the frames from camera
                while True:
                    with camOut.condition:
                        camOut.condition.wait()
                        frame = camOut.frame

                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")

            except Exception as e:
                print("Video Error")

        else:
            self.send_error(404)
            self.end_headers()

class WebServer(socketserver.ThreadingMixIn, server.HTTPServer): # Utilizes threading to help website running
    allow_reuse_address = True # Helps with website restarting
    daemon_threads = True # Helps with keeping track of threads

if (__name__ == "__main__"):
    # Initalizes camera
    # https://picamera.readthedocs.io/en/release-1.13/recipes2.html
    picamera = Picamera2()
    cameraConfig = picamera.create_video_configuration(main={"size": (1920, 1080)})
    picamera.configure(cameraConfig)
    
    # Sends camera into the website
    camOut = VideoOut()
    picamera.start_recording(JpegEncoder(), FileOutput(camOut))

    try:
        # Runs website server
        port = 6969
        addy = ("", port)
        server = WebServer(addy, HttpHandler)
        server.serve_forever()
        
    finally:
        picamera.stop_recording()
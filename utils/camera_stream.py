#!/usr/bin/env python3
from flask import Flask, render_template, Response
from picamera2 import Picamera2
import time
import io

app = Flask(__name__)

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (1920, 1080)})
picam2.configure(config)
picam2.start()
time.sleep(2)


def generate():
    while True:
        stream = io.BytesIO()
        picam2.capture_file(stream, format="jpeg")
        stream.seek(0)
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + stream.read() + b"\r\n")


@app.route("/")
def index():
    return """<html><head><title>Pi Camera Stream</title></head>
    <body><h1>Pi Camera Stream</h1><img src="/video_feed"></body></html>"""


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

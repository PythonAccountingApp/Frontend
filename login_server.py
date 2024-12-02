from PyThreadKiller import PyThreadKiller
import flask
from waitress import serve



class LoginServer:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.serverThread = PyThreadKiller(self.run_server)
        self.callbackData = None
        self.server_status = False

        # 路由註冊
        self.app.add_url_rule("/", "root", self.root)
        self.app.add_url_rule("/github/callback", "GithubCallback", self.GithubCallback, methods=["GET"])
        self.app.add_url_rule("/google/callback", "GoogleCallback", self.GoogleCallback, methods=["GET"])
        self.app.add_url_rule("/google/callback/handle", "GoogleCallbackHandle", self.GoogleCallbackHandle, methods=["GET"])

    def run_server(self):
        serve(self.app, host="localhost", port=53269)

    def root(self):
        return "ss"

    def GithubCallback(self):
        from flask import request, render_template
        if request.args.get("code") is not None:
            self.callbackData = request.args.get("code")
            return render_template("login_successful.html")
        else:
            self.callbackData = "ERROR"
        return render_template("login_failure_github.html")

    def GoogleCallback(self):

        from flask import render_template
        return render_template("google_login_callback.html")

    def GoogleCallbackHandle(self):
        from flask import request, render_template
        if request.args.get("access_token") is not None:
            self.callbackData = [request.args.get("access_token"),request.args.get("token_type")]
            return render_template("login_successful.html")
        else:
            self.callbackData = "ERROR"
            return render_template("login_failure_google.html")


    def LoginServerStart(self):
        print("Server Start")
        self.server_status = True
        self.serverThread.start()

# 2f56277d2ac07844952f

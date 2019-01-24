# Copyright 2019 Allison Boukall with socket and framework by Abram Hindle, Eddie Antonio Santos
#  Allison Boukall - 404 Assignment 1 submission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py
# try: curl -v -X GET http://127.0.0.1:8080/

############################
# Sources
# stackoverflow
# Replacements for switch statement in Python?
# URL: https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python
# Answer: https://stackoverflow.com/a/103081
# Author: Nick - https://stackoverflow.com/users/3233/nick
#
# stackoverflow
# Python: Get relative path from comparing two absolute paths
# URL: https://stackoverflow.com/questions/7287996/python-get-relative-path-from-comparing-two-absolute-paths
# Answer: https://stackoverflow.com/a/34468328
# Author: Jeremy Cochoy - https://stackoverflow.com/users/2535207/jeremy-cochoy
###########################
import socketserver
from pathlib import Path, PurePath

__404__ = """<!DOCTYPE html><html>
    <head><title>404 page not found</title></head>
    <body><h1>404 page not found</h1></body></html>"""

__405__ = """<!DOCTYPE html><html>
    <head><title>405 error</title></head>
    <body><h1>405 - METHOD NOT ALLOWED</h1></body></html>"""

def dictToString(data):
    packet = data['header']+"\r\n"
    if data.get('location'):
        packet += "Location: "+data['location']+"\r\n"
    if data.get('content'):
        packet += "Content-Type: "+data['content']+" charset=utf-8\r\n\r\n"
    if data.get('payload'):
        packet += data['payload']
    return packet

class MyWebServer(socketserver.BaseRequestHandler):
    response ={}

    def create404(self):
        self.response['header'] = "HTTP/1.1 404 Not Found"
        self.response['payload'] = __404__ 
        self.response['content'] = 'text/html;'

    def create405(self):
        self.response['header'] = "HTTP/1.1 405 Method Not Allowed"
        self.response['payload'] = __405__ 
        self.response['content'] = 'text/html;'

    def create200(self, method, payload):
        self.response['header'] = "HTTP/1.1 200 OK"
        self.response['payload'] = payload
        self.response['content'] = self.contentType(method)

    def create301(self, addr):
        self.response['header'] = "HTTP/1.1 301 Moved Permanently"
        self.response['location'] = addr+'/'
    
    # Handles the response packet depending on METHOD
    def methodType(self, header):
        method = header[0].strip(' ')
        if (method == "GET"):
            fileAddr = self.indexFix(header[1])
            return self.openFile(fileAddr)
        else:
            return self.create405()

    #Returns the correct mime type for the data
    def contentType(self, fType):
        return {
            'css': 'text/css;',
            'html': 'text/html;',
        }.get(fType, 'text/plain')  

    #opens file with two checks:
    # 1) Issues 404 if file can not be opened or not in 404
    # 2) Issue 301 if file requires redirect
    def openFile(self, fileAddr):
        ## test path is real
        if not (self.allowedPath(fileAddr)):
            self.create404()
            return 
        ##test redirect
        if (self.redirect(fileAddr)):
            self.create301(fileAddr)
            return
        try:
            file = open('www'+fileAddr, 'r')
            payload= file.read()
            self.create200(fileAddr.rsplit('.')[-1] , payload)
        except:
            self.create404()

    #test if a redirect is necessary, (if not file)
    def redirect(self, filename):
        if (len(filename.split('.'))==1 and filename[-1] != "/"):
            return True
        return False
    
    def allowedPath(self, fileAddr):
        dirPath = PurePath(Path(__file__).resolve().parent, 'www')
        reqPath = PurePath(dirPath, fileAddr[1:])
        if not (Path(reqPath).exists()):
            return False
        reqPath = (Path(reqPath).resolve())
        ##test in parents
        if (dirPath not in reqPath.parents):
            return False
        return True

    #will append index if dealing with a root 
    def indexFix(self, fileName):
        if (fileName[-1] == ("/")):
            fileName += 'index.html'
        return fileName


    def handle(self):
        self.data = self.request.recv(1024).strip()
        strData = self.data.decode("utf-8").split('\n')
        header = strData[0].split(' ')
        if (header):
            self.methodType(header)
            packet = dictToString(self.response)
            self.request.sendall(packet.encode())
            self.response.clear()
 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    #print ('Started httpserver on port ' , PORT)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

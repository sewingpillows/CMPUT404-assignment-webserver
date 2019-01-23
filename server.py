#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
# cite later !!!!!!https://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python
# cite later !!! https://stackoverflow.com/questions/7287996/python-get-relative-path-from-comparing-two-absolute-paths
import json
from pathlib import Path, PurePath

__404__ = """<!DOCTYPE html><html>
    <head><title>404 page not found</title></head>
    <body><h1>404 page not found</h1></body></html>"""

__405__ = """<!DOCTYPE html><html>
    <head><title>405 error</title></head>
    <body><h1>405 - METHOD NOT ALLOWED</h1></body></html>"""
    
def dictToString(data):
    packet = data['header']
    packet += data['content']
    if data.get('payload'):
        packet += data['payload']
    return packet



class MyWebServer(socketserver.BaseRequestHandler):
    content = "Content-Type:"
    charset = "charset=utf-8\r\n"
    response ={}


    def create404(self):
        self.response['header'] = "HTTP/1.1 404 Not Found\r\n"
        self.response['payload'] = __404__ 
        self.response['content'] = self.content+' text/html; '+self.charset+"\r\n"

    def create405(self):
        self.response['header'] = "HTTP/1.1 405 Method Not Allowed\r\n"
        self.response['payload'] = __405__ 
        self.response['content'] = self.content+' text/html; '+self.charset+"\r\n"

    def create200(self, method, payload):
        self.response['header'] = "HTTP/1.1 200 OK\r\n"
        self.response['payload'] = payload
        self.response['content'] = self.content+self.contentType(method)+self.charset+"\r\n"
    
    def methodType(self, header):
        method = header[0].strip(' ')
        fileAddr = self.indexFix(header[1])
        if (method == "GET"):
            return self.openFile(fileAddr)
        else:
            return self.create405()

    def contentType(self, fType):
        return {
            'css': 'text/css;',
            'html': 'text/html;',
        }.get(fType, 'error')  

    def openFile(self, fileAddr):
        dirPath = PurePath(Path(__file__).resolve().parent, 'www')
        reqPath = PurePath(dirPath, fileAddr[1:])
        reqPath = (Path(reqPath).resolve())
        if (dirPath not in reqPath.parents):
            self.create404()
            return 
        try:
            file = open('www'+fileAddr, 'r')
            payload= file.read()
            self.create200(fileAddr.rsplit('.')[-1] , payload)
        except:
            self.create404()


    def indexFix(self, fileName):
        if fileName.endswith("/"):
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
            self.response = {}
 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    #print ('Started httpserver on port ' , PORT)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

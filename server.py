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

    
def dictToString(data):
    packet = data['header']
    packet += data['content']
    if data.get('payload'):
        packet += data['payload']
    return packet



class MyWebServer(socketserver.BaseRequestHandler):
    content = "Content-Type:"
    charset = "charset=utf-8\r\n"

    def methodType(self, method):
        return {
            'GET': 'HTTP/1.1 200 OK\r\n',
            'POST': "HTTP/1.1 405 Method Not Allowed\r\n",
            'PUT': "HTTP/1.1 405 Method Not Allowed\r\n",
            'DELETE': "HTTP/1.1 405 Method Not Allowed\r\n"
        }.get(method, "HTTP/1.1 405 Method Not Allowed\r\n")  


    def contentType(self, fType):
        return {
            'css': self.content+' text/css; '+self.charset,
            'html': self.content+' text/html; '+self.charset,
        }.get(fType, 'error')  

    def openFile(self, fileAddr, data):
        print (fileAddr)
        reqPath = Path('www'+fileAddr).resolve
        dirPath = PurePath(Path(__file__).resolve().parent, 'www')
        print (reqPath in dirPath.parents)
        if (reqPath not in dirPath.parents):
            data['header'] = "HTTP/1.1 404 Not Found\r\n"
            data['payload'] = __404__ 
            data['content'] = self.content+' text/html; '+self.charset+"\r\n"
            return 
        if fileAddr.endswith("/"):
            fileAddr += 'index.html'
        try:
            print ("open")
            file = open('www'+fileAddr, 'r')
            payload= file.read()
            data['payload'] = payload
        except:
            data['header'] = "HTTP/1.1 404 Not Found\r\n"
            data['payload'] = __404__ 
            data['content'] = self.content+' text/html; '+self.charset+"\r\n"

    def parseData(self):
        strData = self.data.decode("utf-8").split('\n')
        header = strData[0].split(' ')
        if (header):
            data = {}
            data['header'] = self.methodType(header[0])
            data['content'] = self.contentType(header[1].rsplit('.')[-1])+"\r\n"
            self.openFile(header[1], data)
            return dictToString(data)

    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        packet =self.parseData()
        print (packet)
        self.request.sendall(packet.encode())
 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    print ('Started httpserver on port ' , PORT)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

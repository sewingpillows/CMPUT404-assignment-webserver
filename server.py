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

###########################
# **********
# Citations
# **********
#
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
        if (self.redirect(header[1])):
            print ("CREATE 301")
            return self.create301(header[1])
        fileAddr = self.indexFix(header[1])
        if (method == "GET"):
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
    # 1) Issues 404 if file can not be opened
    # 2) Issue 404 if file is not located in www
    def openFile(self, fileAddr):
        print ("CREATE OPEN")
        dirPath = PurePath(Path(__file__).resolve().parent, 'www')
        reqPath = PurePath(dirPath, fileAddr[1:])
        if not (Path(reqPath).exists()):
            print (reqPath)
            #print ("FAILS AT PATHCONTRAO")
            self.create404()
            return 
        reqPath = (Path(reqPath).resolve())
        if (dirPath not in reqPath.parents):
            print ("FAILS AT PATH2")
            self.create404()
            return 
        try:
            file = open('www'+fileAddr, 'r')
            payload= file.read()
            self.create200(fileAddr.rsplit('.')[-1] , payload)
        except:
            self.create404()

    #test if a redirect is necessary, (if not file)
    def redirect(self, filename):
        dirPath = PurePath(Path(__file__).resolve().parent, 'www')
        print (dirPath)
        print (filename)
        reqPath = PurePath(dirPath, filename[1:])
        print (reqPath)
        if not (Path(reqPath).exists()):
            return False
        reqPath = (Path(reqPath).resolve())
        if (dirPath not in reqPath.parents):
            return False
        if (len(filename.split('.'))==1 and filename[-1] != "/"):
            return True
        return False

    #will append index if dealing with a root 
    def indexFix(self, fileName):
        if fileName.endswith("/"):
            fileName += 'index.html'

        return fileName


    def handle(self):
        self.data = self.request.recv(1024).strip()
        strData = self.data.decode("utf-8").split('\n')
        header = strData[0].split(' ')
        print ("HEADER", header)
        if (header):
            self.methodType(header)
            packet = dictToString(self.response)
            print (packet)
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

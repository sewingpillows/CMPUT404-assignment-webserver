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
from urllib import request
from enum import Enum     # for enum34, or the stdlib version
# from aenum import Enum  # for the aenum version
#!! CITE LATER IF USING ENUM
METHOD = Enum('Method', 'GET POST PUT DELETE')
STATUS = Enum('Status', '200 404 405')


class MyWebServer(socketserver.BaseRequestHandler):

    def methodType(self, method):
        return {
            'GET': "HTTP/1.1 200 OK\r\n",
            'POST': "405 Method Not Allowed\r\n",
            'PUT': "405 Method Not Allowed\r\n",
            'DELETE': "405 Method Not Allowed\r\n"
        }.get(method, "error")  


    def contentType(self, fType):
        content = "Content-Type"
        charset = "charset=utf-8\r\n"
        print (fType)
        return {
            'css': content+' text/css; '+charset,
            'html': content+' text/html; '+charset,
        }.get(fType, 'error')  

    def openFile(self, fileAddr):
        #print (fileAddr)
        try:
            file = open('www'+fileAddr, 'r')
            return file
        except:
            return False

    def parseData(self):
        strData = self.data.decode("utf-8").split('\n')
        header = strData[0].split(' ')
        #print (header)
        file = self.openFile(header[1])
        packet = self.methodType(header[0])
        #print (packet)
        packet += self.contentType(header[1].rsplit('.')[1])
        packet += "\r\n"
        if (file):
            packet += file.read()
    
        return packet

    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        ##print ("Got a request of: %s\n" % self.data)
        packet =self.parseData()
        strData = self.data.decode("utf-8").split('\n')
        header = strData[0].split(' ')
        #print (packet)
        file = open('www/index.html', 'r')
        data = "HTTP/1.1 200 OK\r\n"
        data += "Content-Type: text/html; charset=utf-8\r\n"
        data += "\r\n"
        data += file.read()
        #print (data)
        self.request.sendall(packet.encode())

        ##self.request.sendall(bytearray("OK",'utf-8'))
 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    print ('Started httpserver on port ' , PORT)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

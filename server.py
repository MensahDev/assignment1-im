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

import mimetypes
from http import HTTPStatus
import re
import os

CWD  = os.getcwd()
HOME = os.path.abspath('./www')

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
            
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        self.data = self.data.decode('utf-8')
        self.status = HTTPStatus.OK
        self.mimetype = mimetypes.types_map['.a']  #unknown type is application/octet-stream
        self.content = None

        if not self.data.startswith('GET'):
            # only handling get for now
            print('server doesnt serve non-GET requests yet')
            self.status = HTTPStatus.METHOD_NOT_ALLOWED
            self.respond()
            return

        self.handle_get()
        self.respond()
        
    def respond(self):
        response = 'HTTP/1.1 ' + str(self.status.value) + ' ' + self.status.phrase
        response += '\r\nContent-Type: ' + self.mimetype

        if self.content:
            response += "\n\n" + self.content
        self.request.sendall(response.encode('utf-8'))

    def handle_get(self):
        # reference: extracting URL from HTTP request via a regex
        # https://stackoverflow.com/questions/35555427/how-to-extract-url-from-get-http-request
        url_pattern = re.compile("^GET (.*)[ ].*")
        url = url_pattern.match(self.data).group(1)
        if url.endswith('/'):
            url += 'index.html'

        if url == '/deep':
            # 301 TODO is this hardcoding? If yes, whats the correct way?
            self.status = HTTPStatus.MOVED_PERMANENTLY
            return

        if not os.path.isfile(HOME+url):
            self.status = HTTPStatus.NOT_FOUND
            return

        if os.path.abspath(HOME+url).find(CWD+"/www/") == -1:
            # /www/ should be in the current path
            self.status = HTTPStatus.NOT_FOUND
            return

        f = open(HOME+url)
        self.content = f.read()
        f.close()

        if url.endswith('.html'):
            self.mimetype = mimetypes.types_map['.html']
        elif url.endswith('.css'):
            self.mimetype = mimetypes.types_map['.css']

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

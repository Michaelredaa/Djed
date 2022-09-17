import sys
import json
import base64
import subprocess

if sys.version_info >= (3, 0):
    import http.client as http
else:
    import httplib as http

class RemotePainter() :
    def __init__(self, port=60041, host='localhost'):
        self._host = host
        self._port = port

        # Json server connection
        self._PAINTER_ROUTE = '/run.json'
        self._HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'}

    # Execute a HTTP POST request to teh Substance Painter server and send/receive JSON data
    def _jsonPostRequest( self, route, body, type ) :
        connection = http.HTTPConnection(self._host, self._port, timeout=3600)
        connection.request('POST', route, body, self._HEADERS)
        response = connection.getresponse()

        data = response.read()
        connection.close()

        if type == "js" :
            data = json.loads( data.decode('utf-8') )

            if 'error' in data:
                OutJson = json.loads( body.decode() )
                print( base64.b64decode( OutJson["js"] ) )
                raise ExecuteScriptError(data['error'])
        else :
            # Python can return nothing, so decoding can fail
            try:
                data = data.decode('utf-8').rstrip()
            except:
                pass

        return data

    def checkConnection(self):
        connection = http.HTTPConnection(self._host, self._port)
        connection.connect()

    # Execute a command
    def execScript( self, script, type ) :
        Command = base64.b64encode( script.encode('utf-8') )

        if type == "js" :
            Command = '{{"js":"{0}"}}'.format( Command.decode('utf-8') )
        else :
            Command = '{{"python":"{0}"}}'.format( Command.decode('utf-8') )

        Command = Command.encode( "utf-8" )

        return self._jsonPostRequest( self._PAINTER_ROUTE, Command, type )

class PainterError(Exception):
    def __init__(self, message):
        super(PainterError, self).__init__(message)

class ExecuteScriptError(PainterError):
    def __init__(self, data):
        super(PainterError, self).__init__('An error occured when executing script: {0}'.format(data))
import os
#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.


__author__="janos"
__date__ ="$Apr 16, 2010 9:33:17 PM$"

#from cgi import parse_qs, escape
#from genshi.template import TemplateLoader
#from pprint import pprint

from semantic_resource_mapping import *
from pprint import pprint
import os
#import re
#from string import join

def test_application(environ, start_response):
    environ["SPYDER_WEB_CONFIG_INSTANCE"] = "rxnorm_configuration.json"
    return main(environ, start_response)
    
def main(environ, start_response):
    
    Errors = {} 
    if environ.has_key("SPYDER_WEB_CONFIG_INSTANCE"):
        try:
            config_filename = environ["SPYDER_WEB_CONFIG_INSTANCE"]
            cf = open(config_filename,'r')
        except IOError, message:
            Errors["IOError"] = "Failed to open %s" % config_filename

        try:
            config = json.loads(cf.read())
            cf.close()
        except ValueError, message:
            Errors["ErrorParsingConfigFile"] = message
            raise

        #Get Configuration
        if config.has_key("semantic_server_type"):
            if config["semantic_server_type"] == "VirtuosoSparqlEndPointConnection": #Virtuoso is the only supported semantic server at this time
                if config.has_key("semantic_server_address"):
                    sparql_endpoint_connection = config["semantic_server_address"]
                    semantic_server = VirtuosoSparqlEndPointConnection(sparql_endpoint_connection)
                else:
                    Errors["NoSparqlEndPoint"] = "There is no Sparql EndPoint Specified"
            else:
                Errors["NoSemanticServerType"] = "No semantic_server_type given in the configuration or invalid type given"
        if config.has_key("uri_to_map"):
            uri_to_map = config["uri_to_map"]
        else:
            Errors[NoUriToMap] = "The uri to map is not found. Normally this is the uri of the server"

    else:
        Errors["NoConfigurationInstance"] = "No configuration instance found please set os.environ['SpyderWebConfigInstance'] = '/var/web/rxnorm/config.json'"

    if len(Errors.keys()):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        response = str(Errors)
    else:

        semantic_resource_map = SemanticResourceMapping(semantic_server,uri_to_map)
        requested_path = environ["PATH_INFO"]
        found_uri = semantic_resource_map.find_resource(requested_path)

        if found_uri:
            status = "200 Ok"
            headers = [('Content-type', 'text/html')]

            about = "About: " + uri_to_map + requested_path

            #response = """<?xml version="1.0" encoding="UTF-8"?>"""
            #response += """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
            response="""<html>
            <head><title>%s</title></head>
            """ % about

            response +=   "<body>\n<h1>%s</h1>\n" % about
            sparql_obj = semantic_resource_map.get_resource(requested_path)
            
            response += "<table>\n"
            for row in sparql_obj.raw_result:
                response += "<tr><td>"
                response += "%s</td><td>" % row["predicate"]["value"]
                if row["object"]["type"] == "uri":
                    response += '<a href="%s">%s</a>' % (row["object"]["value"],row["object"]["value"])
                else:
                    response += "%s" % row["object"]["value"]
                response += "</td></tr>\n"
                
            response += "</table>\n"
            response += "</body></html>"
        else:
            status = "404 Not Found"
            headers = [('Content-type', 'text/plain')]
            response = "Not found: " + uri_to_map + requested_path
            
    start_response(status, headers)
    return [str(response),]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    os.environ["SPYDER_WEB_CONFIG_INSTANCE"] = "rxnorm_configuration.json"
    server = make_server('localhost', 9001, test_application)
    server.serve_forever()

"""
 'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 'HTTP_COOKIE', 'showGraphNames=t; CFID=0; CFTOKEN=2ECCA207-9ACD-44DD-B4513E19C9F331D9' ,
 'HTTP_ACCEPT_ENCODING'
 'QUERY_STRING': '',
 'REMOTE_ADDR': '127.0.0.1',
 'REMOTE_HOST': 'janoslaptop',
 'REQUEST_METHOD': 'GET',
 'PATH_INFO': '/rxnorm/RXAUI',
"""
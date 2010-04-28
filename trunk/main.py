#! /usr/bin/python
import os

__author__="risk.limits"
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
        if config.has_key("default_graph"):
            default_graph = config["default_graph"]
        else:
            default_graph = None

    else:
        Errors["NoConfigurationInstance"] = "No configuration instance found please set os.environ['SpyderWebConfigInstance'] = '/var/web/rxnorm/config.json'"

    if len(Errors.keys()):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        response = str(Errors)
    else:

        semantic_resource_map = SemanticResourceMapping(semantic_server,uri_to_map,default_graph)
        requested_path = environ["PATH_INFO"]
        found_uri = semantic_resource_map.find_resource(requested_path)

        if found_uri:
            status = "200 Ok"
            headers = [('Content-type', 'text/html')]

            about = "About: " + uri_to_map + requested_path

            #response = """<?xml version="1.0" encoding="UTF-8"?>"""
            #response += """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
            response="""<html>
            <head><title>%s</title>
            <style>
/*
	Blue Dream
	Written by Teylor Feliz  http://www.admixweb.com
*/


table { background:#D3E4E5;
 border:1px solid gray;
 border-collapse:collapse;
 color:#fff;
 font:normal 12px verdana, arial, helvetica, sans-serif;
}
caption { border:1px solid #5C443A;
 color:#5C443A;
 font-weight:bold;
 letter-spacing:20px;
 padding:6px 4px 8px 0px;
 text-align:center;
 text-transform:uppercase;
}
td, th { color:#363636;
 padding:.4em;
}
tr { border:1px dotted gray;
}
thead th, tfoot th { background:#5C443A;
 color:#FFFFFF;
 padding:3px 10px 3px 10px;
 text-align:left;
 text-transform:uppercase;
}
tbody td a { color:#363636;
 text-decoration:none;
}
tbody td a:visited { color:gray;
 text-decoration:line-through;
}
tbody td a:hover { text-decoration:underline;
}
tbody th a { color:#363636;
 font-weight:normal;
 text-decoration:none;
}
tbody th a:hover { color:#363636;
}
tbody td+td+td+td a { background-image:url('bullet_blue.png');
 background-position:left center;
 background-repeat:no-repeat;
 color:#03476F;
 padding-left:15px;
}
tbody td+td+td+td a:visited { background-image:url('bullet_white.png');
 background-position:left center;
 background-repeat:no-repeat;
}
tbody th, tbody td { text-align:left;
 vertical-align:top;
}
tfoot td { background:#5C443A;
 color:#FFFFFF;
 padding-top:3px;
}
.odd { background:#fff;
}
tbody tr:hover { background:#99BCBF;
 border:1px solid #03476F;
 color:#000000;
}
            </style>
            </head>
            """ % about

            response +=   "<body>\n<h2>%s</h2>\n" % about
            sparql_obj = semantic_resource_map.get_resource(requested_path)

            response += "<div>\n"
            response += "<table>\n"
            response += "<tr><th>predicate</th><th>object<td></th></tr>\n"
            for row in sparql_obj:
                response += "<tr><td>"
                response += "%s</td><td>" % row["predicate"]["value"]
                if row["object"]["type"] == "uri":
                    response += '<a href="%s">%s</a>' % (row["object"]["value"],row["object"]["value"])
                else:
                    response += "%s" % row["object"]["value"]
                response += "</td></tr>\n"
                
            response += "</table>\n"

            reverse_sparql_obj = semantic_resource_map.get_reverse_resource(requested_path)

            response += "<br/>\n"

            response += "<table>\n"
            response += "<tr><th>predicate</th><th>subject<td></th></tr>\n"
            if reverse_sparql_obj:
                for row in reverse_sparql_obj:
                    response += "<tr>"
                    response += "<td>%s</td>" % row["predicate"]["value"]
                    response += "</td><td>"
                    response += '<a href="%s">%s</a>' % (row["subject"]["value"],row["subject"]["value"])
                    response += "</td></tr>\n"
            response += "</table>\n<br/>\n"
            response += "<footer>Served by Spyder-web</footer>"
            response += "</div>"

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
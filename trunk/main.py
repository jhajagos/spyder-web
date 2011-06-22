#! /usr/bin/python
import os
import urlparse
import urllib2

__author__="risk.limits"
__date__ ="$Apr 16, 2010 9:33:17 PM$"

from semantic_resource_mapping import *
import os

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
                    Errors["NoSparqlEndPoint"] = "There is no Sparql End Point Specified"
            else:
                Errors["NoSemanticServerType"] = "No semantic_server_type given in the configuration or invalid type given"

        if config.has_key("public_semantic_server_address"):
            public_semantic_server_address = config["public_semantic_server_address"]
        else:
            public_semantic_server_address = config["semantic_server_address"]
            
        if config.has_key("uri_to_map"):
            uri_to_map = config["uri_to_map"]
        else:
            Errors[NoUriToMap] = "The uri to map is not found. Normally this is the uri of the server"
        if config.has_key("default_graph"):
            default_graph = config["default_graph"]
        else:
            default_graph = None

        if config.has_key("header_to_include"):
            header_to_include = config["header_to_include"]
        else:
            header_to_include = ""

        if config.has_key("after_header_to_include"):
            after_header_to_include = config["after_header_to_include"]
        else:
            after_header_to_include = ""

        if config.has_key("footer_to_include"):
            footer_to_include = config["footer_to_include"]
        else:
            footer_to_include = ""

        if config.has_key("metadata_uri"):
            metadata_uri = config["metadata_uri"]
        else:
            metadata_uri = None

    else:
        Errors["NoConfigurationInstance"] = "No configuration instance found please set os.environ['SpyderWebConfigInstance'] = '/var/web/rxnorm/config.json'"

    if len(Errors.keys()):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        response = str(Errors)
    else:
        query_dictionary = urlparse.parse_qs(environ["QUERY_STRING"])
        semantic_resource_map = SemanticResourceMapping(semantic_server,uri_to_map,default_graph)
        requested_path = environ["PATH_INFO"]
        uri_object = semantic_resource_map.find_resource_path(requested_path)
        uri_exists = uri_object.exists()

        request_method = environ["REQUEST_METHOD"]
        if environ.has_key("HTTP_ACCEPT"):
            http_accept = environ["HTTP_ACCEPT"]
        else:
            http_accept = "text/html"

        content_type = "text/html"
        if "text/plain" in http_accept:
            content_type = "text/plain"

        if query_dictionary.has_key("content_type"):
            content_type=urllib2.unquote(query_dictionary["content_type"][0])

        if not(uri_exists):
            if query_dictionary.has_key("uri"):
                uri_to_decode = query_dictionary["uri"][0]
                uri = urllib2.unquote(uri_to_decode)
                uri_object = semantic_resource_map.find_resource(uri)
                uri_exists = uri_object.exists()

        if uri_exists:        
            status = "200 Ok"
            headers = [('Content-type', content_type)]

        if content_type not in ["text/plain","application/json","application/rdf+xml","text/html"]:
            status = "406 Not Acceptable"
            headers = [('Content-type', "text/plain")]
            response = "Cannot generate results for 'HTTP_ACCEPT' : '%s'" % content_type

        if uri_exists and request_method=="GET" and content_type in ["text/plain","application/json","application/rdf+xml"]: # Return machine readable represenstation of the resource
            response = uri_object.get_machine_readable_representation(content_type)

        if uri_exists and content_type=="text/html" and request_method=="GET":
            try:
                label = uri_object["rdfs:label"]

                if len(label):
                    label = " (%s)" % str(label.literal_value)
                else:
                    label = ""
            except:
                label = ""

            about = "About: " + uri_object.uri + label
            css = """
          /* Greyscale
Table Design by Scott Boyle, Two Plus Four
www.twoplusfour.co.uk
----------------------------------------------- */

table {border-collapse: collapse;
border: 2px solid #000;
font: normal 80%/140% arial, helvetica, sans-serif;
color: #555;
background: #fff;}

td, th {border: 1px dotted #bbb;
padding: .5em;}

caption {padding: 0 0 .5em 0;
text-align: left;
font-size: 1.4em;
font-weight: bold;
text-transform: uppercase;
color: #333;
background: transparent;}

/* =links
----------------------------------------------- */

table a {padding: 1px;
text-decoration: none;
font-weight: bold;
background: transparent;}

table a:link {border-bottom: 1px dashed #ddd;
color: #000;}

table a:visited {border-bottom: 1px dashed #ccc;
text-decoration: line-through;
color: #808080;}

table a:hover {border-bottom: 1px dashed #bbb;
color: #666;}

/* =head =foot
----------------------------------------------- */

thead th, tfoot th {border: 2px solid #000;
text-align: left;
font-size: 1.2em;
font-weight: bold;
color: #333;
background: transparent;}

tfoot td {border: 2px solid #000;}

/* =body
----------------------------------------------- */

tbody th, tbody td {vertical-align: top;
text-align: left;}

tbody th {white-space: nowrap;}

.odd {background: #fcfcfc;}

tbody tr:hover {background: #fafafa;}
            """

            response = """<?xml version="1.0" encoding="UTF-8"?>"""
            response += """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">"""
            response="""<html>
            <head><title>%s</title>
            <style>
                %s
            </style>
            %s
            </head>
            """ % (about,css,header_to_include)

            response +=   "<body>%s\n<h2>%s</h2>\n" % (after_header_to_include,about)
            
            response += "<div>\n"
            response += "<table>\n"
            response += "<tr><th>predicate</th><th>object<td></th></tr>\n"
            for uri in uri_object["-> ?"]:
                response += "<tr><td>"
                response += "%s</td><td>" % uri

                links = uri_object["-> %s" % uri]
                if type(links) != type([]):
                    links = [links]

                if len(links) > 1:
                    response += "<ul>"

                for link in links:
                    if len(links) > 1:
                        response += "<li>"
                    if type(link) == SemanticResourceObject:
                        response += '<a href="%s">%s</a>' % (link.uri,link.uri)
                    else:
                        response += "%s" % link.literal_value

                    if len(links) > 1:
                        response += "</li>"

                if len(links) > 1:
                    response += "</ul>"
                response += "</td></tr>\n"
                
            response += "</table>\n"

            links_to = uri_object["<- ?"]

            response += "<br/>\n"
            response += "<table>\n"
            response += "<tr><th>predicate</th><th>subject<td></th></tr>\n"
            
            for link_to in links_to:
                response += "<tr>"
                response += "<td>%s</td>" % link_to

                objects_linked_to = uri_object["<- %s" % link_to]

                if type(objects_linked_to) != type([]):
                    objects_linked_to = [objects_linked_to]

                response += "<td>"
                if len(objects_linked_to) > 1:
                    response += "<ul>"
                for object_linked_to in objects_linked_to:
                    if len(objects_linked_to) > 1:
                        response += "<li>"

                    response += '<a href="%s">%s</a>' % (object_linked_to.uri,object_linked_to.uri)
                    if len(objects_linked_to) > 1:
                        response += "</li>"

                if len(objects_linked_to) > 1:
                    response += "</ul>"

                response += "</td></tr>\n"
            response += "</table>\n<br/>\n"

            response += "<br/>"
            response += "<div>"
            response += """Alternative represenations of the resource: <a href="%s">ntriples</a> | <a href="%s">rdf+xml</a>
            """ % (uri_object.get_machine_readable_representation_uri("text/plain",public_semantic_server_address),uri_object.get_machine_readable_representation_uri("application/rdf+xml",public_semantic_server_address))

            response += "<div>"
            response += '<a href="%s">SPARQL Endpoint</a> | graph: <a href="%s">%s</a>' % (public_semantic_server_address, default_graph,default_graph)
            response += "</div>"
            if metadata_uri:
                response += "<div>"
                response += 'Metadata about this published resource: <a href="%s">%s</a>' % (metadata_uri,metadata_uri)
                response += "</div>"


            response += "</div>"
            response += "<br/>"

            response += footer_to_include
            response += """<footer>Served by <a href="http://code.google.com/p/spyder-web/">Spyder-web</a></footer>"""
            response += "</div>"

            response += "</body></html>"
            
        if not(uri_exists):
            status = "404 Not Found"
            headers = [('Content-type', 'text/plain')]
            response = "Not found: " + uri_object.uri
            
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
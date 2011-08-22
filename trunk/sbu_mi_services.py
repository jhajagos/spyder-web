service_definitions = {"pubmed2cuis" : {"parameters": {"pmid": {"regex" : "[0-9]{0,10}"}},
                              "sparql_endpoint" : "http://link.informatics.stonybrook.edu/sparqltoo/",
"sparql_query" : """select distinct ?cui ?cuilabel where {
{
?pmid  <http://purl.org/ontology/bibo/pmid> "%(pmid)s" .
?pmid <http://link.informatics.stonybrook.edu/pubmed/#MeshHeadingList> ?mh .
?mh ?seq ?pmidmh .
?pmidmh <http://link.informatics.stonybrook.edu/pubmed/#MeshMinorDescriptor> ?cui .
?pmidmh rdfs:label ?cuilabel . }
union
{
?pmid  <http://purl.org/ontology/bibo/pmid> "%(pmid)s" .
?pmid <http://link.informatics.stonybrook.edu/pubmed/#MeshHeadingList> ?mh .
?mh ?seq ?pmidmh .
?pmidmh <http://link.informatics.stonybrook.edu/pubmed/#MeshMajorDescriptor> ?cui .
?pmidmh rdfs:label ?cuilabel . }
}""", "default_graph" : "http://link.informatics.stonybrook.edu/pubmed"
}}
service_definitions = {"pubmed2cuis" : {"parameters": {"pmid": {"regex" : "[0-9]{0,10}"}},
                              "sparql_endpoint" : "http://linktoo.informatics.stonybrook.edu:8890/sparql",
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
}""", "default_graph" : "http://link.informatics.stonybrook.edu/pubmed",
"description" : "A web service that retrieves MeSH headers aligned to the UMLS CUI based on the PMID."
},  "cuiIsa" : {"parameters": {"cui": {"regex" : "C[0-9]{0,10}"}},
             "sparql_endpoint" : "http://localhost:8890/sparql",
             "sparql_query" : """prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cui1 ?aui1label ?aui1 ?aui1literal ?sab1 ?sab1label ?cui2 ?aui2 ?aui2literal ?aui2label ?cui2literal WHERE {
?cui1 rdf:type <http://link.informatics.stonybrook.edu/umls/CUI> .
?cui1 <http://link.informatics.stonybrook.edu/umls/CUI/CUI> "%(cui)s".
?aui1 <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui1 .
?aui1 <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?aui1literal .
?aui1 rdfs:label ?aui1label .
?aui1 <http://link.informatics.stonybrook.edu/umls/hasSAB> ?sab1 .
?sab1 rdfs:label ?sab1label .
?aui1 <http://link.informatics.stonybrook.edu/umls/RELA#isa> ?aui2 .
?aui2 <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui2 .
?aui2 rdfs:label ?aui2label .
?aui2 <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?aui2literal .
?aui2 <http://link.informatics.stonybrook.edu/umls/hasSAB> ?sab1 .
?cui2 <http://link.informatics.stonybrook.edu/umls/CUI/CUI> ?cui2literal.
}
""", "default_graph" : "http://nlm.nih.gov/research/umls/",
"description" : "A web service that takes a CUI and returns a parent (isa) term"},
"cuiInverseIsa" : {"parameters": {"cui": {"regex" : "C[0-9]{0,10}"}},
             "sparql_endpoint" : "http://localhost:8890/sparql",
             "sparql_query" : """prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cui1 ?aui1label ?aui1 ?aui1literal ?sab1 ?sab1label ?cui2 ?aui2 ?aui2literal ?aui2label ?cui2literal WHERE {
?cui1 rdf:type <http://link.informatics.stonybrook.edu/umls/CUI> .
?cui1 <http://link.informatics.stonybrook.edu/umls/CUI/CUI> "%(cui)s".
?aui1 <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui1 .
?aui1 <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?aui1literal .
?aui1 rdfs:label ?aui1label .
?aui1 <http://link.informatics.stonybrook.edu/umls/hasSAB> ?sab1 .
?sab1 rdfs:label ?sab1label .
?aui1 <http://link.informatics.stonybrook.edu/umls/RELA#inverse_isa> ?aui2 .
?aui2 <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui2 .
?aui2 rdfs:label ?aui2label .
?aui2 <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?aui2literal .
?aui2 <http://link.informatics.stonybrook.edu/umls/hasSAB> ?sab1 .
?cui2 <http://link.informatics.stonybrook.edu/umls/CUI/CUI> ?cui2literal.
}
""", "default_graph" : "http://nlm.nih.gov/research/umls/",
"description" : "A web service that takes a CUI and returns a child (inverse isa) term"},
"cuiChildren" : {"parameters": {"cui": {"regex" : "C[0-9]{0,10}"}},
            "sparql_endpoint" : "http://localhost:8890/sparql",
            "sparql_query" : """prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?cui1 ?aui1label ?aui1 ?aui1literal ?sab1 ?sab1label ?sab1literal ?cui2 ?aui2 ?aui2literal ?aui2label ?cui2literal WHERE {
?cui1 rdf:type <http://link.informatics.stonybrook.edu/umls/CUI> .
?cui1 <http://link.informatics.stonybrook.edu/umls/CUI/CUI> "%(cui)s".
?aui1 <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui1 .
?aui1 <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?aui1literal .
?aui1 rdfs:label ?aui1label .
?aui1 <http://link.informatics.stonybrook.edu/umls/hasSAB> ?sab1 .
?sab1 rdfs:label ?sab1label .
?sab1 <http://link.informatics.stonybrook.edu/umls/SAB/SAB> ?sab1literal .
?aui1 <http://link.informatics.stonybrook.edu/umls/REL#PAR> ?aui2 .
?aui2 <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui2 .
?aui2 rdfs:label ?aui2label .
?aui2 <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?aui2literal .
?aui2 <http://link.informatics.stonybrook.edu/umls/hasSAB> ?sab1 .
?cui2 <http://link.informatics.stonybrook.edu/umls/CUI/CUI> ?cui2literal.
}
""", "default_graph" : "http://nlm.nih.gov/research/umls/",
            "description" : "A web service that takes a CUI and returns a child term"},
"MeSHCui" : {"parameters": {"MeSH": {"regex" : r"[a-zA-Z0-9 \-/\(\)]"}},
             "sparql_endpoint" : "http://localhost:8890/sparql",
             "sparql_query" : """prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?aui ?cui ?auiliteral ?cuiliteral {
?aui <http://link.informatics.stonybrook.edu/umls/hasTermType> <http://link.informatics.stonybrook.edu/umls/TTY/MH> .
?aui rdfs:label "%s{MeSH}" .
?aui <http://link.informatics.stonybrook.edu/umls/hasCUI> ?cui .
?aui <http://link.informatics.stonybrook.edu/umls/AUI/AUI> ?auiliteral .
?cui <http://link.informatics.stonybrook.edu/umls/CUI/CUI> ?cuiliteral
}
}
""", "default_graph" : "http://nlm.nih.gov/research/umls/",
             "description" : "A web service that given a MeSH header returns a CUI"}
}

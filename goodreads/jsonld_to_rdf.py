import json
from rdflib import Graph, plugin


def convert_jsonld_to_rdf(input_file, output_file):
    with open(input_file, 'r') as f:
        jsonld_lines = f.readlines()

    print('json read')

    graph = Graph()
    for jsonld in jsonld_lines:
        data = json.loads(jsonld)
        g = Graph().parse(data=json.dumps(data), format='json-ld')
        for s, p, o in g:
            graph.add((s, p, o))

    print('graph created')

    with open(output_file, 'wb') as f:
        f.write(graph.serialize(format='turtle').encode('utf-8'))

    print('wrote in file the graph')


convert_jsonld_to_rdf('goodreads_ld_smaller.json', 'goodreads-smaller.ttl')





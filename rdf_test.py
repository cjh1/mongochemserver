from rdflib import Namespace, Graph, URIRef
from rdflib.term import BNode, Literal
from rdflib.namespace import RDF, OWL, NamespaceManager
import requests
import argparse

cheminf = Namespace('http://semanticscience.org/resource/')
mongochem = Namespace('http://openchemsitry.kitware.com/molecules#')



def create_molecule_graph(name, inchi):
    g = Graph()
    inchi_node = BNode()

    molecule = URIRef(mongochem[name])

    namespace_manager = NamespaceManager(g)
    namespace_manager.bind('cheminf', cheminf, override=False)
    namespace_manager.bind('mongochem', mongochem, override=False)
    namespace_manager.bind('owl', OWL, override=False)


    g.add((molecule, OWL.subClassOf, cheminf.CHEMINF_000000))
    g.add((molecule, OWL.label, Literal(name.lower())))
    g.add((inchi_node, RDF.type, cheminf.CHEMINF_000113))
    g.add((inchi_node, cheminf.SIO_000300, Literal(inchi)))
    g.add((molecule, cheminf.CHEMINF_000200, inchi_node))

    return g

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', required=True)
parser.add_argument('-p', '--password', required=True)

config = parser.parse_args()

molecules = [('Methane', 'InChI=1/CH4/h1H4'),
             ('Ethanol', 'InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3'),
             ('Methanol', 'InChI=1S/CH4O/c1-2/h2H,1H3')]

creds = (config.user, config.password)

for (name, inchi) in molecules:
    mol = create_molecule_graph(name, inchi)
    rdf =  mol.serialize()

    print rdf

    r = requests.put('http://localhost:8890/DAV/home/mongochem/rdf_sink/%s.rdf' % name, data=rdf, auth=creds)
    r.raise_for_status()


# Now run SPARQL query for Ethanol

query = 'SELECT DISTINCT ?x ' \
        'WHERE ' \
            '{ ?x <http://semanticscience.org/resource/CHEMINF_000200> ?y . ' \
               '?y <http://semanticscience.org/resource/SIO_000300> "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3" ' \
            '}'

print query

params = {
    'default-graph-uri': 'http://localhost:8890/DAV/home/mongochem/rdf_sink#this',
    'query': query,
    'format': 'application/sparql-results+json'
}


r = requests.get('http://localhost:8890/sparql', params=params, auth=creds)
r.raise_for_status()

print r.json()






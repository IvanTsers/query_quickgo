import sys
import requests
import argparse
import pandas as pd
import json
from argparse import RawTextHelpFormatter
from io import BytesIO

### Output formatting ###
def print_non_obsolete_table(x, cols):
    '''
    Prints specified columns of x where isObsolete==False to stdout.
    '''
    x = x[x['isObsolete'] == False]
    print(len(x), "terms are non-obsolete", file = sys.stderr)
    x = x[cols]
    x.to_csv(sys.stdout, index = False, sep='\t')

def print_non_obsolete_report(x, header, content):
    '''
    Prints specified columns of x where isObsolete==False to stdout in
    the report format.  Report format:
    
    header
    content
    ----

    where header is constructed from a set of columns
    and content is some long description

    '''
    x = x[x['isObsolete'] == False]
    print(len(x), "terms are non-obsolete", file = sys.stderr)
    for i, row in x.iterrows():
        row_str = f"{'; '.join(row[header])}\n{row[content]}\n----"
        print(row_str, file = sys.stdout)


def read_ids():
    '''
    Reads GO ids from a column in a tsv file
    '''
    ids_passed = args.ids is not None
    tsv_passed = (args.idtsv is not None) & (args.idcol is not None)
    wrong_args = ids_passed & ((args.idtsv is not None) | (args.idcol is not None))
    if wrong_args:
        print('Please specify comma-separated terms (-ids) or a column in a file (-idtsv and -idcol)')
        sys.exit()
    elif ids_passed:
        ids = args.ids
        return ids
    elif tsv_passed:
        ids = pd.read_table(args.idtsv)[args.idcol].str.cat(sep=',')
        return ids
    else:
        print('Please specify comma-separated terms (-ids) or a column in a file (-idtsv and -idcol)')
        sys.exit()

# We define the main parser

parser = argparse.ArgumentParser(
    description = '''This script provides a custom CLI for QuickGO API.  It builds an
URL request based on provided arguments, sends it to QuickGO, and
processes the response.  ''',
    epilog = '''Author: Ivan Tsers
e-mail: tsers@evolbio.mpg.de''',
    formatter_class = RawTextHelpFormatter
)

# We will use subcommands (subparsers) for our canned API requests
subparsers = parser.add_subparsers(dest = 'command')

# We add a subparser for the 'chart' request
chart = subparsers.add_parser('chart', description = '''Download a png
chart of a GO term. If multiple GO terms are scpecified, all of them
will appear at the same chart.''')
chart.add_argument('-ids', type = str, help = 'comma-separated GO ids')
chart.add_argument('-idtsv', type = str, default = None,
                    help = 'name of a tsv file containing a column of GO terms')
chart.add_argument('-idcol', type = str, default = None,
                    help = 'name of a GO terms column in a tsv file')
chart.add_argument('-bh', type = int, help = 'term box height in pixels')
chart.add_argument('-bw', type = int, help = 'term box width in pixels')
chart.add_argument('-fs', type = int, help = 'text font size in pixels')
chart.add_argument('-out', type = str, default = 'chart.png', help = 'output file')
chart.add_argument('-c', action = 'store_true', help = 'show children')
chart.add_argument('-nokey', action = 'store_false', help = 'hide key (legend)')

# We add a subparser for the 'downloadSearch' request (only swissprot annotations!)
swissprot = subparsers.add_parser('swissprot', description =
                                   '''Download a tsv table of
                                   Swiss-Prot annotations related to
                                   the term and its children.''')
swissprot.add_argument('-ids', type = str, help = 'comma-separated GO ids')

# We add a subparser for the 'coterms' request
coterms = subparsers.add_parser('coterms', description = 'Get co-occurring terms.')
coterms.add_argument('-id', type = str, help = 'a target GO id')
coterms.add_argument('-t', type = float, default = 0.0, help = 'similarity threshold')
coterms.add_argument('-s', type = str, default = 'ALL', help = 'annotation source (ALL or MANUAL)')

# We add a subparser for the 'terms' request, which we use to fetch a term definition
define = subparsers.add_parser('define', description = 'Find definitions of GO terms.')
define.add_argument('-ids', type = str, default = None, help = 'comma-separated GO ids')
define.add_argument('-idtsv', type = str, default = None,
                   help = 'name of a tsv file containing a column of GO terms')
define.add_argument('-idcol', type = str, default = None,
                   help = 'name of a GO terms column in a tsv file')
define.add_argument('-report', action="store_true",
                   help = 'format the output as a report instead of a table')

# We add a subparser for the 'search' request
search = subparsers.add_parser('search', description = 'Search GO terms by keywords in description.')
search.add_argument('-q', type = str, default = None, help = 'some value to search for in the ontology')
search.add_argument('-l', type = int, default = 25, help = 'results per page [1-600]')
search.add_argument('-p', type = int, default = 1, help = 'the results page to retrieve')

# We add a subparser for the 'descendants' request
descendants = subparsers.add_parser('descendants', description =
                                    '''Get all descendants of GO terms. Attention: the queried terms are
                                    also descendants of themselves!''')
descendants.add_argument('-ids', type = str, default = None, help = 'comma-separated GO ids')
descendants.add_argument('-relations', type = str, default = "is_a,part_of,occurs_in,regulates",
                         help = '''comma-separated ontology relationships (any combination of "is_a",
"part_of", "occurs_in", "regulates)" ''')
descendants.add_argument('-idtsv', type = str, default = None,
                   help = 'name of a tsv file containing a column of GO terms')
descendants.add_argument('-idcol', type = str, default = None,
                   help = 'name of a GO terms column in a tsv file')

# We add a subparser for the 'ancestors' request
ancestors = subparsers.add_parser('ancestors', description =
                                    '''Get all ancestors of GO terms. Attention: the queried terms are
                                    also ancestors of themselves!''')
ancestors.add_argument('-ids', type = str, default = None, help = 'comma-separated GO ids')
ancestors.add_argument('-relations', type = str, default = "is_a,part_of,occurs_in,regulates",
                         help = '''comma-separated ontology relationships (any combination of "is_a",
"part_of", "occurs_in", "regulates)" ''')
ancestors.add_argument('-idtsv', type = str, default = None,
                   help = 'name of a tsv file containing a column of GO terms')
ancestors.add_argument('-idcol', type = str, default = None,
                   help = 'name of a GO terms column in a tsv file')

# We add a subparser for the 'children' request
children = subparsers.add_parser('children', description = 'Get children of GO terms.')
children.add_argument('-ids', type = str, default = None, help = 'comma-separated GO ids')
children.add_argument('-idtsv', type = str, default = None,
                   help = 'name of a tsv file containing a column of GO terms')
children.add_argument('-idcol', type = str, default = None,
                   help = 'name of a GO terms column in a tsv file')

# We parse a subcommand. If there is none, we print help
args = parser.parse_args(args = None if sys.argv[1:] else ['--help'])

# We parse arguments for the subcommand. If there are none, we print help
if len(sys.argv) == 2:
    subparsers.choices[sys.argv[1]].print_help()
    sys.exit(1)

# We construct our requests based on the provided commands/arguments
# We start with the basic QuickGO services URL
requestURL = "https://www.ebi.ac.uk/QuickGO/services/"

if args.command == 'chart':
    requestURL += 'ontology/go/terms/{ids}/chart'
    ids = read_ids()
    params = {'ids': ids,
              'showKey': args.nokey,
              'termBoxHeight': args.bh,
              'termBoxWidth': args.bw,
              'showChildren': args.c,
              'fontSize': args.fs}
    headers = {'Accept': 'application/json'}

if args.command == 'swissprot':
    requestURL += 'annotation/downloadSearch'
    params = {'includeFields': 'goName',
              'geneProductType': 'protein',
              'geneProductSubset': 'Swiss-Prot',
              'goId': args.ids,
              'goUsage': 'descendants',
              'selectedFields': 'goId,goName,name'}
    headers = {'Accept': 'text/tsv'}

if args.command == 'coterms':
    requestURL += 'annotation/coterms/' + args.id
    params = {'source': args.s,
              'similarityThreshold': args.t}
    headers = {'Accept': 'application/json'}

if args.command == 'define':
    requestURL += 'ontology/go/terms/'
    ids = read_ids()
    requestURL += ids
    params = ''
    headers = {'Accept': 'application/json'}

if args.command == 'search':
    requestURL += 'ontology/go/search/'
    params = {'query': args.q,
              'limit': args.l,
              'page': args.p}
    headers = {'Accept': 'application/json'}

if args.command == 'descendants':
    requestURL += 'ontology/go/terms/'
    ids = read_ids()
    requestURL += ids + "/descendants"
    params = {'relations': args.relations}
    headers = {'Accept': 'application/json'}


if args.command == 'ancestors':
    requestURL += 'ontology/go/terms/'
    ids = read_ids()
    requestURL += ids + "/ancestors"
    params = {'relations': args.relations}
    headers = {'Accept': 'application/json'}

if args.command == 'children':
    requestURL += 'ontology/go/terms/'
    ids = read_ids()
    requestURL += ids + "/children"
    params = ''
    headers = {'Accept': 'application/json'}


# We will receive the return's content as bytes
content = bytearray()

# We send the request and stream it. We print the number of received
# bytes to track the progress
print("Sending the request...", file = sys.stderr)
with requests.get(requestURL, params = params, headers = headers,
                  stream = True) as r:
    if not r.ok:
        r.raise_for_status()
        sys.exit()

    for i in r.iter_content():
       content.extend(i)
       print (len(content), end = " Bytes received...\r", file = sys.stderr)
print (len(content), "Bytes received", file = sys.stderr)

# We print the output
if args.command == 'swissprot':
    # We cast a table using the bytes from the API response
    print('Formatting the output...', file = sys.stderr)
    df = pd.read_csv(BytesIO(content), sep = '\t')
    df_uniq = df.drop_duplicates()
    df_uniq.to_csv(sys.stdout, sep = '\t', index = False)

elif args.command == 'coterms':
    print('Formatting the output...', file = sys.stderr)
    json = json.load(BytesIO(content))["results"]
    df = pd.DataFrame.from_records(json)
    df.to_csv(sys.stdout, sep = '\t', index = False)

elif args.command == 'define':
    print('Formatting the output...', file = sys.stderr)
    json = json.load(BytesIO(content))["results"]
    dfs = []
    for record in json:
        dfs.append(pd.json_normalize(record))
    df = pd.concat(dfs)

    if args.report:
        print_non_obsolete_report(df, ["id", "aspect", "name"], "definition.text")
        
    else:
        print_non_obsolete_table(df, ["id", "aspect", "name", "definition.text"])

elif args.command == 'search':
    nhits = json.load(BytesIO(content))["numberOfHits"]
    print(nhits, "terms found", file = sys.stderr)
    json = json.load(BytesIO(content))["results"]
    df = pd.DataFrame.from_records(json)
    print_non_obsolete_table(df, ["id", "aspect", "name"])

elif args.command == 'descendants':
    nhits = json.load(BytesIO(content))["numberOfHits"]
    print(nhits, "terms queried for descendants", file = sys.stderr)
    json = json.load(BytesIO(content))["results"]
    df = pd.json_normalize(json, record_path = 'descendants', meta = ['id'])
    print(len(df), "total descendants found", file = sys.stderr)
    df.columns = ['descendant', 'id']
    df = df[['id', 'descendant']]
    df.to_csv(sys.stdout, sep='\t', index = False)

elif args.command == 'ancestors':
    nhits = json.load(BytesIO(content))["numberOfHits"]
    print(nhits, "terms queried for ancestors", file = sys.stderr)
    json = json.load(BytesIO(content))["results"]
    df = pd.json_normalize(json, record_path = 'ancestors', meta = ['id'])
    print(len(df), "total ancestors found", file = sys.stderr)
    df.columns = ['ancestor', 'id']
    df = df[['id', 'ancestor']]
    df.to_csv(sys.stdout, sep='\t', index = False)

elif args.command == 'children':
    nhits = json.load(BytesIO(content))["numberOfHits"]
    print(nhits, "terms queried for children", file = sys.stderr)
    json = json.load(BytesIO(content))["results"]
    df = pd.DataFrame()
    have_children = 0
    for result in json:
        result_id = result['id']
        if 'children' in result:
            have_children = have_children + 1
            # Flatten the children data
            children_data = result['children']
            children_df = pd.json_normalize(children_data)
            children_df['query_id'] = result_id
            children_df = children_df[['query_id', 'id', 'name']]
            children_df = children_df.rename(columns = {'id': 'child_id', 'name': 'child_name'})
            # Concatenate with the main DataFrame
            df = pd.concat([df, children_df], ignore_index = True)
    print(have_children, "of the terms have children", file = sys.stderr)
    print(len(df), "children found", file = sys.stderr)
    df.to_csv(sys.stdout, sep='\t', index = False)

else:
    with open(args.out, 'wb') as o:
        o.write(content)
        o.close()

# query_quickgo

This Python3 script provides builds URL requests for QuickGO API based
on provided arguments, sends it to QuickGO, and processes the
response.

## How to install
Get the dependencies: Python (at least 3.8) and Python packages:
'''
pip install pandas
pip install requests
'''
Clone the repository
'''
git clone https://github.com/IvanTsers/query_quickgo
cd query_quickgo
'''
## An example run
'''
python query_quickgo.py search respiration
'''

There are eight subcommands: `chart`, `swissprot`, `coterms`,
`define`, `search`, `descendants`, `ancestors`, and `children`. Help
is available for every command.
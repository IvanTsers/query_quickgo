# query_quickgo

This Python3 script builds URL requests for QuickGO API based
on provided arguments, sends it to QuickGO, and processes the
response.
]
## How to install
Get the dependencies: Python (at least 3.8) and Python packages:
```
pip install pandas
pip install requests
```
Clone the repository
```
git clone https://github.com/IvanTsers/query_quickgo
cd query_quickgo
```
An example run:
```
python query_quickgo.py search -q respiration
```
There are eight subcommands: `chart`, `swissprot`, `coterms`,
`define`, `search`, `descendants`, `ancestors`, and `children`. Help
is available for every command.

## Run using Docker

The script and all its dependencies can be containerized.
To build your local copy of the image `query_quickgo`:
```
git clone https://github.com/IvanTsers/query_quickgo
cd query_quickgo
sudo docker build -t query_quickgo -f docker/Dockerfile --force-rm .
```
An example run:
```
sudo docker run --rm query_quickgo search -q respiration
```
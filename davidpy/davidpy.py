import os
import pandas as pd
import sys
import inspect
import re
import configparser
from suds.client import Client


def check_converter():
    # Checks for existing of file for converting Gene names to Ensembl IDs and reverse
    
    dir_path = os.path.split(os.path.abspath(inspect.getsourcefile(check_converter)))[0]
    converter_filename = ".ensembl_to_hgnc_human.txt"
    if os.path.isfile(dir_path+'/'+converter_filename):
        print("Ensembl file found")
        return pd.read_csv(dir_path+'/'+converter_filename, sep='\t')
    else:
        try:
            import biomart, sys
            server = biomart.BiomartServer( "http://uswest.ensembl.org/biomart")
            ensembl = server.datasets['hsapiens_gene_ensembl']
            r = ensembl.search({'attributes': ['external_gene_name', 'ensembl_gene_id']})
            convert_df = pd.read_csv(r.url, sep='\t', names=["Gene name", "Gene stable ID"]).dropna()
            convert_df.to_csv(dir_path+'/'+converter_filename, sep='\t', index=False)

            if sys.platform.startswith("win"): # Hiding file in Windows
                try:
                    import subprocess
                    subprocess.call(['attrib', '+h', dir_path+'/'+converter_filename])   
                except:
                    pass

            print("Ensembl file downloaded from Biomart")
            return convert_df
        except:
            print("Couldn't find or download Ensembl file")
            return False


def converter(genes_list_or_path, reverse=False):
    import re
    
    # Checking if input is a file and trying to open it
    if os.path.isfile(genes_list_or_path):
        with open(genes_list_or_path) as input_file:
            genes_string = input_file.read()
    else:
        genes_string = genes_list_or_path
        
    # Splitting string to list of genes
    genes_list = re.findall(r"[\w\-\_']+", genes_string)
    
    global ensembl_table
    global temporary_conv_df
    
    # Checking if dataframe already exsists
    try:
        ensembl_table
    except:
        ensembl_table = check_converter()
    
    # Defining the source of table with gene IDs
    # If we cannot gain a table with ALL genes 
    # (e.g. no rights to write file)...
    if type(ensembl_table) != bool:
        temporary_conv_df = ensembl_table
    # ... trying to create the table with OUR genes
    else:
        try:
            temporary_conv_df
        except:
            print("Connected to Biomart")
            import biomart
            server = biomart.BiomartServer("http://uswest.ensembl.org/biomart")
            ensembl = server.datasets['hsapiens_gene_ensembl']
            r = ensembl.search({'filters': {'external_gene_name': genes_list},
                                'attributes': ['external_gene_name', 'ensembl_gene_id']})
            temporary_conv_df = pd.read_csv(r.url, sep='\t', names=["Gene name", "Gene stable ID"]).dropna()

    if not reverse:
        genes_list_conv = temporary_conv_df['Gene stable ID'].loc[temporary_conv_df['Gene name'].isin(genes_list)].to_list()
    else:
        genes_list_conv = temporary_conv_df['Gene name'].loc[temporary_conv_df['Gene stable ID'].isin(genes_list)].to_list()

    return list(set(genes_list_conv))


def set_config(**kwargs):
    import configparser
    
    if not sys.platform.startswith('linux'):
        print("Your OS is not Linux. If you want to change defaults, edit module's .py file.")
        return
    else:
        path = os.path.expanduser("~") + '/.config/DAVID.ini'
        config = configparser.ConfigParser()
        if os.path.exists(path):
            config.read_file(open(path))
        else:
            config["DEFAULT"] = {"email": "",
                                 "threshold": 0.1,
                                 "count": 2,
                                 "overlap": 3,
                                 "initialSeed": 3,
                                 "finalSeed": 3,
                                 "linkage": 0.5,
                                 "kappa": 50}
            if not "email" in kwargs.keys():
                email = str(input("Please, insert your email: "))
                config["DEFAULT"]["email"] = email
        
    
    # Changing parameters
    if kwargs:
        for key in config["DEFAULT"]:
            if key in kwargs.keys():
                config["DEFAULT"][key] = str(kwargs[key])
                del kwargs[key]
                #print(key+":", config["DEFAULT"][key])
    with open(path, 'w') as configfile:
        config.write(configfile)
    if kwargs.keys():
        print("Wrong parameter(s):", ", ".join(kwargs.keys()))


def check_config():
    import configparser
    path = ''
    if sys.platform.startswith('linux'):
        path = os.path.expanduser("~") + '/.config/DAVID.ini'
        if not os.path.exists(path):
            set_config()
        config = configparser.ConfigParser()
        config.read_file(open(path))
        config = dict(config["DEFAULT"])
    else:
        # Change this part if you use OS except of Linux
        config = {"email": "",
                  "threshold": 0.1,
                  "count": 2,
                  "overlap": 3,
                  "initialSeed": 3,
                  "finalSeed": 3,
                  "linkage": 0.5,
                  "kappa": 50}
        if not config['email']:
            email = str(input("Please, insert your email and register at http://david-d.ncifcrf.gov/webservice/register.htm\n"))
            config["email"] = email
    return config


def DAVID_start(input_list_path, input_bg_path=None, email=None):
    # Reading configs
    global DAVID_conf
    DAVID_conf = check_config()
    if not email:
        email = DAVID_conf["email"]
    
    # Reading file or string with genes and converting to Ensembl format
    input_list_ids = ",".join(converter(input_list_path))
    print('List loaded')
    if input_bg_path:
        input_bg_ids = ",".join(converter(input_bg_path))
        print('Using file background')
    else:
        print('Using default background')
    
    # Establishing connection and trying to authenticate
    client = Client(
        'https://david-d.ncifcrf.gov/webservice/services/DAVIDWebService?'
        'wsdl')
    client.wsdl.services[0].setlocation(
        'https://david-d.ncifcrf.gov/webservice/services/DAVIDWebService.'
        'DAVIDWebServiceHttpSoap11Endpoint/')
    auth = client.service.authenticate(email)
    if "Failed" in auth:
        auth = "Failed. For user registration, go to http://david-d.ncifcrf.gov/webservice/register.htm"
    print('User Authentication:', auth)
    
    # Sending list of genes and background to the server
    print('Percentage mapped(list):', client.service.addList(
        input_list_ids, 'ENSEMBL_GENE_ID', 'LIST1', 0))
    if input_bg_path:
        print('Percentage mapped(background):', client.service.addList(
            input_bg_ids, 'ENSEMBL_GENE_ID', 'BACKGROUND1', 1))
    return client


def get_chart(DAVID, threshold=None, count=None):
    if not threshold:
        threshold = DAVID_conf["threshold"]
    if not count:
        count = DAVID_conf["count"]
    chart = DAVID.service.getChartReport(threshold, count)
    df = pd.DataFrame.from_dict(chart)
    df.columns = [i[0] for i in df.loc[0]]
    df = df.applymap(lambda x: x[1])
    new_IDs = []
    for ID in df['geneIds']:
        new_IDs.append(", ".join(converter(ID, reverse=True)))
    df['geneIds'] = new_IDs
    cols = ["categoryName", "termName", "geneIds", "percent", "ease", "benjamini"]
    df = df[cols].sort_values("benjamini")
    df.columns = ["Cateogry", "Term", "Genes", "Percent", "P-Value", "Benjamini"]
    return df


def main():
    import argparse
    parser = argparse.ArgumentParser(description='DAVID Functional Annotation Chart retrieving script')
    parser.add_argument('-i', type=str, help='Input list of genes (file or "GENE1,GENE2,ETC")', required=True)
    parser.add_argument('--bg', type=str, help='Background (file or "GENE1,GENE2,ETC")')
    parser.add_argument('--tsv', help='Save to tsv', action="store_true")
    parser.add_argument('--csv', help='Save to csv', action="store_true")
    parser.add_argument('--full', help='Show all columns of the table', action="store_true")

    args = parser.parse_args()
    
    
    if not args.i:
        DAVID = DAVID_start(args.i)
    else:
        DAVID = DAVID_start(args.i, args.bg)
        
    df = get_chart(DAVID)
    
    print("First 20 terms:")
    if args.full:
        pd.options.display.max_columns = None
        print(df.head(20))
    else:
        print(df.head(20)[['Term', 'Percent', 'Benjamini']])
        
    
    if args.tsv:
        df.to_csv("DAVID_chart.tsv", sep='\t', index=False)
    elif args.csv:
        df.to_csv("DAVID_chart.csv", index=False)

if __name__ == '__main__':
    main()

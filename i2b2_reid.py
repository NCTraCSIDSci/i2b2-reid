import cx_Oracle
import pyodbc
import csv
import configparser
import os
import argparse
import datetime
import time
import logging

def load_inis(ini_path):
    flist = os.listdir(ini_path)
    return flist

def oracle_connect(config, section):
    host = config[section]['host']
    port = config[section]['port']
    sid = config[section]['sid']
    user = config[section]['user']
    pwd = config[section]['pwd']

    dsn_tns = cx_Oracle.makedsn(host, port, sid)
    conn = cx_Oracle.connect(user, pwd, dsn_tns)
    return(conn)

def mssql_connect(config, section):
    host = config[section]['host']
    port = config[section]['port']
    database = config[section]['database']
    user = config[section]['user']
    pwd = config[section]['pwd']

    constr = 'DRIVER={SQL Server};SERVER='+host+';DATABASE='+database+';PORT='+port+';UID='+user+';PWD='+ pwd
    conn = pyodbc.connect(constr, autocommit=True)
    return(conn)

def get_i2b2_patient_ids(conn, qmid, pat_sql):
    cursor=conn.cursor()
    cursor.execute(pat_sql, [query_master_id])
    #colnames = [d[0] for d in cursor.description]
    data = cursor.fetchall()
    darr = [d[0] for d in data]

    return(darr)

def get_ehr_patients(conn, pat_ids, pat_sql):
    i=0
    pats=[]
    cursor=conn.cursor()
    for pid in pat_ids:
        cursor.execute(pat_sql, pid)
        data = cursor.fetchall()
        if( data != None and len(data) > 0 ):
            pats.append(data[0])

    colnames = [d[0] for d in cursor.description]
    data = cursor.fetchall()
    #data = cursor.fetchmany(10)
    result = {'header':colnames, 'data':pats}
    return(result)

def export_pats(output_file, pats):
    header = pats['header']
    rows = pats['data']
    with open(output_file,'w',newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        csvwriter.writerow(header)
        for row in rows:
            csvwriter.writerow(row)
    return(0)

##################################################################################
# command line args
clparse = argparse.ArgumentParser(description='re-identify i2b2 query')
clparse.add_argument('--config', required=True, help='name of config file with database info')
clparse.add_argument('--log', required=True, help='name of the log file, logging information will be appended to file')
args = clparse.parse_args()

# setup logging
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, filename=args.log, datefmt="%Y-%m-%d %H:%M:%S")
logging.info("i2b2 re-identification run: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")) )

# get config
config_fname = args.config
config = configparser.ConfigParser()
config.read(config_fname)

input_dir = config['reid']['input_dir']
output_dir = config['reid']['output_dir']
done_dir = config['reid']['done_dir']

#get db connections
if config['db_i2b2']['dbms'] == 'oracle':
    i2b2_conn = oracle_connect(config,'db_i2b2')
elif config['db_i2b2']['dbms'] == 'mssql':
    i2b2_conn = mssql_connect(config,'db_i2b2')
else:
    logging.error("ERROR: invalid database type for db_i2b2")
    exit(1)

if config['db_ehr']['dbms'] == 'oracle':
    ehr_conn = oracle_connect(config,'db_ehr')
elif config['db_ehr']['dbms'] == 'mssql':
    ehr_conn = mssql_connect(config,'db_ehr')
else:
    logging.error("ERROR: invalid database type for db_ehr")
    exit(1)

#load sql files
with open(config['sql']['i2b2_patients'],'r') as f:
    sql_i2b2_pats = f.read()

with open(config['sql']['ehr_patients'],'r') as f:
    sql_ehr_pats = f.read()

ini_files = []
ini_files = load_inis(input_dir)

if not ini_files:
    logging.info("No ini files to process")

# process re-id requests, must be in .ini format
for ini in ini_files:
    file_prefix = os.path.splitext(ini)[0]
    ini_file = os.path.join(input_dir,ini)
    timestr = time.strftime("%Y_%m_%d_%H_%M_%S")
    done_file = os.path.join(done_dir, file_prefix + '_' + timestr + '.ini')

    logging.info("---------------------------------------------------------")
    logging.info("Processing ini: {}".format(ini_file) )

    ## get ini params ##
    config = configparser.ConfigParser()
    config.read(ini_file)

    ## move ini file to completed directory
    #os.rename(ini_file, done_file)
    logging.info("Moved ini file to:  {}".format(done_file))


    # get query_master_id of query with saved patient set
    if config.has_option('DEFAULT','query_master_id'):
        query_master_id = config['DEFAULT']['query_master_id']
    else:
        logging.error("ERROR: Invalid file format, missing [default] query_master_id, ini file: {}".format(ini_file) )
        # skip to next ini file
        continue

    logging.info('query_master_id = {}'.format(query_master_id))

    output_file = os.path.join(output_dir, file_prefix + '_' + timestr + '.csv')

    logging.info("Start export for i2b2 query master id: {}".format(query_master_id))

    try:
        # get i2b2 cohort
        pat_ids = get_i2b2_patient_ids(i2b2_conn,query_master_id, sql_i2b2_pats)

        pats = get_ehr_patients(ehr_conn, pat_ids, sql_ehr_pats)
        export_pats(output_file, pats)

        logging.info("Export to file {} complete".format(output_file))

    except Exception as e:
        #not currently handling exceptions
        raise(e)


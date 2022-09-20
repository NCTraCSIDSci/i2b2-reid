# i2b2-reid

Setup:
1) create configuration file with connection information to database(s), pointers to sql files used in re-identification and re-id process information.  See example ini file here: https://github.com/NCTraCSIDSci/i2b2-reid/blob/main/example_config.ini
2) create SQL to extract i2b2 patient set from your i2b2 database, see example here:  https://github.com/NCTraCSIDSci/i2b2-reid/blob/main/example_i2b2.sql
3) create SQL to export the identified patient set from your EHR database, see example here:  https://github.com/NCTraCSIDSci/i2b2-reid/blob/main/example_ehr.sql
4) create a re-id job request ini file, see example here:  
5) run the program like this:

python i2b2_reid.py --config <name of config ini file> --log <name of log file>

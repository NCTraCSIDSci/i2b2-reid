-- THIS SQL IS USED TO EXPORT IDENTIFIED PATIENTS (AND ANY OTHER INFORMATION) FROM YOUR EHR DATABASE
-- THERE MUST BE A BIND VARIABLE IN THE WHERE CLAUSE.  THIS BIND VARIABLE WILL BE POPULATED WITH THE PATIENT IDENTIFIER RETURNED FROM THE I2B2 QUERY
-- FOR ORACLE USE :bind_pid
-- FOR MSSQL AND OTHER DATABASES USE ?

select distinct
  getdate() as EXTRACT_DATE,
  patient_table.MRN,
  patient_table.LIVING_STATUS,
  patient_table.FIRST_NAME,
  patient_table.LAST_NAME,
  patient_table.BIRTH_DATE,
  patient_table.SEX,
  patient_table.RACE,
  patient_table.ETHNICITY
from
  patient_table
where
  patient.pat_id = ?

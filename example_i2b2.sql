-- THIS SQL IS USED TO PULL THE PATIENT SET FOR AN I2B2 QUERY_MASTER_ID
-- TWO RULES THIS SQL MUST FOLLOW:
-- 1) RETURN A SINGLE COLUMN, THIS IS A PATIENT IDENTIFIER THAT WILL BE PASSED TO THE EHR SQL
-- 2) HAVE THE BIND VARIABLE (:bind_qmid) IN THE WHERE CLAUSE

select distinct
        patient_mapping.patient_ide as patient_id  -- MUST RETURN A SINGLE PATIENT ID,  THIS WILL BE PASSED THROUGH TO THE EHR SQL
from
        qt_query_master qt_query_master
        join qt_query_instance qt_query_instance on qt_query_master.query_master_id=qt_query_instance.query_master_id
        join qt_query_result_instance qt_query_result_instance on qt_query_instance.query_instance_id=qt_query_result_instance.query_instance_id
        join qt_patient_set_collection qt_patient_set_collection on qt_query_result_instance.result_instance_id = qt_patient_set_collection.result_instance_id
        join patient_mapping patient_mapping on qt_patient_set_collection.patient_num = patient_mapping.patient_num
where
        query_master_id=:bind_qmid                -- MUST HAVE THIS BIND VALUE, THIS WILL VALUE WILL BE FROM THE I2B2 REID JOB INI FILE
        and patient_ide_status='A'

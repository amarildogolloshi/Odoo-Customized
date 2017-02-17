import mysql.connector
from mysql.connector import errorcode
from unidecode import unidecode
import csv
import os
import datetime
import collections
import time
import datetime
import psycopg2
import psycopg2.extras





class generate_csv():
    beg_start_time = time.time()
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    print cur_dir
    os.chdir(cur_dir)
    
    time1 = datetime.datetime.time(datetime.datetime.now())
 #creating csv and import to folder /csv/   
    def insert(csvfile, dictvals):
        # order the files by their migration #
        fieldnames = [] 
        res = dictvals[0] 
        for key in res.keys():
            fieldnames.append(key)
            
        if not os.path.exists(os.getcwd()+'/csv_data/'):
            os.makedirs(os.getcwd()+'/csv_data/')
        # =============================
        print 'writing to...',csvfile
        with open(os.getcwd()+'/csv_data/'+csvfile+'.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for index in range(len(dictvals)):
                print index, dictvals[index]
                writer.writerow(dictvals[index])
                
        print '...write completed.'
        return
#connection    
    print 'Connecting to database...'  
            
#     postgre_conn = psycopg2.connect (user='openerp', password='openerp',
#                                              host='192.168.100.253',port=5432,
#                                              database='EPFC')
    mysql_conn = mysql.connector.connect(user='prog', password='berth482',
                                                 host='192.168.100.7', port=3306,
                                                 database='hrms')

    print 'Connection Established.'
   
    mysql_cursor =  mysql_conn.cursor()


#======================
## epfc and mysql Brand
    print 'Processing...religion'
    pgquery = ("""SELECT REPLACE(`cReligion`,'M','R') as id , cReligionDesc as name FROM genReligion ORDER BY creligiondesc""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    print 
    emp_rlgn = []
    emp_rlgn_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        emprlgn = {}
#         pbrand = {'active': True}
#         pbrand['id'] = ('{}'.format(ctr_key))
#         pbrand['old_brand_code'] = ('{}'.format(old_brand_code))
        emprlgn['id'] = ('{}'.format(id))
        emprlgn['name'] = ('{}'.format(name))
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_rlgn.append(emprlgn)
        
    insert('employee.religion',emp_rlgn)
     
# #=====================
    print 'Processing...Employee Education Level'
    pgquery = ("""select replace(concat('employee_education_level_', lower(cleveldesc),'id'),' ','')as id, cleveldesc as name 
                from geneduclevel order by cleveldesc""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_educ_lvl = []
    emp_educ_lvl_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empeduclvl = {}
#         pbrand = {'active': True}
#         pbrand['id'] = ('{}'.format(ctr_key))
#         pbrand['old_brand_code'] = ('{}'.format(old_brand_code))
        empeduclvl['id'] = ('{}'.format(id))
        empeduclvl['name'] = ('{}'.format(name))
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_educ_lvl.append(empeduclvl)
        
    insert('employee.education.level',emp_educ_lvl)
    
#======================
## epfc and mysql Brand
    print 'Processing...Employee Education Course'
    pgquery = ("""select lower(concat('employee_education_course_',replace(replace(ccourse, ' ', ''),'.',''),'','id')) id,
                    ccourse name,nnumyears noofyears from gencourse order by name;""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_educ_course = []
    emp_educ_course_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name,noofyears) in pgsql_recs:
        ctr_key+=1
        empeduccourse = {}
        empeduccourse['id'] = ('{}'.format(id))
        empeduccourse['noofyears'] = ('{}'.format(noofyears))
        empeduccourse['name'] = ('{}'.format(name))
        
        
        
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_educ_course.append(empeduccourse)
        
    insert('employee.education.course',emp_educ_course)
     
# #=====================

    print 'Processing...Employee Medical Blood'
    pgquery = ("""select distinct lower(concat('employee_medical_blood_',replace(replace(cbloodtype, ' ', ''),'.',''),'','id')) id,
                (cbloodtype) name from empmedinfo order by name""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_med_bld = []
    emp_med_bld_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empmedbld = {}
        empmedbld['id'] = ('{}'.format(id))
        empmedbld['name'] = ('{}'.format(name))
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_med_bld.append(empmedbld)
        
    insert('employee.medical.blood',emp_med_bld)
     
# #=====================

    print 'Processing...Employee Medical Allergy'
    pgquery = ("""select replace(concat('employee_medical_allergy_', lower(callergy),'id'),' ','')as id, callergy as name 
                from empmedallergy order by name""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_med_alrgy = []
    emp_med_alrgy_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empmedalrgy = {}
        empmedalrgy['id'] = ('{}'.format(id))
        empmedalrgy['name'] = ('{}'.format(name))
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_med_alrgy.append(empmedalrgy)
        
    insert('employee.medical.allergy',emp_med_alrgy)
# #=====================

    print 'Processing...Employee Medical Healthprob'
    pgquery = ("""select replace(replace(concat('employee_medical_healthprob_', lower(chealthprob),'id'),' ',''),'.','')as id, chealthprob as name 
                from empmedhealthprob order by name""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_med_hlthprb = []
    emp_med_hlthprb_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empmedhlthprb = {}
        empmedhlthprb['id'] = ('{}'.format(id))
        empmedhlthprb['name'] = ('{}'.format(name))
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_med_hlthprb.append(empmedhlthprb)
        
    insert('employee.medical.healthprob',emp_med_hlthprb)
# #=====================

    print 'Processing...Employee Skills Category'
    pgquery = ("""select replace(concat('employee_skills_categ_', lower(csklcatcode),'id'),' ','')as id, csklcategory as name 
                from empskillscategory order by name""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_skl_categ = []
    emp_skl_categ_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empsklcateg = {}
        empsklcateg['id'] = ('{}'.format(id))
        empsklcateg['name'] = ('{}'.format(name))
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_skl_categ.append(empsklcateg)
        
    insert('employee.skills.category',emp_skl_categ)
# #=====================

    print 'Processing...Employee Skills'
    pgquery = ("""select lower(concat('employee_skills_',replace(cskill, ' ', ''),'','id')) id,
                replace(concat('employee_skills_categ_', lower(left(cskillcode,3)),'id'),' ','') as skill_categ_id, cskill name 
                from empskillslist""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_skl = []
    emp_skl_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,skill_categ_id,name) in pgsql_recs:
        ctr_key+=1
        empskl = {}
        empskl['id'] = ('{}'.format(id))
        empskl['skill_category_id:id'] = ('{}'.format(skill_categ_id))
        empskl['name'] = ('{}'.format(name))
       
#         key = pbrand['old_brand_code']
#         if key not in product_brandpg_key:
#             product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
#         pbrand['create_date'] = 'NOW()'
            
        emp_skl.append(empskl)
        
    insert('employee.skills',emp_skl)
 # #=====================

    print 'Processing...Employee Seminar Config'
    pgquery = ("""select lower(concat('employee_conf_seminar_',replace(replace(cseminartitle, ' ', ''),'.',''),'','id')) id, cseminartitle name 
                from empseminars order by name""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_smnr = []
    emp_smnr_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empsmnr = {}
        empsmnr['id'] = ('{}'.format(id))
        empsmnr['name'] = ('{}'.format(name))
            
        emp_smnr.append(empsmnr)
        
    insert('employee.conf.seminar',emp_smnr)   
 # #=====================

    print 'Processing...Employee External Jobs'
    pgquery = ("""SELECT DISTINCT LOWER(CONCAT('employee_external_job_',REPLACE(REPLACE(coccupation, ' ', ''),'.',''),'','id')) id, coccupation NAME 
                FROM empparents WHERE coccupation NOT IN ('-','.') ORDER BY NAME;""")
    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_ext_job = []
    emp_ext_job_pg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (id,name) in pgsql_recs:
        ctr_key+=1
        empextjob = {}
        empextjob['id'] = ('{}'.format(id))
        empextjob['name'] = ('{}'.format(name))
            
        emp_ext_job.append(empextjob)
        
    insert('employee.external.jobs',emp_ext_job) 
#======================
    print 'Processing...Employee Job Level'
    pgquery = ("""select distinct lower(concat('config_job_level_',replace(replace(jlid, ' ', ''),'.',''),'','id')) id, 
                jlid code, 
                  (case when right(jlid,1) = 0 then concat(jltype,' ',right(jlid,2))
                    when right(jlid,2) not like '0%' and right(jlid,2) > 0  then concat(jltype,' ',right(jlid,2))
                    else concat(jltype,' ',right(jlid,1)) end) name,
                  (case when jltype like '%manager%' then 'config_job_level_m00id' 
                    when jltype like '%professional%' then 'config_job_level_pt0id' 
                    when jltype like '%rank and file%' then 'config_job_level_rf0id' 
                  end) as parent_id   
                from joblevel where jlid is not null  and jlid != '' order by code""")
                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_job_lvl = []
    emp_job_lvl_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
    parent_insrt = [('config_job_level_m00id', 'MANAGERIAL', 'M00', ''),
                    ('config_job_level_pt0id', 'Professional Technical', 'PT0', ''),
                    ('config_job_level_rf0id', 'Rank and File', 'RF0', '')]
    
    for (id,name,code,parent_id) in parent_insrt:
        ctr_key+=1
        parentinsrt = {}
         
        parentinsrt['id'] = ('{}'.format(id))
        parentinsrt['code'] = ('{}'.format(code))
        parentinsrt['name'] = ('{}'.format(name))
        parentinsrt['parent_id:id'] = ('{}'.format(parent_id))
        emp_job_lvl.append(parentinsrt)
        
    for (id,code,name,parent_id) in pgsql_recs:
        ctr_key+=1
        empjoblvl = {}
          
        empjoblvl['id'] = ('{}'.format(id))
        empjoblvl['code'] = ('{}'.format(code))
        empjoblvl['name'] = ('{}'.format(name))
        empjoblvl['parent_id:id'] = ('{}'.format(parent_id))
          
        emp_job_lvl.append(empjoblvl)   
        
    insert('config.job.level',emp_job_lvl)
     
# #=====================
    print 'Processing...Employee Job List'
    pgquery = ("""SELECT DISTINCT LOWER(CONCAT('hr_job_',REPLACE(REPLACE(cjcode, ' ', ''),'.',''),'','id')) id,
                (cjtitle) NAME,
                CASE WHEN jlid IS NULL THEN ''
                     WHEN jlid = '' THEN '' 
                    ELSE LOWER(CONCAT('config_job_level_',REPLACE(REPLACE(jlid, ' ', ''),'.',''),'','id')) END job_level_id,
                (SELECT  LOWER(CONCAT('muti_base.res_company_',REPLACE(REPLACE(cbucode, ' ', ''),'.',''),'','id')) cbusunit 
                    FROM genbusinessunit WHERE cbu = cbucode) company_id
                 FROM empjd a, genjd b WHERE a.`cjd` = b.`cjcode`
                AND a.`cempid` NOT IN (SELECT cempid FROM empseparate)
                AND ddateeffect = (SELECT MAX(ddateeffect) FROM empjd WHERE a.`cempid` = cempid);""")
                                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_job = []
    emp_job_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
        
    for (id,name,job_level_id,company_id) in pgsql_recs:
        ctr_key+=1
        empjob = {}
          
        empjob['id'] = ('{}'.format(id))
        empjob['name'] = ('{}'.format(name))
        empjob['job_level_id:id'] = ('{}'.format(job_level_id))
        empjob['company_id:id'] = ('{}'.format(company_id))
          
        emp_job.append(empjob)   
        
    insert('hr.job',emp_job)
     
# #=====================
    print 'Processing...Employee License'
    pgquery = ("""select lower(concat('employee_conf_license_',replace(replace(clicensecode, ' ', ''),'.',''),'','id')) id, 
                clicensedesc name from genlicenselist""")
                                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    emp_lcnse = []
    emp_lcnse_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
        
    for (id,name) in pgsql_recs:
        ctr_key+=1
        emplcnse = {}
          
        emplcnse['id'] = ('{}'.format(id))
        emplcnse['name'] = ('{}'.format(name))
          
        emp_lcnse.append(emplcnse)   
        
    insert('employee.conf.license',emp_lcnse)
     
# #=====================
    print 'Processing...HR Department'
    pgquery = ("""SELECT CONCAT('hr_department_',a.`cBranchCode`,'id') AS id,
                 a.`cBranchDept` AS NAME ,
                CASE WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('muti') THEN 'muti_base.res_company_branch_mutihomeoffice'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('epfc') THEN 'muti_base.res_company_branch_epfchomeoffice'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('hsi','') THEN 'muti_base.res_company_branch_hondahomeoffice' 
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('bradc','') THEN 'muti_base.res_company_branch_10000001id' 
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('hlrdc','') THEN 'muti_base.res_company_branch_07000001id'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('asi','') THEN 'muti_base.res_company_branch_20000001id'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('siasa') AND a.cbranchdept IN ('greatwall') THEN 'muti_base.res_company_branch_siasagreatwall'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('siasa') AND a.cbranchdept LIKE ('%phoenix%') THEN 'muti_base.res_company_branch_12000024id' 
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('siasa') THEN 'muti_base.res_company_branch_siasahomeoffice'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('ssaiai') THEN 'muti_base.res_company_branch_ssaiaihomeoffice'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('4mratco') THEN 'muti_base.res_company_branch_4mratcohomeoffice'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('care') THEN 'muti_base.res_company_branch_14000006id' 
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('rbn') THEN 'muti_base.res_company_branch_16000001id'
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('cbg uhi') THEN 'muti_base.res_company_branch_cbg'    
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('ckei','asa','vmi','adc','mvcthr-b','ckugmc','psa','arkclick') THEN CONCAT('muti_base.res_company_',LOWER(b.cbucode),'id')
                     WHEN a.`cBrDept` = 'D' AND b.cabbreviation IN ('phoenix') THEN 'muti_base.res_company_branch_pumgashomeoffice'
                     ELSE
                    CONCAT('muti_base.res_company_',LOWER(b.cbucode),'id')
                END company_id
                 FROM GenBranchDept a , GenBusinessUnit b
                 WHERE b.`cBUCode` = a.`cBUCode`
                ORDER BY b.cabbreviation ,NAME;
                """)
                                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    hr_dept = []
    hr_dept_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
        
    for (id,name,company_id) in pgsql_recs:
        ctr_key+=1
        hrdept = {}
        print 'testunidecode', ('{}'.format(unidecode(name)))
        hrdept['id'] = ('{}'.format(id))
        hrdept['name'] = ('{}'.format(unidecode(name)))
        hrdept['company_id:id'] = ('{}'.format(company_id))
          
        hr_dept.append(hrdept)   
#         
    insert('hr.department',hr_dept)
    
# #=====================

    print 'Processing...HR Department'
    pgquery = ("""SELECT a.`cEmpNo` AS id, a.`cEmpNo` AS emp_id, a.`cLastName` AS emp_lastname,
                a.`cFirstName` AS emp_firstname, a.`cMiddle` AS emp_middlename, a.`cNickName` AS company_name,
                IFNULL(
                (SELECT 
             CONCAT('hr_department_',x2.cbranchdept,'id') FROM empbranchdept x2 WHERE  a.`cEmpNo` = x2.cempid
                    AND x2.ddateeffect = (SELECT MAX(x22.ddateeffect) FROM empbranchdept x22 WHERE x2.cempid = x22.cempid)
                    -- para lang ma identify kung belong sya sa dept.
                    AND x2.cbranchdept IN (SELECT a.`cBranchCode`
                FROM GenBranchDept a , GenBusinessUnit b
                WHERE b.`cBUCode` = a.`cBUCode`)
                -- end
                LIMIT 1),'') AS department_id,    
                IFNULL(
                (SELECT  LOWER(CONCAT('hr_job_',REPLACE(REPLACE(cjcode, ' ', ''),'.',''),'','id')) id
                FROM empjd x1, genjd b WHERE x1.`cjd` = b.`cJCode`
                AND x1.cEmpID = a.`cEmpNo`
                -- para lang ma identify kung belong sya sa job
                AND b.cjcode IN (SELECT jd.`cJCode`
                FROM genjd jd , GenBusinessUnit b
                WHERE jd.`cBU` = b.`cBUCode`)
                -- end     
                AND x1.`cEmpID` NOT IN (SELECT cempid FROM empseparate)
                AND ddateeffect = (SELECT MAX(ddateeffect) FROM empjd WHERE x1.`cEmpID` = cempid)
                ),'') AS job_id,    
                c.`nHeight` AS height, c.`nWeight` AS weight, c.`dBirthDate` AS birthday ,
                (CASE WHEN c.`cSex` = 'M' IN (SELECT c.`cSex` FROM EmpPersonalInfo WHERE a.`cEmpNo` = cempid)
                THEN 'Female' ELSE 'Male' END) AS gender,
                c.`cTIN` AS tin_no , REPLACE(c.`cSSSNo`,'-','') sss_no, c.`cHDMFNo` hdmf_no,
                REPLACE(c.`cPhilHealthNo`,'-','') AS phic_no,
                (SELECT 
                CASE WHEN gcs.ccivilstatusdesc LIKE '%widow%'THEN 'widower'  
                ELSE REPLACE(LOWER(gcs.`cCivilStatusDesc`),' ','') END
                 FROM EmpPersonalInfo epi , genCivilStatus gcs
                WHERE epi.`cCivilStatus` = gcs.`cCivilstatus` AND epi.cempid = a.`cEmpNo`) AS marital ,
                REPLACE(c.`cReligion`,'M','R') AS religion_id,
                (CASE WHEN a.cempno IN (SELECT d.cempid FROM empseparate d WHERE dDateEffectivity <= CURDATE()
                AND d.cempid = a.`cEmpNo`)THEN 'FALSE' ELSE 'TRUE' END) AS active                
                FROM empinfo a ,EmpPersonalInfo c
                WHERE LEFT(cempno,1) = 'M'
                AND a.`cEmpNo` = c.`cEmpID`
                ORDER BY a.`cLastName`;""")
                                        
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    hr_emp = []
    hr_emp_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
        
    for (id,emp_id,emp_lastname,emp_firstname,emp_middlename,company_name,department_id,job_id,
            height,weight,birthday,gender,tin_no,sss_no,hdmf_no,phic_no,marital,religion_id,active
         )in pgsql_recs:
        ctr_key+=1
        hremp = {}
        hremp['id'] = ('{}'.format(id))
        hremp['emp_id'] = ('{}'.format(emp_id))
        hremp['emp_lastname'] = ('{}'.format(unidecode(emp_lastname)))
        hremp['emp_firstname'] = ('{}'.format(unidecode(emp_firstname)))
        hremp['emp_middlename'] = ('{}'.format(unidecode(emp_middlename)))
        hremp['company_name'] = ('{}'.format(unidecode(company_name)))
        hremp['department_id:id'] = ('{}'.format(department_id))
        hremp['job_id:id'] = ('{}'.format(job_id))
        hremp['height'] = ('{}'.format(height))
        hremp['weight'] = ('{}'.format(weight))
        hremp['birthday'] = ('{}'.format(birthday))
        hremp['gender'] = ('{}'.format(unidecode(gender)))
        hremp['tin_no'] = ('{}'.format(unidecode(tin_no)))
        hremp['sss_no'] = ('{}'.format(unidecode(sss_no)))
        hremp['hdmf_no'] = ('{}'.format(unidecode(hdmf_no)))
        hremp['phic_no'] = ('{}'.format(unidecode(phic_no)))
        hremp['marital'] = ('{}'.format(unidecode(marital)))
        hremp['religion_id:id'] = ('{}'.format(unidecode(religion_id)))
        hremp['active'] = ('{}'.format(active))
          
        hr_emp.append(hremp)   
#         
    insert('hr.employee',hr_emp)
    
# #=====================
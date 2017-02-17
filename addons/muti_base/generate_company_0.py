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
            
        if not os.path.exists(os.getcwd()+'/data/'):
            os.makedirs(os.getcwd()+'/data/')
        # =============================
        print 'writing to...',csvfile
        with open(os.getcwd()+'/data/'+csvfile+'.csv', 'w') as csvfile:
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
     
# #=====================
    print 'Processing...Partners'
    pgquery = ("""SELECT REPLACE(CONCAT('res_partner_', LOWER(cbucode),'id'),' ','')AS id,cbusunit NAME, 
                'False' is_company,
                (CASE WHEN cabbreviation IN ('ckei','asa','vmi','adc','mvcthr-b','ckugmc','psa','arkclick') 
                           THEN 'false' ELSE 'true' END) active
                 FROM genbusinessunit ORDER BY active,NAME;""")
                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    
    pgquery1 = ("""SELECT CONCAT('res_partner_',a.`cbranchcode`,'id') AS id,
                CASE WHEN b.`cabbreviation` LIKE '%bradc%' THEN CONCAT('BRDC ',a.`cbranchdept`)
                     WHEN a.`cbranchdept` LIKE CONCAT('%', b.`cabbreviation` ,'%') THEN a.`cbranchdept`
                     ELSE CONCAT(b.`cabbreviation`,' ',a.`cbranchdept`) END NAME,              
               'true' is_company,
                 (CASE WHEN b.`cabbreviation` IN ('ckei','asa','vmi','adc','mvcthr-b','ckugmc','psa','arkclick')THEN 'false'  
                       WHEN a.`cbranchdept` REGEXP ('agdao|butuan|toril|gensan|counter|m''lang|malaybalay|nabunturan|ozamiz|
                                    |pagadian|francisco|construction|alabel|cotabato|not|don''t|dipolog|
                                    |fgmg|iligan|proper|glan|ipil|kabacan|lake sebu|manila|tupi|zamboanga|
                                    |tampakan|tantangan') THEN 'false' 
                       WHEN a.cbranchcode IN ('06000101','06000076','06000055','06000057','06000052','06000050','06000054',
                                  '06000049','06000053','06000052','06000009','06000051','06000052','07000003',
                                  '03000009','01000070','01000063','01000095','01000104','01000053','01000032',
                                  '01000073','01000040','01000084','01000101','01000103','01000078','12000023',
                                  '12000022','06000070','06000062') THEN 'false' 
                       ELSE 'true' END) active
                 FROM genbranchdept a , genbusinessunit b
                 WHERE b.`cbucode` = a.`cbucode`
                 AND a.`cbrdept` = 'b'
                 ORDER BY active,NAME;""")
                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery1)
    pgsql_recs1 = mysql_cursor.fetchall() 
    
    
    res_partner = []
    res_partner_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
    
    
    
    for (id,name,is_company,active) in pgsql_recs:
        ctr_key+=1
        respartner = {}
          
        respartner['id'] = ('{}'.format(id))
        respartner['name'] = ('{}'.format(unidecode(name)))
        respartner['is_company'] = ('{}'.format(is_company))
        respartner['active'] = ('{}'.format(active))
          
        res_partner.append(respartner)
        
    for (id,name,is_company,active) in pgsql_recs1:
        ctr_key+=1
        respartner = {}
          
        respartner['id'] = ('{}'.format(id))
        respartner['name'] = ('{}'.format(unidecode(name)))
        respartner['is_company'] = ('{}'.format(is_company))
        respartner['active'] = ('{}'.format(active))
          
        res_partner.append(respartner) 
          
    manual_insrt = [('res_partner_mutihomeoffice','MUTI HOME OFFICE','True','True'),
                    ('res_partner_epfchomeoffice','EPFC HOME OFFICE','True','True'),
                    ('res_partner_hondahomeoffice','HONDA HOME OFFICE','True','True'),
                    ('res_partner_siasagreatwall','SIASA GREATWALL','True','True'),
                    ('res_partner_siasahomeoffice','SIASA HOME OFFICE','True','True'),
                    ('res_partner_ssaiaihomeoffice','SSAIAI HOME OFFICE','True','True'),
                    ('res_partner_4mratcohomeoffice','4MRATCO HOME OFFICE','True','True'),
                    ('res_partner_pumgashomeoffice','PUMGAS HOME OFFICE','True','True'),
                    ('res_partner_cbg','CBG','True','True'),
                    ]
    
    for (id,name,is_company,active) in manual_insrt:
        ctr_key+=1
        respartner = {}
          
        respartner['id'] = ('{}'.format(id))
        respartner['name'] = ('{}'.format(unidecode(name)))
        respartner['is_company'] = ('{}'.format(is_company))
        respartner['active'] = ('{}'.format(active))
          
        res_partner.append(respartner)    
    insert('res.partner',res_partner)    
     
# #=====================
    print 'Processing...Company/Branch'
    pgquery = ("""SELECT REPLACE(CONCAT('res_company_', LOWER(cbucode),'id'),' ','')AS id,
                '' CODE,cabbreviation abbreviation,cbusunit NAME, 'base.PHP' currency_id, 
                REPLACE(CONCAT('res_partner_', LOWER(cbucode),'id'),' ','')AS partner_id,'base.main_company' parent_id, 
                '' area_id, 'False' is_branch,
                (CASE WHEN cabbreviation IN ('ckei','asa','vmi','adc','mvcthr-b','ckugmc','psa','arkclick') 
                           THEN 'false' ELSE 'true' END) active
                 FROM genbusinessunit ORDER BY active,NAME;""")
                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    
    pgquery1 = ("""SELECT CONCAT('res_company_branch_',a.`cbranchcode`,'id') AS id,'' CODE,'' abbreviation,
                CASE WHEN b.`cabbreviation` LIKE '%bradc%' THEN CONCAT('BRDC ',a.`cbranchdept`)
                     WHEN a.`cbranchdept` LIKE CONCAT('%', b.`cabbreviation` ,'%') THEN a.`cbranchdept`
                     ELSE CONCAT(b.`cabbreviation`,' ',a.`cbranchdept`) END NAME,
                'base.PHP' currency_id,CONCAT('res_partner_',a.`cbranchcode`,'id') AS partner_id,
                CONCAT('res_company_',REPLACE(REPLACE(LOWER(b.`cbucode`),'.',''),' ',''),'id')  AS parent_id,
                '' area_id,'true' is_branch,
                 (CASE WHEN b.`cabbreviation` IN ('ckei','asa','vmi','adc','mvcthr-b','ckugmc','psa','arkclick')THEN 'false'  
                       WHEN a.`cbranchdept` REGEXP ('agdao|butuan|toril|gensan|counter|m''lang|malaybalay|nabunturan|ozamiz|
                                    |pagadian|francisco|construction|alabel|cotabato|not|don''t|dipolog|
                                    |fgmg|iligan|proper|glan|ipil|kabacan|lake sebu|manila|tupi|zamboanga|
                                    |tampakan|tantangan') THEN 'false' 
                       WHEN a.cbranchcode IN ('06000101','06000076','06000055','06000057','06000052','06000050','06000054',
                                  '06000049','06000053','06000052','06000009','06000051','06000052','07000003',
                                  '03000009','01000070','01000063','01000095','01000104','01000053','01000032',
                                  '01000073','01000040','01000084','01000101','01000103','01000078','12000023',
                                  '12000022','06000070','06000062') THEN 'false' 
                       ELSE 'true' END) active
                 FROM genbranchdept a , genbusinessunit b
                 WHERE b.`cbucode` = a.`cbucode`
                 AND a.`cbrdept` = 'b'
                 ORDER BY active,NAME;""")
                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery1)
    pgsql_recs1 = mysql_cursor.fetchall() 
    
    
    comp_branch = []
    comp_branch_pg_key = collections.OrderedDict()
    print 'pgsql_recs',pgsql_recs
    ctr_key = 0
    
    
    
    for (id,code,abbreviation,name,currency_id,partner_id,parent_id,area_id,is_branch,active) in pgsql_recs:
        ctr_key+=1
        compbranch = {}
          
        compbranch['id'] = ('{}'.format(id))
        compbranch['code'] = ('{}'.format(code))
        compbranch['abbreviation'] = ('{}'.format(abbreviation))
        compbranch['name'] = ('{}'.format(name))
        compbranch['currency_id:id'] = ('{}'.format(currency_id))
        compbranch['partner_id:id'] = ('{}'.format(partner_id))
        compbranch['parent_id:id'] = ('{}'.format(parent_id))
        compbranch['area_id:id'] = ('{}'.format(area_id))
        compbranch['is_branch'] = ('{}'.format(is_branch))
        compbranch['active'] = ('{}'.format(active))
          
        comp_branch.append(compbranch)
        
    for (id,code,abbreviation,name,currency_id,partner_id,parent_id,area_id,is_branch,active) in pgsql_recs1:
        ctr_key+=1
        compbranch = {}
          
        compbranch['id'] = ('{}'.format(id))
        compbranch['code'] = ('{}'.format(code))
        compbranch['abbreviation'] = ('{}'.format(abbreviation))
        compbranch['name'] = ('{}'.format(name))
        compbranch['currency_id:id'] = ('{}'.format(currency_id))
        compbranch['partner_id:id'] = ('{}'.format(partner_id))
        compbranch['parent_id:id'] = ('{}'.format(parent_id))
        compbranch['area_id:id'] = ('{}'.format(area_id))
        compbranch['is_branch'] = ('{}'.format(is_branch))
        compbranch['active'] = ('{}'.format(active))
          
        comp_branch.append(compbranch) 
          
    manual_insrt = [('res_company_branch_mutihomeoffice','','','MUTI HOME OFFICE','base.PHP','muti_base.res_partner_mutihomeoffice','muti_base.res_company_bu000006id','','True','True'),
                    ('res_company_branch_epfchomeoffice','','','EPFC HOME OFFICE','base.PHP','muti_base.res_partner_epfchomeoffice','muti_base.res_company_bu000006id','','True','True'),
                    ('res_company_branch_hondahomeoffice','','','HONDA HOME OFFICE','base.PHP','muti_base.res_partner_hondahomeoffice','muti_base.res_company_bu000003id','','True','True'),
                    ('res_company_branch_siasagreatwall','','','SIASA GREATWALL','base.PHP','muti_base.res_partner_siasagreatwall','muti_base.res_company_bu000012id','','True','True'),
                    ('res_company_branch_siasahomeoffice','','','SIASA HOME OFFICE','base.PHP','muti_base.res_partner_siasahomeoffice','muti_base.res_company_bu000012id','','True','True'),
                    ('res_company_branch_ssaiaihomeoffice','','','SSAIAI HOME OFFICE','base.PHP','muti_base.res_partner_ssaiaihomeoffice','muti_base.res_company_bu000019id','','True','True'),
                    ('res_company_branch_4mratcohomeoffice','','','4MRATCO HOME OFFICE','base.PHP','muti_base.res_partner_4mratcohomeoffice','muti_base.res_company_bu000021id','','True','True'),
                    ('res_company_branch_pumgashomeoffice','','','PUMGAS HOME OFFICE','base.PHP','muti_base.res_partner_pumgashomeoffice','muti_base.res_company_bu000017id','','True','True'),
                    ('res_company_branch_cbg','','','CBG','base.PHP','muti_base.res_partner_cbg','muti_base.res_company_bu000008id','','True','True'),
                    ]
    
    for (id,code,abbreviation,name,currency_id,partner_id,parent_id,area_id,is_branch,active) in manual_insrt:
        ctr_key+=1
        compbranch = {}
          
        compbranch['id'] = ('{}'.format(id))
        compbranch['code'] = ('{}'.format(code))
        compbranch['abbreviation'] = ('{}'.format(abbreviation))
        compbranch['name'] = ('{}'.format(name))
        compbranch['currency_id:id'] = ('{}'.format(currency_id))
        compbranch['partner_id:id'] = ('{}'.format(partner_id))
        compbranch['parent_id:id'] = ('{}'.format(parent_id))
        compbranch['area_id:id'] = ('{}'.format(area_id))
        compbranch['is_branch'] = ('{}'.format(is_branch))
        compbranch['active'] = ('{}'.format(active))
          
        comp_branch.append(compbranch)    
    insert('res.company',comp_branch)
#======================
## epfc and mysql Brand
    print 'Processing...Config Branch'
    pgquery = ("""SELECT CONCAT('config_branch_',a.`cbranchcode`,'id') AS id,
                CASE WHEN b.`cabbreviation` LIKE '%bradc%' THEN CONCAT('BRDC ',a.`cbranchdept`)
                     WHEN a.`cbranchdept` LIKE CONCAT('%', b.`cabbreviation` ,'%') THEN a.`cbranchdept`
                     ELSE CONCAT(b.`cabbreviation`,' ',a.`cbranchdept`) END NAME,
                CONCAT('muti_base.res_partner_',REPLACE(REPLACE(LOWER(b.`cbucode`),'.',''),' ',''),'id')  AS partner_id,
                CONCAT('muti_base.res_company_',REPLACE(REPLACE(LOWER(b.`cbucode`),'.',''),' ',''),'id')  AS company_id,
                '' area_id,'' branch_code,'muti_base.config_area_1' area_id,
                 (CASE WHEN b.`cabbreviation` IN ('ckei','asa','vmi','adc','mvcthr-b','ckugmc','psa','arkclick')THEN 'false'  
                       WHEN a.`cbranchdept` REGEXP ('agdao|butuan|toril|gensan|counter|m''lang|malaybalay|nabunturan|ozamiz|
                                    |pagadian|francisco|construction|alabel|cotabato|not|don''t|dipolog|
                                    |fgmg|iligan|proper|glan|ipil|kabacan|lake sebu|manila|tupi|zamboanga|
                                    |tampakan|tantangan') THEN 'false' 
                       WHEN a.cbranchcode IN ('06000101','06000076','06000055','06000057','06000052','06000050','06000054',
                                  '06000049','06000053','06000052','06000009','06000051','06000052','07000003',
                                  '03000009','01000070','01000063','01000095','01000104','01000053','01000032',
                                  '01000073','01000040','01000084','01000101','01000103','01000078','12000023',
                                  '12000022','06000070','06000062') THEN 'false' 
                       ELSE 'true' END) active
                 FROM genbranchdept a , genbusinessunit b
                 WHERE b.`cbucode` = a.`cbucode`
                 AND a.`cbrdept` = 'b'
                 ORDER BY active,NAME;""")
                    
    print 'Processing...SQL.'
    mysql_cursor.execute(pgquery)
    pgsql_recs = mysql_cursor.fetchall() 
    cnfg_brnch = []
    cnfg_brnch_pg_key = collections.OrderedDict()

    ctr_key = 0
    for (id,name,partner_id,company_id,area_id,branch_code,area_id,active) in pgsql_recs:
        ctr_key+=1
        cnfgbrnch = {}
        cnfgbrnch['id'] = ('{}'.format(id))
        cnfgbrnch['name'] = ('{}'.format(name))
        cnfgbrnch['partner_id:id'] = ('{}'.format(partner_id))
        cnfgbrnch['company_id:id'] = ('{}'.format(company_id))
        cnfgbrnch['area_id:id'] = ('{}'.format(area_id))
        cnfgbrnch['branch_code'] = ('{}'.format(branch_code))
        cnfgbrnch['area_id:id'] = ('{}'.format(area_id))
        cnfgbrnch['active'] = ('{}'.format(active))
        
        cnfg_brnch.append(cnfgbrnch)
        
    insert('config.branch',cnfg_brnch)
     
# #=====================

# import mysql.connector
# from mysql.connector import errorcode
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
            
    postgre_conn = psycopg2.connect (user='openerp', password='openerp',
                                             host='192.168.100.253',port=5432,
                                             database='EPFC')

    print 'Connection Established.'
   
    postgre_cursor = postgre_conn.cursor()


#======================
## epfc and mysql Brand
    print 'Processing...Brand'
    pgquery = ("""select brand_id,coalesce(name,'') as name,coalesce(old_brand_code,'') as old_brand_code from product_brand""")
    
    print 'Processing...SQL.'
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall() 
    
    product_brand = []
    product_brandpg_key = collections.OrderedDict()
    
    ctr_key = 0
    for (brand_id,name,old_brand_code) in pgsql_recs:
        ctr_key+=1
        pbrand = {'active': True}
        pbrand['id'] = ('{}'.format(ctr_key))
        pbrand['old_brand_code'] = ('{}'.format(old_brand_code))
        pbrand['brand_id'] = ('{}'.format(brand_id))
        pbrand['name'] = ('{}'.format(name))
        key = pbrand['old_brand_code']
        if key not in product_brandpg_key:
            product_brandpg_key[key] = ctr_key
        
        #pbrand['create_uid'] = 1
        pbrand['create_date'] = 'NOW()'
            
        product_brand.append(pbrand)
        
    insert('product.brand',product_brand)
     
# #=====================
# MODEL
    
    print 'Processing...Model'
     
    pgquery = ("""select m.vecmodel_id as vecmodel_id,
                  coalesce(b.brand_id,'') as brand_id,
                  coalesce(m.name,'') as name, COALESCE(m.old_model_code,'') as old_model_code 
                  from product_model m
                  left join product_brand b on CAST (b.brand_id AS INTEGER)= m.brand_id""")
    
    start = time.time()  
    print start  
    print 'Processing...SQL.'
    end=time.time()
    print end-start
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
   
    prod_model = []
    prod_model_key = collections.OrderedDict()
       
    ctr_key = 0
    for(vecmodel_id,brand_id,name,old_model_code) in pgsql_recs:
         ctr_key+=1
         pgmodel = {'active': True}
         pgmodel['id'] = ('{}'.format(ctr_key))
         pgmodel['vecmodel_id'] = ('{}'.format(vecmodel_id))
         pgmodel['brand_id'] = ('{}'.format(brand_id))
         pgmodel['name'] = ('{}'.format(name))
         pgmodel['old_model_code'] = ('{}'.format(old_model_code))
           
         key = pgmodel['old_model_code']
         if key not in prod_model_key:
             prod_model_key[key] = ctr_key
               
         #pgmodel['create_uid'] = 1
         pgmodel['create_date'] = 'NOW()'
          
         prod_model.append(pgmodel)
           
    insert('product.model',prod_model)        

#=====================
#EPFC COLOR
    print 'Processing...Color'
    pgquery = ("""select veccolor_id,coalesce(name,'') as name,coalesce(old_color_code,'') as old_color_code from product_color order by id""")
    print 'Processing...SQL.'
     
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
     
    prod_color = []
    prod_color_key = collections.OrderedDict()
     
    ctr_key = 0
    for(veccolor_id,name,old_color_code) in pgsql_recs:
        ctr_key+=1
        pgcolor = {'active': True}
        pgcolor['id'] = ('{}'.format(ctr_key))
        pgcolor['veccolor_id'] = ('{}'.format(veccolor_id))
        pgcolor['name'] = ('{}'.format(name))
        pgcolor['old_color_code'] = ('{}'.format(old_color_code))
        key = pgcolor['old_color_code']
        if key not in prod_color_key:
            prod_color_key[key] = ctr_key
             
        #pgcolor['create_uid'] = 1
        pgcolor['create_date'] = 'NOW()'
         
        prod_color.append(pgcolor)
         
    insert('product.color',prod_color)

#=====================
#EPFC BODY
    print 'Processing...Body'
    pgquery = ("""select vecbody_id,coalesce(name,''),old_body_code from product_body order by vecbody_id;""")
    print 'Processing...SQL.'
     
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
     
    prod_body = []
    prod_body_key = collections.OrderedDict()
     
    ctr_key = 0
    for(vecbody_id,name,old_body_code) in pgsql_recs:
        ctr_key+=1
        pgbody = {'active': True}
        pgbody['id'] = ('{}'.format(ctr_key))
        pgbody['vecbody_id'] = ('{}'.format(vecbody_id))
        pgbody['name'] = ('{}'.format(name))
        pgbody['old_body_code'] = ('{}'.format(old_body_code))
        key = pgbody['old_body_code']
        if key not in prod_body_key:
            prod_body_key[key] = ctr_key
             
        #pgbody['create_uid'] = 1
        pgbody['create_date'] = 'NOW()'
         
        prod_body.append(pgbody)
         
    insert('product.body',prod_body)

#=====================
#EPFC WHEEL
    print 'Processing...Wheel'
    pgquery = ("""select vecwheel_id,name,old_wheel_code from product_wheel""")
    print 'Processing...SQL.'
     
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
     
    prod_wheel = []
    prod_wheel_key = collections.OrderedDict()
     
    ctr_key = 0
    for(vecwheel_id,name,old_wheel_code) in pgsql_recs:
        ctr_key+=1
        pgwheel = {'active': True}
        pgwheel['id'] = ('{}'.format(ctr_key))
        pgwheel['vecwheel_id'] = ('{}'.format(vecwheel_id))
        pgwheel['name'] = ('{}'.format(name))
        pgwheel['old_wheel_code'] = ('{}'.format(old_wheel_code))
        key = pgwheel['old_wheel_code']
        if key not in prod_body_key:
            prod_body_key[key] = ctr_key
             
#         pgwheel['create_uid'] = 1
        pgwheel['create_date'] = 'NOW()'
         
        prod_wheel.append(pgwheel)
         
    insert('product.wheel',prod_wheel)

#=====================
#EPFC TYPE
    print 'Processing...Type'
    pgquery = ("""select vectype_id,name from product_type""")
    print 'Processing...SQL.'
     
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
     
    prod_type = []
    prod_type_key = collections.OrderedDict()
     
    ctr_key = 0
    for(vectype_id,name) in pgsql_recs:
        ctr_key+=1
        pgtype = {'active': True}
        pgtype['id'] = ('{}'.format(ctr_key))
        pgtype['vectype_id'] = ('{}'.format(vectype_id))
        pgtype['name'] = ('{}'.format(name))
#         pgtype['old_vehicle_code'] = ('{}'.format(vectype_id))
#         key = pgtype['old_vehicle_code']
#         if key not in prod_type_key:
#             prod_type_key[key] = ctr_key
             
        #pgtype['create_uid'] = 1
        pgtype['create_date'] = 'NOW()'
         
        prod_type.append(pgtype)
         
    insert('product.type',prod_type)
    
#=====================
#EPFC TRANSMISSION
    print 'Processing...Transmission'
    pgquery = ("""select vectrans_id,name,old_transmission_code from product_transmission order by old_transmission_code""")
    print 'Processing...SQL.'
     
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
     
    prod_transmission = []
    prod_transmission_key = collections.OrderedDict()
     
    ctr_key = 0
    for(vectrans_id,name,old_transmission_code) in pgsql_recs:
        ctr_key+=1
        pgtransmission = {'active': True}
        pgtransmission['id'] = ('{}'.format(ctr_key))
        pgtransmission['vectrans_id'] = ('{}'.format(vectrans_id))
        pgtransmission['name'] = ('{}'.format(name))
        pgtransmission['old_transmission_code'] = ('{}'.format(old_transmission_code))
        key = pgtransmission['old_transmission_code']
        if key not in prod_transmission_key:
            prod_transmission_key[key] = ctr_key
             
        #pgtransmission['create_uid'] = 1
        pgtransmission['create_date'] = 'NOW()'
         
        prod_transmission.append(pgtransmission)
         
    insert('product.transmission',prod_transmission)
#=====================
#EPFC MC CLASSIFICATION
    print 'Processing...Mc classification'
    pgquery = ("""select mc_classification,breaking_period from product_mc_classification""")
    print 'Processing...SQL.'
     
    postgre_cursor.execute(pgquery)
    pgsql_recs = postgre_cursor.fetchall()
     
    prod_mcclassification = []
    prod_mcclassification_key = collections.OrderedDict()
     
    ctr_key = 0
    for(mc_classification,breaking_period) in pgsql_recs:
        ctr_key+=1
        pgmcclas= {'active': True}
        pgmcclas['id'] = ('{}'.format(ctr_key))
        pgmcclas['mc_classification'] = ('{}'.format(mc_classification))
        pgmcclas['breaking_period'] = ('{}'.format(breaking_period))
             
        #pgmcclas['create_uid'] = 1
        pgmcclas['create_date'] = 'NOW()'
         
        prod_mcclassification.append(pgmcclas)
         
    insert('product.mc.classification',prod_mcclassification)

#pop up for complete import    
    print 'Complete generating csv'
    time2 = datetime.datetime.time(datetime.datetime.now())
    print 'Process time:', time1, time2
#closing cursor and connection

    postgre_conn.close()
    postgre_cursor.close()
    
    
         
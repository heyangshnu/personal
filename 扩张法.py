
# coding: utf-8

from feature_engineer import *
import pandas as pd
from sqlalchemy.engine import create_engine
engine_1 = create_engine(
        'mysql+pymysql://ro:cKqj4E3$K7GGeqs@nshd-slave-bi.mysql.rds.aliyuncs.com/paydayloan?charset=utf8',
        echo=False,pool_size=20, max_overflow=0)
engine_2 = create_engine(
    'mysql+pymysql://riskcontrol:tuLwJ3G6FLwR6t4A@nshd-risk.mysql.rds.aliyuncs.com/riskcontrol?charset=utf8',
    echo=False)

sql = """select distinct userId
from eva_riskcontrol_audits
where status = "rejected" and userId not in (
	select distinct userId
	from eva_riskcontrol_audits
	where status = 'approved')
	and createdAt between UNIX_TIMESTAMP('2017-7-1 00:00:00') and UNIX_TIMESTAMP('2017-9-1 00:00:00');"""
RefuseUid = pd.read_sql(sql,engine_1)

uids = list(set(RefuseUid.userId))

for i in range(int(len(uids)/1000)):
    u = model(uids[i*1000:(i+1)*1000])
    features = u.features
    features.to_csv(r'/home/heyang/code/Reject Inference/data/reject_features_'+str(i)+'.csv',index=False)
    #print("已经完成了第",i*100,"个uid了")
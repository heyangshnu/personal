from bmqb.model_utils import *

class model():
    def __init__(self, uid, loan_time=None):
        """
        :param uid: 用户ID
        :param loan_time: 借款次数，有三种情况
        若该用户为首借，loan_time默认1,
        若为复借，loan_time默认为-1
        若已知该用户为复借，loan_time可以指定从1开始的正整数，且该数应该小于改用户的最大借款次数
        """

        if isinstance(uid,int):
            self.audit = pd.read_sql("""select userId as uid, createdAt from eva_riskcontrol_audits 
                                        where userId > 100 and userId = {}""".format(uid),engine_1)
            self.uid = [uid]
        elif isinstance(uid,list):
            if len(uid) == 1:
                self.audit = pd.read_sql("""select userId as uid, createdAt from eva_riskcontrol_audits 
                                                        where userId > 100 and userId = {}""".format(uid[0]), engine_1)
            else:
                self.audit = pd.read_sql("""select userId as uid, createdAt 
                                            from eva_riskcontrol_audits 
                                            where userId > 100 and userId in {}""".format(tuple(uid)), engine_1)
            self.uid = sorted(uid)

        self.audit['startDate'] = self.audit.createdAt.map(lambda x: datetime.datetime.fromtimestamp(x).date())
        # self.first = pd.read_sql("""select  loan.id as loan_id,loan.userId as uid, startDate,endDate,
        #                                           loan.loanAmount,loan.payAmount, repayments.overduedays,
        #                                           DATE_FORMAT(FROM_UNIXTIME(repayments.repaidAt), '%%Y-%%m-%%d') as repayAt
        #                                           from eva_loan_loans as loan
        #                                           left join eva_loan_repayments as repayments
        #                                           on loan.repaymentid = repayments.id and repayments.status='repaid'
        #                                           where loan.status='paid'
        #                                           and (loan.endDate < CURDATE() or repayments.repaidAt is not null)
        #                                           order by endDate,uid""", engine_1)
        # self.first['timestamp'] = self.first.startDate.map(lambda x: int(time.mktime(x.timetuple())))
        # a = self.first.groupby("uid")['loan_id']
        # self.first["loan_time"] = a.rank()
        # self.first['repayAt'] = self.first['repayAt'].map(lambda x: parse_ymd(x))
        # self.first['loan_time'] = self.first['loan_time'].astype(int)
        # self.uids = set(self.first.uid)
        #
        # ## 用户是否是复借
        # is_reloan = []
        # for i in self.uid:
        #     if i in self.uids:
        #         is_reloan.append(True)
        #     else:
        #         is_reloan.append(False)
        # self.is_reloan = is_reloan

        ## 所有uid的借款次数
        tmp = []
        # if loan_time == None:
        #     tmp = [1] * len(self.uid)
        # elif isinstance(loan_time,list):
        #     for i in range(len(self.uid)):
        #         if self.is_reloan[i]:
        #             max_loan_times = int(max(self.first[self.first.uid==self.uid[i]].loan_time))
        #             if loan_time[i]:
        #                 if loan_time[i] > max_loan_times:
        #                     print("该用户最大借款次数为{}".format(max_loan_times), "loan_time应为小于其的正整数")
        #                 else:
        #                     tmp.append(loan_time[i])
        #             else:
        #                 tmp.append(-1)
        #         else:
        #             tmp.append(1)
        # elif isinstance(loan_time,int):
        #     tmp = [loan_time]
        #
        # self.loan_time = tmp
        self.features = self.prepare_data()

    def get_up(self):
        if len(self.uid) == 1:
            tmp = pd.read_sql("""select b.id as uid,b.realName,b.gender,b.loginFailedAt,
                                                         b.registerFrom,b.registerOs,b.registerIp,
                                                         b.registerAgent,b.certNumber,c.birthday,
                                                         c.income,c.relationshipStatus,c.degree,
                                                         c.company,c.companyType,c.companyProvince,
                                                         c.companyCity,c.companyState,c.companyDivisionCode,
                                                         c.companyLocation,c.workExperience,c.career,c.jobTitle,
                                                         c.industry,c.province,c.city,c.state,c.divisionCode,
                                                         c.houseType,c.houseProperty,c.phoneBusiness,c.phoneHome,
                                                         d.zmxyScore,d.zmxyIvsScore,d.zmxyIvsVerification,d.tongdunRiskscore,
                                                         d.zmxyFraudTaskId,d.zmxyIvsWatchListTaskId
                                                        from
                                                        (select distinct userId
                                                        from eva_riskcontrol_audits) as a
                                                        join eva_user_users as b
                                                        on a.userId = b.Id
                                                        join eva_user_profiles as c
                                                        on a.userId = c.userId
                                                        join eva_riskcontrol_credits as d
                                                        on a.userId = d.userId
                                                        where b.id = {}""".format(self.uid[0]), engine_1)
        else:
            tmp = pd.read_sql("""select b.id as uid,b.realName,b.gender,b.loginFailedAt,
                                             b.registerFrom,b.registerOs,b.registerIp,
                                             b.registerAgent,b.certNumber,c.birthday,
                                             c.income,c.relationshipStatus,c.degree,
                                             c.company,c.companyType,c.companyProvince,
                                             c.companyCity,c.companyState,c.companyDivisionCode,
                                             c.companyLocation,c.workExperience,c.career,c.jobTitle,
                                             c.industry,c.province,c.city,c.state,c.divisionCode,
                                             c.houseType,c.houseProperty,c.phoneBusiness,c.phoneHome,
                                             d.zmxyScore,d.zmxyIvsScore,d.zmxyIvsVerification,d.tongdunRiskscore,
                                             d.zmxyFraudTaskId,d.zmxyIvsWatchListTaskId
                                            from
                                            (select distinct userId
                                            from eva_riskcontrol_audits) as a
                                            join eva_user_users as b
                                            on a.userId = b.Id
                                            join eva_user_profiles as c
                                            on a.userId = c.userId
                                            join eva_riskcontrol_credits as d
                                            on a.userId = d.userId
                                            where b.id in {}""".format(tuple(self.uid)), engine_1)
        tmp.index = range(len(tmp))
        df = pd.DataFrame(columns=df_up.columns,index=range(len(self.uid)))
        df.uid = tmp.uid
        if True in df.uid.isnull().value_counts():
            self.fail_sql_up = list(set(self.uid)-set(tmp.uid))
        df.age = tmp.certNumber.map(lambda x:cal_age(x[6:14]))

        # df.age = pd.Series(cal_age(tmp.certNumber.iloc[0][6:14]))
        # df['zmxyIvsWatchList'] = str(tmp.zmxyIvsWatchList.map(lambda x: zm_1(x)).iloc[0])
        # try:
        #     df.zmxyIvsWatchList = df.zmxyIvsWatchList.map(eval)
        # except:
        #     df.zmxyIvsWatchList = 'not_hit'
        # df['zmxyIvsVerification'] = str(tmp.zmxyIvsVerification.map(lambda x: None if not x else x.split(",")).iloc[0])
        # df.zmxyIvsVerification = df.zmxyIvsVerification.map(eval)

        gender = pd.get_dummies(tmp.gender, prefix='gender')
        rFrom = pd.get_dummies(tmp.registerFrom, prefix='rFrom')
        rOS = pd.get_dummies(tmp.registerOs, prefix='rOs')
        income = pd.get_dummies(tmp.income, prefix='income')
        marr = pd.get_dummies(tmp.relationshipStatus, prefix='marr')
        degree = pd.get_dummies(tmp.degree, prefix='degree')
        com_type = pd.get_dummies(tmp.companyType, prefix='company')
        com_prov = pd.get_dummies(tmp.companyProvince, prefix='company_prov')
        career = pd.get_dummies(tmp.career, prefix='career')
        work_exp = pd.get_dummies(tmp.workExperience, prefix='workExp')
        job_title = pd.get_dummies(tmp.jobTitle, prefix='job')
        house_prop = pd.get_dummies(tmp.houseProperty, prefix='houseProp')
        house_type = pd.get_dummies(tmp.houseType, prefix='houseType')
        industry = pd.get_dummies(tmp.industry, prefix='industry')
        prov = pd.get_dummies(tmp.province, prefix='province')

        tt = pd.concat([gender, rFrom, rOS, income, marr,
                        degree, com_type, com_prov, career, work_exp,
                        job_title, house_prop, house_type, industry, prov], axis=1)
        # for i in tt.columns:
        #     if i in df.columns:
        #         df[i] = tt[i]

        for i in tt.columns:
            df[i] = tt[i]
        # for i in df.columns:
        #     if 'term' in i:
        #         df[i].fillna(0, inplace=True)
        #
        # df.overduedays.fillna(100, inplace=True)

        # zm_feature = pd.DataFrame(columns=verify_code['验证信息码'].tolist() + risk_code['风险代码'].tolist(),
        #                           index=tmp.index)
        #
        # for i in verify_code['验证信息码'].tolist():
        #     zm_feature[i] = tmp.zmxyIvsVerification.map(lambda s: zm_2(s, i))
        # for i in risk_code.风险代码.tolist():
        #     zm_feature[i] = tmp.zmxyIvsWatchList.map(lambda s: zm_3(s, i))
        # df["zm_hit_num"] = zm_feature.sum(axis=1)

        # df.zkScore = xdata_rule[xdata_rule.uid == uid].zk_score.iloc[0]
        # df.zkScore = zk_score_3_4(User(int(uid)))
        zkScore = []
        for i in self.uid:
            try:
                zkScore.append(zk_score_3_4(User(int(i))))
            except:
                zkScore.append(None)

        try:
            tongdunRiskscore = tmp.tongdunRiskscore
        except:
            tongdunRiskscore = None

        try:
            zmxyScore = tmp.zmxyScore
        except:
            zmxyScore = None

        try:
            zmxyIvsScore = tmp.zmxyIvsScore
        except:
            zmxyIvsScore = None

        df.zkScore = pd.Series(zkScore, name='zkScore')
        df.tongdunRiskscore = tongdunRiskscore
        df.zmxyScore = zmxyScore
        df.zmxyIvsScore = zmxyIvsScore

        # if uid not in scores.uid:
        #     df.zkScore = xdata_rule[xdata_rule.uid == uid].zk_score.iloc[0]
        #
        #     df.tongdunRiskscore = xdata[xdata.uid == uid].tongdunRiskscore.iloc[0]
        #     df.zmxyScore = xdata[xdata.uid == uid].zmxyScore.iloc[0]
        #     df.zmxyIvsScore = xdata[xdata.uid == uid].zmxyIvsScore.iloc[0]

        for i in df.columns:
            for j in ['zkScore', 'tongdunRiskscore', 'zmxyScore', 'zmxyIvsScore']:
                if i != j:
                    df[i].fillna(int(0), inplace=True)

        df['rOs_Android'] = df['rOs_android'] + df['rOs_Android'] + df['rOs_ANDROID']
        del df['rOs_android']
        del df['rOs_ANDROID']
        feats = [i for i in df.columns if i not in ['loan_time', 'zmxyIvsWatchList', 'zmxyIvsVerification']]
        df = df[feats]
        df.rename(columns={"zkScore":'zk_v_3_4'},inplace=True)

        return df

    def get_hd(self):
        amount_dict = {"0~0.2w": 1, "0~0.2W": 1, "0～0.2w": 1, "0～0.2W": 1, "0w～0.2w": 1, "0W～0.2W": 1,
                       "0.2w~0.5w": 2, "0.2W~0.5W": 2, "0.2w～0.5w": 2, "0.2W～0.5W": 2,
                       "0.5w~1w": 3, "0.5w～1w": 3, "0.5W~1W": 3, "0.5W～1W": 3,
                       "1w~3w": 4, "1w～3w": 4, "1W~3W": 4, "1W～3W": 4,
                       "3w~5w": 5, "3w～5w": 5, "3W~5W": 5, "3W～5W": 5,
                       "5w~10w": 6, "5w～10w": 6, "5W~10W": 6, "5W～10W": 6,
                       "10w以上": 7, "10W以上": 7}

        df = pd.DataFrame(columns=df_hd.columns, index=range(len(self.uid)))
        if len(self.uid) == 1:
            tmp = pd.read_sql("""select userId as uid, status, platformResponseParams
                            from eva_riskcontrol_background_tasks
                            where userId = {}
                            and status='success'
                            and platform='huadao'
                            """.format(self.uid[0]), engine_1)
        else:
            tmp = pd.read_sql("""select userId as uid, status, platformResponseParams
                from eva_riskcontrol_background_tasks
                where userId in {}
                and status='success'
                and platform='huadao'
                """.format(tuple(self.uid)), engine_1)

        tmp = tmp[~tmp.uid.duplicated()]
        tmp.index = range(len(tmp))

        if len(tmp):
            df['uid'] = tmp.uid
            if True in df.uid.isnull().value_counts():
                self.fail_sql_hd = list(set(self.uid) - set(tmp.uid))
            df['status'] = tmp.status
            df["response"] = tmp.platformResponseParams.map(hd_f_1)
            df.response = df.response.map(hd_f_2)
            # del df['platformResponseParams']

            df["EMR002"] = df.response.map(lambda x: None if not x else hd_002(x[0]["DATA"]))
            df["EMR004"] = df.response.map(lambda x: None if not x else hd_004(x[1]["DATA"]))
            df["EMR007"] = df.response.map(lambda x: None if not x else hd_007(x[2]["DATA"]))
            df["EMR009"] = df.response.map(lambda x: None if not x else hd_009(x[3]["DATA"]))
            df["EMR012"] = df.response.map(lambda x: None if not x else hd_012(x[4]["DATA"]))
            df["EMR013"] = df.response.map(lambda x: None if not x else hd_013(x[5]["DATA"]))

            # res_002 = hd_fliter_002(df.loc[0],audit)
            # res_004 = hd_fliter_004(df.loc[0],audit)
            # res_007 = hd_fliter_007(df.loc[0],audit)
            # res_009 = hd_fliter_009(df.loc[0],audit)
            # res_012 = hd_fliter_012(df.loc[0],audit)
            # res_013 = hd_fliter_013(df.loc[0],audit)


            p = Pool(12)
            result_002 = []
            result_004 = []
            result_007 = []
            result_009 = []
            result_012 = []
            result_013 = []
            for i in df.index:
                result_002.append(p.apply_async(hd_fliter_002, (df.loc[i], self.audit)))
                result_004.append(p.apply_async(hd_fliter_004, (df.loc[i], self.audit)))
                result_007.append(p.apply_async(hd_fliter_007, (df.loc[i], self.audit)))
                result_009.append(p.apply_async(hd_fliter_009, (df.loc[i], self.audit)))
                result_012.append(p.apply_async(hd_fliter_012, (df.loc[i], self.audit)))
                result_013.append(p.apply_async(hd_fliter_013, (df.loc[i], self.audit)))

            p.close()
            p.join()

            res_002 = {}
            res_004 = {}
            res_007 = {}
            res_009 = {}
            res_012 = {}
            res_013 = {}
            for p in range(len(result_002)):
                res_002[p] = result_002[p].get()
                res_004[p] = result_004[p].get()
                res_007[p] = result_007[p].get()
                res_009[p] = result_009[p].get()
                res_012[p] = result_012[p].get()
                res_013[p] = result_013[p].get()
            try:
                df_002 = pd.DataFrame(res_002).T.rename(columns={"p_type": "EMR002_p_type",
                                                                 "platform": "EMR002_platform"})
            except:
                df_002 = pd.DataFrame(columns=['EMR002_p_type', 'EMR002_platform', 'EMR002_registerTime'])

            try:
                df_004 = pd.DataFrame(res_004).T.rename(columns={"p_type": "EMR004_p_type",
                                                                 "platform": "EMR004_platform"})
            except:
                df_004 = pd.DataFrame(columns=['EMR004_applyAmount', 'EMR004_applyResult',
                                               'EMR004_applyTime', 'EMR004_p_type', 'EMR004_platform'])

            try:
                df_007 = pd.DataFrame(res_007).T.rename(columns={"p_type": "EMR007_p_type",
                                                                 "platform": "EMR007_platform"})
            except:
                df_007 = pd.DataFrame(columns=['EMR007_loanAmount', 'EMR007_loanTime',
                                               'EMR007_p_type', 'EMR007_platform'])

            try:
                df_009 = pd.DataFrame(res_009).T.rename(columns={"p_type": "EMR009_p_type",
                                                                 "platform": "EMR009_platform"})
            except:
                df_009 = pd.DataFrame(columns=['EMR009_p_type', 'EMR009_platform', 'EMR009_rejectTime'])

            try:
                df_012 = pd.DataFrame(res_012).T.rename(columns={"money": "EMR012_money",
                                                                 "platform": "EMR012_platform"})
            except:
                df_012 = pd.DataFrame(columns=['EMR012_counts', 'EMR012_d_time',
                                               'EMR012_money', 'EMR012_platform'])

            try:
                df_013 = pd.DataFrame(res_013).T.rename(columns={"money": "EMR013_money",
                                                                 "platform": "EMR013_platform"})
            except:
                df_013 = pd.DataFrame(columns=['EMR013_money', 'EMR013_platform'])

            f_1 = pd.concat([df_002, df_004, df_007, df_009, df_012, df_013], axis=1)
            # ss = []
            # for i in [res_002, res_004, res_007, res_009, res_012, res_013]:
            #     if i:
            #         ss.append(i)
            #         for j in i.keys():
            #             df[j] = str(i[j])
            #             df[j] = df[j].map(lambda x: eval(x))
            if len(df_002):
                f_1['EMR002_len'] = f_1.EMR002_platform.map(lambda x: None if not x else len(set(x)))
                f_1.EMR002_registerTime = f_1.EMR002_registerTime.map(
                    lambda x: None if not x else list(map(lambda x: hd_to_date(x), x)))
                f_1["registerGap"] = f_1.EMR002_registerTime.map(lambda x: None if not x else hd_loan_gap(x))
                f_1["registerGap_max"] = f_1.registerGap.map(lambda x: None if not x else max(x))
                f_1["registerGap_min"] = f_1.registerGap.map(lambda x: None if not x else min(x))
                f_1["registerGap_std"] = f_1.registerGap.map(lambda x: None if not x else np.std(x))
                f_1["registerGap_mean"] = f_1.registerGap.map(lambda x: None if not x else np.mean(x))
                f_1["registerGap_median"] = f_1.registerGap.map(lambda x: None if not x else np.median(x))
                f_1["registerGap_dispersion"] = f_1.registerGap.map(lambda x: None if not x else np.std(x) / np.mean(x))
                f_1["registerGap_mode"] = f_1.registerGap.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["registerGap_mode_rate"] = f_1.registerGap.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["EMR002_bank_rate"] = f_1.EMR002_p_type.map(lambda x: None if not x else x.count("1") / len(x))
                f_1["EMR002_non_bank_rate"] = f_1.EMR002_p_type.map(lambda x: None if not x else x.count("2") / len(x))
                f_1["EMR002_platform_mode_rate"] = f_1.EMR002_platform.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))

            if len(df_004):
                f_1['EMR004_len'] = f_1.EMR004_platform.map(lambda x: None if not x else len(set(x)))
                f_1.EMR004_applyTime = f_1.EMR004_applyTime.map(
                    lambda x: None if not x else list(map(lambda x: hd_to_date(x), x)))
                f_1.EMR004_applyAmount = f_1.EMR004_applyAmount.map(
                    lambda x: None if not x else [amount_dict[i] for i in x])
                f_1["applyGap"] = f_1.EMR004_applyTime.map(lambda x: None if not x else hd_loan_gap(x))
                f_1["applyGap_max"] = f_1.applyGap.map(lambda x: None if not x else max(x))
                f_1["applyGap_min"] = f_1.applyGap.map(lambda x: None if not x else min(x))
                f_1["applyGap_std"] = f_1.applyGap.map(lambda x: None if not x else np.std(x))
                f_1["applyGap_mean"] = f_1.applyGap.map(lambda x: None if not x else np.mean(x))
                f_1["applyGap_median"] = f_1.applyGap.map(lambda x: None if not x else np.median(x))
                f_1["applyGap_dispersion"] = f_1.applyGap.map(lambda x: None if not x else np.std(x) / np.mean(x))
                f_1["applyGap_mode"] = f_1.applyGap.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["applyGap_mode_rate"] = f_1.applyGap.map(lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["applyAmount_max"] = f_1.EMR004_applyAmount.map(lambda x: None if not x else max(x))
                f_1["applyAmount_min"] = f_1.EMR004_applyAmount.map(lambda x: None if not x else min(x))
                f_1["applyAmount_mode"] = f_1.EMR004_applyAmount.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["applyAmount_mode_rate"] = f_1.EMR004_applyAmount.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["EMR004_bank_rate"] = f_1.EMR004_p_type.map(lambda x: None if not x else x.count("1") / len(x))
                f_1["EMR004_non_bank_rate"] = f_1.EMR004_p_type.map(lambda x: None if not x else x.count("2") / len(x))
                f_1["EMR004_platform_mode_rate"] = f_1.EMR004_platform.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))

            if len(df_007):
                f_1['EMR007_len'] = f_1.EMR007_platform.map(lambda x: None if not x else len(set(x)))
                f_1.EMR007_loanTime = f_1.EMR007_loanTime.map(
                    lambda x: None if not x else list(map(lambda x: hd_to_date(x), x)))
                f_1.EMR007_loanAmount = f_1.EMR007_loanAmount.map(
                    lambda x: None if not x else [amount_dict[i] for i in x])
                f_1["loanGap"] = f_1.EMR007_loanTime.map(lambda x: None if not x else hd_loan_gap(x))
                f_1["loanGap_max"] = f_1.loanGap.map(lambda x: None if not x else max(x))
                f_1["loanGap_min"] = f_1.loanGap.map(lambda x: None if not x else min(x))
                f_1["loanGap_std"] = f_1.loanGap.map(lambda x: None if not x else np.std(x))
                f_1["loanGap_mean"] = f_1.loanGap.map(lambda x: None if not x else np.mean(x))
                f_1["loanGap_median"] = f_1.loanGap.map(lambda x: None if not x else np.median(x))
                f_1["loanGap_dispersion"] = f_1.loanGap.map(lambda x: None if not x else np.std(x) / np.mean(x))
                f_1["loanGap_mode"] = f_1.loanGap.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["loanGap_mode_rate"] = f_1.loanGap.map(lambda x: None if not x else list(mode(x)[1])[0] / len(x))

                f_1["loanAmount_max"] = f_1.EMR007_loanAmount.map(lambda x: None if not x else max(x))
                f_1["loanAmount_min"] = f_1.EMR007_loanAmount.map(lambda x: None if not x else min(x))
                f_1["loanAmount_mode"] = f_1.EMR007_loanAmount.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["loanAmount_mode_rate"] = f_1.EMR007_loanAmount.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["EMR007_bank_rate"] = f_1.EMR007_p_type.map(lambda x: None if not x else x.count("1") / len(x))
                f_1["EMR007_non_bank_rate"] = f_1.EMR007_p_type.map(lambda x: None if not x else x.count("2") / len(x))
                f_1["EMR007_platform_mode_rate"] = f_1.EMR007_platform.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))

            if len(df_009):
                f_1['EMR009_len'] = f_1.EMR009_platform.map(lambda x: None if not x else len(set(x)))
                f_1.EMR009_rejectTime = f_1.EMR009_rejectTime.map(
                    lambda x: None if not x else list(map(lambda x: hd_to_date(x), x)))
                f_1["rejectGap"] = f_1.EMR009_rejectTime.map(lambda x: None if not x else hd_loan_gap(x))
                f_1["rejectGap_max"] = f_1.rejectGap.map(lambda x: None if not x else max(x))
                f_1["rejectGap_min"] = f_1.rejectGap.map(lambda x: None if not x else min(x))
                f_1["rejectGap_std"] = f_1.rejectGap.map(lambda x: None if not x else np.std(x))
                f_1["rejectGap_mean"] = f_1.rejectGap.map(lambda x: None if not x else np.mean(x))
                f_1["rejectGap_median"] = f_1.rejectGap.map(lambda x: None if not x else np.median(x))
                f_1["rejectGap_dispersion"] = f_1.rejectGap.map(lambda x: None if not x else np.std(x) / np.mean(x))
                f_1["rejectGap_mode"] = f_1.rejectGap.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["rejectGap_mode_rate"] = f_1.rejectGap.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["EMR009_bank_rate"] = f_1.EMR009_p_type.map(lambda x: None if not x else x.count("1") / len(x))
                f_1["EMR009_non_bank_rate"] = f_1.EMR009_p_type.map(lambda x: None if not x else x.count("2") / len(x))
                f_1["EMR009_platform_mode_rate"] = f_1.EMR009_platform.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))

            if len(df_012):
                f_1['EMR012_len'] = f_1.EMR012_platform.map(lambda x: None if not x else len(set(x)))
                f_1.EMR012_d_time = f_1.EMR012_d_time.map(lambda x: None if not x else list(map(lambda x: hd_s(x), x)))
                f_1["overGap"] = f_1.EMR012_d_time.map(lambda x: None if not x else hd_loan_gap(x))
                f_1["overAmount"] = f_1.EMR012_money.map(lambda x: None if not x else [amount_dict[i] for i in x])
                f_1.EMR012_counts = f_1.EMR012_counts.map(lambda x: None if not x else list(map(lambda x: eval(x), x)))
                f_1["EMR012_counts_max"] = f_1.EMR012_counts.map(lambda x: None if not x else max(x))
                f_1["EMR012_counts_min"] = f_1.EMR012_counts.map(lambda x: None if not x else min(x))
                f_1["EMR012_counts_mean"] = f_1.EMR012_counts.map(lambda x: None if not x else np.mean(x))
                f_1["EMR012_counts_std"] = f_1.EMR012_counts.map(lambda x: None if not x else np.std(x))
                f_1["EMR012_counts_median"] = f_1.EMR012_counts.map(lambda x: None if not x else np.median(x))
                f_1["EMR012_counts_dispersion"] = f_1.EMR012_counts.map(
                    lambda x: None if not x else np.std(x) / np.mean(x))
                f_1["EMR012_counts_mode"] = f_1.EMR012_counts.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["EMR012_counts_mode_rate"] = f_1.EMR012_counts.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["has_over"] = f_1.overAmount.map(lambda x: 0 if not x else 1)
                f_1["overAmount_max"] = f_1.overAmount.map(lambda x: None if not x else max(x))
                f_1["overAmount_min"] = f_1.overAmount.map(lambda x: None if not x else min(x))
                f_1["overAmount_mode"] = f_1.overAmount.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["overAmount_mode_rate"] = f_1.overAmount.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["EMR012_platform_mode_rate"] = f_1.EMR012_platform.map(lambda x: None if not x else 1 / len(x))

            if len(df_013):
                f_1['EMR013_len'] = f_1.EMR013_platform.map(lambda x: None if not x else len(set(x)))
                f_1["debtAmount"] = f_1.EMR013_money.map(lambda x: None if not x else [amount_dict[i] for i in x])
                f_1["has_debt"] = f_1.debtAmount.map(lambda x: 0 if not x else 1)
                f_1["debtAmount_max"] = f_1.debtAmount.map(lambda x: None if not x else max(x))
                f_1["debtAmount_min"] = f_1.debtAmount.map(lambda x: None if not x else min(x))
                f_1["debtAmount_mode"] = f_1.debtAmount.map(lambda x: None if not x else list(mode(x)[0])[0])
                f_1["debtAmount_mode_rate"] = f_1.debtAmount.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))
                f_1["EMR013_platform_mode_rate"] = f_1.EMR013_platform.map(
                    lambda x: None if not x else list(mode(x)[1])[0] / len(x))

            for i in f_1.columns:
                df[i] = f_1[i]

            df.loanRatio = df.EMR004_len / df.EMR002_len
            df.approvedRatio = df.EMR007_len / df.EMR004_len
            df.rejectRatio = df.EMR009_len / df.EMR004_len
            df.defaultRatio = df.EMR012_len / df.EMR004_len
            df.debtRatio = df.EMR013_len / df.EMR004_len

        else:
            print("华道征信数据未获取")

        feats = [i for i in df.columns if i not in ['overduedays', 'startDate', 'loan_time', 'status',
                                                    'query_time', 'response',
                                                    'EMR002', 'EMR004', 'EMR007', 'EMR009', 'EMR012', 'EMR013',
                                                    'EMR002_p_type', 'EMR002_platform', 'EMR002_registerTime',
                                                    'EMR004_applyAmount', 'EMR004_applyResult', 'EMR004_applyTime',
                                                    'EMR004_p_type', 'EMR004_platform',
                                                    'EMR007_loanAmount', 'EMR007_loanTime', 'EMR007_p_type',
                                                    'EMR007_platform',
                                                    'EMR009_p_type', 'EMR009_platform', 'EMR009_rejectTime',
                                                    'EMR012_counts', 'EMR012_d_time', 'EMR012_money',
                                                    'EMR012_platform',
                                                    'EMR013_money', 'EMR013_platform',
                                                    'overAmount', 'debtAmount',
                                                    'registerGap', 'applyGap', 'loanGap', 'rejectGap', 'overGap']]

        df = df[feats]
        for i in df.columns:
            if i != 'uid':
                df.rename(columns={i: i + "_hd"}, inplace=True)

        # df = df[~df.uid.duplicated()]
        return df

    def get_no(self):
        df = pd.DataFrame(columns=df_91.columns, index=range(len(self.uid)))
        if len(self.uid) == 1:
            tmp = pd.read_sql("""select a.userId as uid, a.status, a.platformResponse 
                                        from eva_riskcontrol_91credit_multilateral as a
                                        left join
                                        (select userId, max(createdAt) as createdAt
                                        from eva_riskcontrol_91credit_multilateral group by userId) as b
                                        on a.userId = b.userId
                                        where a.createdAt = b.createdAt
                                        and a.status = 'success'
                                        and a.userId > 100
                                        and a.userId = {}
                                        order by a.userId
                                        """.format(self.uid[0]), engine_1)
        else:
            tmp = pd.read_sql("""select a.userId as uid, a.status, a.platformResponse 
                                        from eva_riskcontrol_91credit_multilateral as a
                                        left join
                                        (select userId, max(createdAt) as createdAt
                                        from eva_riskcontrol_91credit_multilateral group by userId) as b
                                        on a.userId = b.userId
                                        where a.createdAt = b.createdAt
                                        and a.status = 'success'
                                        and a.userId > 100
                                        and a.userId in {}
                                        order by a.userId
                                        """.format(tuple(self.uid)),engine_1)
        tmp.index = range(len(tmp))
        if len(tmp):
            df['uid'] = tmp.uid
            if True in df.uid.isnull().value_counts():
                self.fail_sql_no = list(set(self.uid) - set(tmp.uid))
            df['status'] = tmp.status
            df["response"] = tmp.platformResponse.map(lambda x: json.loads(x))

            loanType = []
            loanState = []
            loanAmount = []
            repayState = []
            loanTime = []
            arrearsAmount = []
            loanPeriod = []
            companyCode = []
            startDate = []
            for i in df.uid:
                try:
                    res = NOParser(int(i))
                    loanType.append(res.loanType)
                    loanState.append(res.loanState)
                    loanAmount.append(res.loanAmount)
                    repayState.append(res.repayState)
                    arrearsAmount.append(res.arrearsAmount)
                    loanTime.append(len(res.loanType))
                    loanPeriod.append(res.loanPeriod)
                    companyCode.append(res.companyCode)
                    startDate.append(res.startDate)
                except:
                    loanType.append(None)
                    loanState.append(None)
                    loanAmount.append(None)
                    repayState.append(None)
                    arrearsAmount.append(None)
                    loanTime.append(0)
                    loanPeriod.append(None)
                    companyCode.append(None)
                    startDate.append(None)

            loanType = pd.Series(loanType)
            loanState = pd.Series(loanState)
            loanAmount = pd.Series(loanAmount)
            repayState = pd.Series(repayState)
            loanTime = pd.Series(loanTime)
            arrearsAmount = pd.Series(arrearsAmount)
            companyCode = pd.Series(companyCode)
            loanPeriod = pd.Series(loanPeriod)
            startDate = pd.Series(startDate)

            df["loanType"] = loanType
            df["loanState"] = loanState
            df["loanAmount"] = loanAmount
            df["repayState"] = repayState
            df["arrearsAmount"] = arrearsAmount
            df["loanTime"] = loanTime
            df["loanPeriod"] = loanPeriod
            df["companyCode"] = companyCode
            df["startDate"] = startDate

            df['timestamp'] = startDate
            df.startDate = df.startDate.map(lambda x:None if not x else list(map(lambda x: datetime.datetime.fromtimestamp(x).date(), x)))

            p = Pool(12)
            result = []
            for i in df.index:
                result.append(p.apply_async(myfliter_91, (df.loc[i], self.audit)))
            p.close()
            p.join()

            res = {}
            for p in range(len(result)):
                res[p] = result[p].get()

            loanType = []
            loanState = []
            loanAmount = []
            repayState = []
            loanTime = []
            arrearsAmount = []
            companyCode = []
            loanPeriod = []
            startDate = []
            for i in range(len(res)):
                if res[i]:
                    loanType.append(res[i]["loanType"])
                    loanState.append(res[i]["loanState"])
                    loanAmount.append(res[i]["loanAmount"])
                    repayState.append(res[i]["repayState"])
                    loanTime.append(res[i]["loanTime"])
                    arrearsAmount.append(res[i]["arrearsAmount"])
                    companyCode.append(res[i]["companyCode"])
                    loanPeriod.append(res[i]["loanPeriod"])
                    startDate.append(res[i]["startDate"])
                else:
                    loanType.append([])
                    loanState.append([])
                    loanAmount.append([])
                    repayState.append([])
                    loanTime.append(0)
                    arrearsAmount.append([])
                    companyCode.append([])
                    loanPeriod.append([])
                    startDate.append([])
            df["loanType"] = loanType
            df["loanState"] = loanState
            df["loanAmount"] = loanAmount
            df["repayState"] = repayState
            df["arrearsAmount"] = arrearsAmount
            df["loanTime"] = loanTime
            df["loanPeriod"] = loanPeriod
            df["companyCode"] = companyCode
            df["startDate"] = startDate

            df.has_arrears = df.arrearsAmount.map(lambda x: 1 if any(x) else 0)
            df.arrears_min = df.arrearsAmount.map(lambda x: None if len(x) == 0 else min(x))
            df.arrears_max = df.arrearsAmount.map(lambda x: None if len(x) == 0 else max(x))
            df.arrears_std = df.arrearsAmount.map(lambda x: None if len(x) == 0 else np.std(x))
            df.arrears_mean = df.arrearsAmount.map(lambda x: None if len(x) == 0 else np.mean(x))
            df.arrears_median = df.arrearsAmount.map(lambda x: None if len(x) == 0 else np.median(x))

            df.loanType_0 = df.loanType.map(lambda x: None if len(x) == 0 else x.count(0) / len(x))
            df.loanType_1 = df.loanType.map(lambda x: None if len(x) == 0 else x.count(1) / len(x))
            df.loanType_2 = df.loanType.map(lambda x: None if len(x) == 0 else x.count(2) / len(x))
            df.loanType_3 = df.loanType.map(lambda x: None if len(x) == 0 else x.count(3) / len(x))
            df.loanType_4 = df.loanType.map(lambda x: None if len(x) == 0 else x.count(4) / len(x))

            df.loanType_mode = df.loanType.map(lambda x: None if len(x) == 0 else list(mode(x)[0])[0])
            df.loanType_mode_rate = df.loanType.map(lambda x: None if len(x) == 0 else list(mode(x)[1])[0] / len(x))

            df.loanAmount_0 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(0) / len(x))
            df.loanAmount_1 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-1) / len(x))
            df.loanAmount_2 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-2) / len(x))
            df.loanAmount_3 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-3) / len(x))
            df.loanAmount_4 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-4) / len(x))
            df.loanAmount_5 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-5) / len(x))
            df.loanAmount_6 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-6) / len(x))
            df.loanAmount_7 = df.loanAmount.map(lambda x: None if len(x) == 0 else x.count(-7) / len(x))
            df.loanAmount_8 = df.loanAmount.map(
                lambda x: None if len(x) == 0 else np.mean(list(map(lambda x: x >= 1, x))))
            df.loanAmount_max = df.loanAmount.map(lambda x: None if len(x) == 0 else max(x))
            df.loanAmount_min = df.loanAmount.map(lambda x: None if len(x) == 0 else min(x))
            df.loanAmount_std = df.loanAmount.map(lambda x: None if len(x) == 0 else np.std(x))
            df.loanAmount_mean = df.loanAmount.map(lambda x: None if len(x) == 0 else np.mean(x))
            df.loanAmount_median = df.loanAmount.map(lambda x: None if len(x) == 0 else np.median(x))
            df.loanAmount_mode = df.loanAmount.map(lambda x: None if len(x) == 0 else list(mode(x)[0])[0])
            df.loanAmount_mode_rate = df.loanAmount.map(lambda x: None if len(x) == 0 else list(mode(x)[1])[0] / len(x))

            df.loanState_0 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(0) / len(x))
            df.loanState_1 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(1) / len(x))
            df.loanState_2 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(2) / len(x))
            df.loanState_3 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(3) / len(x))
            df.loanState_4 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(4) / len(x))
            df.loanState_5 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(5) / len(x))
            df.loanState_6 = df.loanState.map(lambda x: None if len(x) == 0 else x.count(6) / len(x))

            df.loanState_approved = df.loanState_2 + df.loanState_3 + df.loanState_6

            df.loanState_mode = df.loanState.map(lambda x: None if len(x) == 0 else list(mode(x)[0])[0])
            df.loanState_mode_rate = df.loanState.map(lambda x: None if len(x) == 0 else list(mode(x)[1])[0] / len(x))

            df.loanPeriod_0 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(0))
            df.loanPeriod_1 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(1))
            df.loanPeriod_2 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(2))
            df.loanPeriod_3 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(3))
            df.loanPeriod_4 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(4))
            df.loanPeriod_5 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(5))
            df.loanPeriod_6 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(6))
            df.loanPeriod_9 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(9))
            df.loanPeriod_10 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(10))
            df.loanPeriod_11 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(11))
            df.loanPeriod_12 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(12))
            df.loanPeriod_13 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(13))
            df.loanPeriod_18 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(18))
            df.loanPeriod_21 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(21))
            df.loanPeriod_24 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(24))
            df.loanPeriod_36 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(36))
            df.loanPeriod_48 = df.loanPeriod.map(lambda x: None if len(x) == 0 else x.count(48))

            df.loanPeriod_max = df.loanPeriod.map(lambda x: None if len(x) == 0 else max(x))
            df.loanPeriod_min = df.loanPeriod.map(lambda x: None if len(x) == 0 else min(x))
            df.loanPeriod_std = df.loanPeriod.map(lambda x: None if len(x) == 0 else np.std(x))
            df.loanPeriod_mean = df.loanPeriod.map(lambda x: None if len(x) == 0 else np.mean(x))

            df.loanPeriod_mode = df.loanPeriod.map(lambda x: None if len(x) == 0 else list(mode(x)[0])[0])
            df.loanPeriod_mode_rate = df.loanPeriod.map(lambda x: None if len(x) == 0 else list(mode(x)[1])[0] / len(x))

            df.repayState_0 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(0) / len(x))
            df.repayState_1 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(1) / len(x))
            df.repayState_2 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(2) / len(x))
            df.repayState_3 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(3) / len(x))
            df.repayState_4 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(4) / len(x))
            df.repayState_5 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(5) / len(x))
            df.repayState_6 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(6) / len(x))
            df.repayState_7 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(7) / len(x))
            df.repayState_8 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(8) / len(x))
            df.repayState_9 = df.repayState.map(lambda x: None if len(x) == 0 else x.count(9) / len(x))

            df.repayState_overdue = df.repayState_2 + df.repayState_3 + df.repayState_4 + \
                                    df.repayState_5 + df.repayState_6 + df.repayState_7 + df.repayState_8

            df.repayState_mode = df.repayState.map(lambda x: None if len(x) == 0 else list(mode(x)[0])[0])
            df.repayState_mode_rate = df.repayState.map(lambda x: None if len(x) == 0 else list(mode(x)[1])[0] / len(x))

            df.startDate = df.startDate.map(lambda x: sorted(x))
            loangap = df.startDate.map(lambda x: loan_gap_91(x))
            df.loangap_max = loangap.map(lambda x: None if len(x) == 0 else max(x))
            df.loangap_min = loangap.map(lambda x: None if len(x) == 0 else min(x))
            df.loangap_std = loangap.map(lambda x: None if len(x) == 0 else np.std(x))
            df.loangap_mean = loangap.map(lambda x: None if len(x) == 0 else np.mean(x))
            df.loangap_median = loangap.map(lambda x: None if len(x) == 0 else np.median(x))

            df['month'] = df.startDate.map(lambda x: None if len(x) == 0 else list(map(lambda x: x.isoformat()[:7], x)))

            # 最近一个月的借贷次数
            df.lastest_loan = df.month.map(lambda x: None if not x else pd.Series(x).value_counts()[max(x)])
            # 每月最高的借贷次数
            df.loantime_max = df.month.map(lambda x: None if not x else pd.Series(x).value_counts().max())
            # 平均的每月借贷次数
            df.loantime_mean = df.month.map(lambda x: None if not x else
            pd.Series(x).value_counts().sum() / len(pd.Series(x).value_counts()))

            odState = df.repayState.apply(
                lambda x: None if len(x) == 0 else np.mean(list(map(lambda x: x in range(2, 8), x))))
            df.has_od = odState.map(f1_91)

            company_P2P = df.companyCode.apply(
                lambda x: None if len(x) == 0 else np.mean(list(map(lambda x: x[:3] == 'P2P', x))))
            df.companyLen = df.companyCode.apply(lambda x: None if len(x) == 0 else len(set(x)))

            df.black_list = company_P2P.map(f2_91)

            oh_1 = pd.get_dummies(df.loanType_mode, prefix='loanT')
            oh_2 = pd.get_dummies(df.loanAmount_mode, prefix='loanA')
            oh_3 = pd.get_dummies(df.loanState_mode, prefix='loanS')
            oh_4 = pd.get_dummies(df.repayState_mode, prefix='repayS')

            tt = pd.concat([oh_1, oh_2, oh_3, oh_4], axis=1)
            for i in tt.columns:
                for j in ['loanA_', 'loanS_', 'repayS_', 'loanT_']:
                    if j in i and i[-2:]=='.0':
                        tt.rename(columns={i: i[:-2]}, inplace=True)

            for i in tt.columns:
                df[i] = tt[i]

            for i in df_91.columns:
                for j in ['loanA_', 'loanS_', 'repayS_', 'loanT_']:
                    if j in i:
                        #             print(i)
                        df[i].fillna(int(0), inplace=True)
        else:
            print("91征信数据未获取")

        feats = [i for i in df.columns if i not in ['loanType', 'loanState', 'loanAmount', 'month', 'label',
                                                    'repayState', 'loan_time', 'arrearsAmount', 'companyCode',
                                                    'loanPeriod', 'overduedays', 'startDate', 'status',
                                                    'response', 'timestamp']]

        df = df[feats]
        for i in df.columns:
            if i != 'uid':
                df.rename(columns={i: i + "_91"}, inplace=True)
        return df

    def get_sms(self):
        df = pd.DataFrame(columns=df_sms.columns,index=range(len(self.uid)))

        df['uid'] = pd.Series(self.uid, name='uid')
        tmp = []
        content = []
        startDate = []
        ct = []

        if len(self.loan_time) == 1:
            if self.loan_time[0] == 1:
                df['loan_time'] = 1
                startDate = [self.audit[self.audit.uid == self.uid].startDate.iloc[self.loan_time[0] - 1]]
            elif self.loan_time[0] == -1:
                lt = int(self.first[self.first.uid == self.uid].loan_time.max())
                df['loan_time'] = lt
                startDate = [self.first[self.first.uid == self.uid].startDate.iloc[lt - 1]]
            else:
                df['loan_time'] = self.loan_time[0] - 1
                startDate = [self.first[self.first.uid == self.uid].startDate.iloc[self.loan_time[0] - 1]]
            if isinstance(startDate[0], datetime.date):
                ct = [int(time.mktime(startDate[0].timetuple()))]
            if isinstance(startDate[0], str):
                ct = [int(time.mktime(datetime.datetime.strptime(startDate[0], "%Y-%m-%d")))]
        else:
            for i in df.index:
                if self.loan_time[i] == 1 or self.loan_time[i] == None:
                    tmp.append(1)
                    startDate.append(self.audit[self.audit.uid == self.uid[i]].startDate.iloc[self.loan_time[i] - 1])
                elif self.loan_time[i] == -1:
                    lt = int(self.first[self.first.uid == self.uid[i]].loan_time.max())
                    tmp.append(lt)
                    startDate.append(self.first[self.first.uid == self.uid[i]].startDate.iloc[lt - 1])
                else:
                    tmp.append(self.loan_time[i])
                    startDate.append(self.first[self.first.uid == self.uid[i]].startDate.iloc[self.loan_time[i] - 1])
                if isinstance(startDate[i], datetime.date):
                    ct.append(int(time.mktime(startDate[i].timetuple())))
                if isinstance(startDate[i], str):
                    ct.append(int(time.mktime(datetime.datetime.strptime(startDate[i], "%Y-%m-%d"))))
        num = 0
        for i in df.index:
            num += 1
            s = merge_all_sms(session_1, self.uid[i], ct[i])
            content.append(s)

        df['content'] = content
        df['has_SMS'] = df.content.map(lambda x: 1 if x else 0)

        if df['has_SMS'].sum() == 0:
            print("所有用户均未获取短信")
        else:
            pattern_CN = '(\【[\u4e00-\u9fa5]*?\】)'
            pattern_EN = '(\[[\u4e00-\u9fa5]*?\])'
            pattern_CN_NU = '(\【[\u4e00-\u9fa5]+?[0-9]+?\】)'
            pattern_EN_NU = '(\[[\u4e00-\u9fa5]+?[0-9]+?\])'

            m_loan_app_CN = df.content.apply(lambda x: re.findall(pattern_CN, x))
            m_loan_app_EN = df.content.apply(lambda x: re.findall(pattern_EN, x))
            m_loan_app_CN_NU = df.content.apply(lambda x: re.findall(pattern_CN_NU, x))
            m_loan_app_EN_NU = df.content.apply(lambda x: re.findall(pattern_EN_NU, x))

            # tmp = [list(pd.Series(m_loan_app_CN[i]).unique()) for i in range(len(m_loan_app_CN))]
            m_loan_app_CN_unique = [list(pd.Series(i).unique()) for i in list(m_loan_app_CN)]
            m_loan_app_EN_unique = [list(pd.Series(i).unique()) for i in list(m_loan_app_EN)]
            m_loan_app_CN_NU_unique = [list(pd.Series(i).unique()) for i in list(m_loan_app_CN_NU)]
            m_loan_app_EN_NU_unique = [list(pd.Series(i).unique()) for i in list(m_loan_app_EN_NU)]

            loan_apps_CN = wipe_sms(m_loan_app_CN_unique)
            loan_apps_EN = wipe_sms(m_loan_app_EN_unique)
            loan_apps_CN_NU = wipe_sms(m_loan_app_CN_NU_unique)
            loan_apps_EN_NU = wipe_sms(m_loan_app_EN_NU_unique)

            m_apps = [loan_apps_CN[i] + loan_apps_EN[i] + loan_apps_CN_NU[i] + loan_apps_EN_NU[i] for i in range(len(df))]
            m_apps = pd.Series(m_apps, index=df.index)

            # loan_list = ["金","信","贷款","借","筹","分期","钱","资金","支付","融","人人花"]
            # num_loan_app = pd.Series(count_loan_apps(m_apps, loan_list))

            loan_apps = apps[apps.category.map(lambda x: '借贷' in x)].appName.tolist()
            loan_apps.append('暖手好贷')
            df.num_loan_app = m_apps.map(lambda x: len(set(x).intersection(set(loan_apps))))

            df.num_sms = df.content.apply(lambda x: x.count('smsFrom'))
            df.num_apps = pd.Series(m_apps.apply(lambda x: len(x)))

            # 查找关键字
            key_1, key_2, key_3, key_4, key_5 = "未通过审核", "通过审核", "用款申请", "申请袋 款", "放款"
            key_6, key_7, key_8, key_9, key_10 = "尽快还款", "已逾期", "催收部", "欠款逾期", "透支"
            key_11, key_12, key_13, key_14, key_15 = "金额", "金融", "额度", "还款", "借款"
            key_16, key_17, key_18, key_19, key_20 = "欠费", "余额不足", "中国移动", "中国电信", "中国联通"
            key_21, key_22, key_23, key_24, key_25 = "贷款", "分期", "账单", "结欠", "到期"
            key_26, key_27, key_28, key_29, key_30 = "未还金额", "借条", "逾期", "已经结清", "罚息"
            key_31, key_32, key_33, key_34, key_35 = "现金", "信用", "支付", "违约", "法院"
            key_36, key_37, key_38, key_39, key_40 = "钱包", "征信", "应还金额", "银行", "消费"

            for ix, i in enumerate([key_1, key_2, key_3, key_4, key_5,
                                    key_6, key_7, key_8, key_9, key_10,
                                    key_11, key_12, key_13, key_14, key_15,
                                    key_16, key_17, key_18, key_19, key_20,
                                    key_21, key_22, key_23, key_24, key_25,
                                    key_26, key_27, key_28, key_29, key_30,
                                    key_31, key_32, key_33, key_34, key_35,
                                    key_36, key_37, key_38, key_39, key_40
                                    ]):
                df['key_' + str(ix + 1)] = df.content.apply(lambda x: x.count(i))

            # 统计余额类特征
            pattern_1 = r'余额[1-9][0-9]+[\.\,\，元][0-9]+'
            pattern_2 = r'应还金额[1-9][0-9]+[\.\,\，元][0-9]+'
            # 统计余额列表
            df['balance'] = df.content.apply(lambda x: re.findall(pattern_1, x))
            # 统计金额列表
            df['amount'] = df.content.apply(lambda x: re.findall(pattern_2, x))
            df.balance = df.balance.apply(lambda x: None if len(x) == 0 else list(map(get_number_sms, x)))
            df.amount = df.amount.apply(lambda x: None if len(x) == 0 else list(map(lambda x: get_number_sms(x[2:]), x)))

            df["num_of_consum"] = df.balance.apply(lambda x: None if x == None else len(x))
            df["balance_max"] = df.balance.map(lambda x: None if x == None else max(x))
            df["balance_min"] = df.balance.map(lambda x: None if x == None else min(x))
            df["balance_mean"] = df.balance.map(lambda x: None if x == None else np.mean(x))
            df["balance_std"] = df.balance.map(lambda x: None if x == None else np.std(x))

            df["amount_max"] = df.amount.map(lambda x: None if x == None else max(x))
            df["amount_min"] = df.amount.map(lambda x: None if x == None else min(x))
            df["amount_mean"] = df.amount.map(lambda x: None if x == None else np.mean(x))
            df["amount_std"] = df.amount.map(lambda x: None if x == None else np.std(x))

        df['loan_time'] = pd.Series(tmp)

        feats = [i for i in df.columns if
                 i not in ['overduedays', 'termAsday', 'label', 'content', 'balance', 'amount']]
        return df[feats]

    def get_call(self):
        df = pd.DataFrame(columns=df_call.columns,index=range(len(self.uid)))

        df['uid'] = pd.Series(self.uid, name='uid')
        df['contacts_num'] = np.NaN
        df['Conversation_with_contacts_num'] = np.NaN
        df['Conversation_with_emergency_num'] = np.NaN

        for index, i in enumerate(self.uid):
            tmp1 = pd.read_sql("""select userId, contactList 
                                  from eva_riskcontrol_contactlists 
                                  where userId = {}""".format(i), engine_1)
            if tmp1.shape[0] == 0:
                tmp1 = pd.DataFrame([[np.NaN, np.NaN]], columns=tmp1.columns)
            tmp1['num'] = tmp1['contactList'].map(lambda s: f1_call(s))
            tmp1['phone_list'] = tmp1['contactList'].map(lambda s: f3_call(s))
            contact_num = tmp1['num'][0]
            numList1 = tmp1['phone_list'][0]
            tmp2 = pd.read_sql("""select userId,mobile 
                                    from eva_user_contacts 
                                    where userId = {}""".format(i), engine_1)
            tmp2 = tmp2.groupby(['userId'])['mobile'].agg([('emergencyContacts', f2_call)]).reset_index()
            numList2 = tmp2['emergencyContacts'][0]

            x = CallParser(int(i))
            if x.hasContent:
                commDf = x.commDf
                numList3 = list(commDf['another_nm'])
            else:
                numList3 = [[[]]]
            count_0 = 0
            count_1 = 0
            for mm in numList3:
                if mm in numList1[0]:
                    count_0 = count_0 + 1
                if mm in numList2[0]:
                    count_1 = count_1 + 1
            df['contacts_num'][index] = contact_num
            df['Conversation_with_contacts_num'][index] = count_0
            df['Conversation_with_emergency_num'][index] = count_1

        p = Pool(12)
        result = []
        for i in self.uid:
            result.append(p.apply_async(f_call, (CallParser(int(i)),)))
        p.close()
        p.join()
        res = {}
        for p, q in zip(range(len(result)), sorted(df.uid)):
            res[q] = result[p].get()
        data = pd.DataFrame(res).T
        data.index = range(len(data))
        for i in data.columns:
            df[i] = data[i]

        df["comm_gap_min"] = df.comm_gap.map(lambda x: min(x) if x else None)
        df["comm_gap_max"] = df.comm_gap.map(lambda x: max(x) if x else None)
        df["comm_gap_std"] = df.comm_gap.map(lambda x: np.std(x) if x else None)
        df["comm_gap_mean"] = df.comm_gap.map(lambda x: np.mean(x) if x else None)
        df["comm_gap_median"] = df.comm_gap.map(lambda x: np.median(x) if x else None)
        df["comm_gap_mode"] = df.comm_gap.map(lambda x: list(mode(x)[0])[0] if x else None)
        df["comm_gap_mode_rate"] = df.comm_gap.map(lambda x: list(mode(x)[0])[0] / len(x) if x else None)
        df["weekend_rate"] = df.weekday_6 + df.weekday_7
        df.num_coll_call.fillna(109, inplace=True)
        df["has_coll_call"] = df.num_coll_call.map(lambda x: 1 if x > 0 else 0)
        df["clock_interval"] = df.clock_mode.map(lambda x: classify_call(x) if x else None)
        company = pd.get_dummies(df.company)
        ii = pd.get_dummies(df.clock_interval, prefix="通话时间段_")

        tt = pd.concat([company, ii], axis=1)

        for i in tt.columns:
            df[i] = tt[i]

        for i in df.columns:
            for j in ['CHINA_', '通话时间段_']:
                if j in i:
                    #             print(i)
                    df[i].fillna(int(0), inplace=True)

        feats = [i for i in df.columns if i not in ['termAsday', 'overduedays', 'loan_time', 'label',
                                                    'another_comm_mode', 'another_comm_mode_rate',
                                                    'another_comm_number',
                                                    'comm_gap', 'company', 'place_mode', 'type_mode',
                                                    'term_7', 'term_14', 'term_28', 'clock_interval',
                                                    'bank_info_call', 'bank_info_number', 'bank_info_call_count_1m',
                                                    'bank_info_call_count_3m', 'blacklist_info_call',
                                                    'blacklist_info_number', 'loan_info_call', 'loan_info_number',
                                                    'collect_info_call', 'collect_info_number', 'ordinary_info_call',
                                                    'ordinary_info_number', 'high_risk_info_call',
                                                    'high_risk_info_number',
                                                    'takeout_info_call', 'takeout_info_number']]
        return df[feats]

    def get_td(self):
        df = pd.DataFrame(columns=df_td.columns, index=range(len(self.uid)))
        if len(self.uid) == 1:
            tmp = pd.read_sql("""select userId as uid,platformResponseParams from eva_riskcontrol_background_tasks 
                                          where platform = 'tongdun' 
                                          and type = 'tongdun_pre_loan_report_fetch' 
                                          and status = 'success' 
                                          and userId = {}""".format(self.uid[0]), engine_1)
        else:
            tmp = pd.read_sql("""select userId as uid,platformResponseParams from eva_riskcontrol_background_tasks 
                                  where platform = 'tongdun' 
                                  and type = 'tongdun_pre_loan_report_fetch' 
                                  and status = 'success' 
                                  and userId in {}""".format(tuple(self.uid)), engine_1)
        tmp = tmp[~tmp.uid.duplicated()]
        tmp.index = range(len(tmp))
        df['uid'] = tmp.uid
        if True in df.uid.isnull().value_counts():
            self.fail_sql_td = list(set(self.uid)-set(tmp.uid))
        if len(tmp):
            platformResponseParams = tmp['platformResponseParams'].tolist()
            tt = []
            for i in range(len(platformResponseParams)):
                raw_data = platformResponseParams[i]
                tt.append(get_feature_td(raw_data))

            train = pd.DataFrame(tt)

            for i in train.columns:
                for j in ['risk_level', 'device_info_deviceType', 'type', 'final_decision']:
                    if j in i:
                        temp = pd.get_dummies(train[i], prefix=i)
                        train = pd.concat([train, temp], axis=1)
                        del train[i]

            for i in train.columns:
                df[i] = train[i]

            for i in set(df.columns) - set(df_td.columns):
                del df[i]

            for i in df.columns:
                for j in ['risk_level', 'device_info_deviceType', 'type', 'final_decision']:
                    if j in i:
                        df[i].fillna(int(0), inplace=True)
        else:
            print("同盾报告未获取")
        return df

    def get_zm(self):
        df = pd.DataFrame(columns=df_zm.columns,index=range(len(self.uid)))
        del df['zmxyScore']
        if len(self.uid) == 1:
            tmp = pd.read_sql("""select b.id as uid,
                                            d.zmxyIvsVerification,d.zmxyFraudTaskId,d.zmxyIvsWatchListTaskId
                                            from
                                            (select distinct userId 
                                            from eva_riskcontrol_audits) as a 
                                            join eva_user_users as b
                                            on a.userId = b.Id
                                            join eva_user_profiles as c
                                            on a.userId = c.userId
                                            join eva_riskcontrol_credits as d
                                            on a.userId = d.userId
                                            where b.id = {}""".format(self.uid[0]), engine_1)
        else:
            tmp = pd.read_sql("""select b.id as uid,
                                    d.zmxyIvsVerification,d.zmxyFraudTaskId,d.zmxyIvsWatchListTaskId
                                    from
                                    (select distinct userId 
                                    from eva_riskcontrol_audits) as a 
                                    join eva_user_users as b
                                    on a.userId = b.Id
                                    join eva_user_profiles as c
                                    on a.userId = c.userId
                                    join eva_riskcontrol_credits as d
                                    on a.userId = d.userId
                                    where b.id in {}""".format(tuple(self.uid)), engine_1)
        tmp.index = range(len(tmp))
        df['uid'] = tmp.uid
        if True in df.uid.isnull().value_counts():
            self.fail_sql_zm = list(set(self.uid)-set(tmp.uid))

        tmp['zmxyFraud'] = tmp.zmxyFraudTaskId.map(deal_zmxyFraudTaskId)
        tmp['zmxyIvsWatchList'] = tmp.zmxyIvsWatchListTaskId.map(deal_zmxyIvsWatchListTaskId)

        if len(tmp):

            tmp['zmxyIvsVerification'] = tmp['zmxyIvsVerification'].apply(lambda x: str(x).split(','))

            # zmxyIvsVerification构造
            tmp['芝麻IVS认证长度'] = tmp['zmxyIvsVerification'].apply(lambda x: len(x))
            tmp['芝麻V1'] = tmp['zmxyIvsVerification'].apply(lambda x: x[0])
            tmp['芝麻V2'] = list(
                map(lambda x, y: x[1] if y > 1 else 'None_v2', tmp['zmxyIvsVerification'], tmp['芝麻IVS认证长度']))
            tmp['芝麻V3'] = list(
                map(lambda x, y: x[2] if y > 2 else 'None_V3', tmp['zmxyIvsVerification'], tmp['芝麻IVS认证长度']))
            tmp['芝麻V4'] = list(
                map(lambda x, y: x[3] if y > 3 else 'None_V4', tmp['zmxyIvsVerification'], tmp['芝麻IVS认证长度']))

            t1 = pd.get_dummies(tmp['芝麻V1'], prefix='one_hot_V1')
            tmp = pd.concat([tmp, t1], axis=1)

            # t1.columns=['None_V1', 'V_CN_NA', 'V_CN_NM_MA', 'V_CN_NM_UM']
            t2 = pd.get_dummies(tmp['芝麻V2'], prefix='one_hot_V2')
            tmp = pd.concat([tmp, t2], axis=1)

            t3 = pd.get_dummies(tmp['芝麻V3'], prefix='one_hot_V3')
            tmp = pd.concat([tmp, t3], axis=1)

            t4 = pd.get_dummies(tmp['芝麻V4'], prefix='one_hot_V4')
            tmp = pd.concat([tmp, t4], axis=1)

            # del t1, t2, t3, t4
            # zmxyFraud构造

            tmp['芝麻F1'] = tmp['zmxyFraud'].apply(replace_zm)
            tmp['芝麻F2_total'] = list(
                map(lambda x, y: eval(x)['total'] if y == 'have_F1' else 0, tmp['zmxyFraud'], tmp['芝麻F1']))
            tmp['芝麻F3_settled'] = list(
                map(lambda x, y: eval(x)['settled'] if y == 'have_F1' else 0, tmp['zmxyFraud'], tmp['芝麻F1']))
            tmp['芝麻F3_unsettle'] = list(
                map(lambda x, y: eval(x)['unsettled'] if y == 'have_F1' else 0, tmp['zmxyFraud'], tmp['芝麻F1']))
            #
            f1 = pd.get_dummies(tmp['芝麻F1'], prefix='one_hot_F1')
            tmp = pd.concat([tmp, f1], axis=1)

            # del f1

            # zmxyIvsWatchList 构造

            tmp['芝麻关注名单数目'] = tmp['zmxyIvsWatchList'].apply(replace2_zm)

            del_list = ['芝麻V1', '芝麻V2', '芝麻V3', '芝麻V4', 'zmxyIvsVerification',
                        '芝麻F1', 'zmxyFraud', 'zmxyIvsWatchList', 'zmxyFraudTaskId',
                        'zmxyIvsWatchListTaskId', 'zmxyScore']

            for i in del_list:
                if i in tmp.columns:
                    del tmp[i]

            for i in tmp.columns:
                df[i] = tmp[i]
        else:
            print("芝麻欺诈、芝麻关注名单未获取")

        return df

    def prepare_data(self):
        # try:
        #     self.sms = self.get_sms()
        # except:
        #     print("短信特征工程失败")
        try:
            self.up = self.get_up()
        except:
            print("个人基本信息特征工程失败")
        try:
            self.hd = self.get_hd()
        except:
            print("华道征信特征工程失败")
        try:
            self.no = self.get_no()
        except:
            print("91征信特征工程失败")
        # try:
        #     self.call = self.get_call()
        # except:
        #     print("通话记录特征工程失败")
        try:
            self.td = self.get_td()
        except:
            print("同盾特征工程失败")
        try:
            self.zm = self.get_zm()
        except:
            print("芝麻征信特征工程失败")
        try:
            tmp = pd.concat([self.up, self.hd, self.no, self.td, self.zm], axis=1)
            print("特征工程成功")
        except:
            print("特征工程失败")
        return tmp.T[~tmp.columns.duplicated()].T


    # @classmethod
    # def transform(self, df):
    #
    #     features_info = pd.read_csv(r'/home/heyang/data/IV/feature_info.csv')
    #
    #     colname = features_info.columns.tolist()
    #     valname = features_info.ix[0, :].tolist()
    #
    #     dic_val_num = {}
    #     dic_num_val = {}
    #     for i in range(len(colname)):
    #         dic_val_num[valname[i]] = colname[i]
    #         dic_num_val[colname[i]] = valname[i]
    #
    #     sql = """select * from varname_hy;"""
    #     varname = pd.read_sql(sql, engine_2)
    #
    #     ConVar1 = list(varname.convar)
    #     ConVar1 = [x for x in ConVar1 if x != None]
    #     CatVar1 = list(varname.catvar)
    #
    #     ConVar = []
    #     CatVar = []
    #     for var in ConVar1:
    #         ConVar.append(dic_val_num[var])
    #     for var in CatVar1:
    #         CatVar.append(dic_val_num[var])
    #
    #     iv_path = '/home/heyang/data/IV/IVResult/'
    #     features_con_woe = [list(df.uid)]
    #     for var in ConVar:
    #         data = pd.read_csv(iv_path + var + '.csv')
    #         Cutpoint = list(data.Cutpoint)
    #         Cutpoint = Cutpoint[0:len(Cutpoint) - 2]
    #         Cutpoint = list(set([float(x.split(' ')[1]) for x in Cutpoint]))
    #         Cutpoint = [-100000] + Cutpoint
    #         Cutpoint.append(1000000)
    #         Cutpoint = sorted(Cutpoint)
    #         WoE = list(data.WoE)
    #         varvalues_new = []
    #         varvalues_old = list(df[dic_num_val[var]])
    #         for val in varvalues_old:
    #             if val == val:
    #                 for i in range(len(Cutpoint) - 1):
    #                     if val > Cutpoint[i] and val <= Cutpoint[i + 1]:
    #                         varvalues_new.append(WoE[i])
    #                         break
    #                     else:
    #                         continue
    #             else:
    #                 varvalues_new.append(0)
    #         features_con_woe.append(varvalues_new)
    #     features_con_woe = pd.DataFrame(features_con_woe).T
    #     features_con_woe.columns = ['uid'] + ConVar1
    #     for i in ['term_7', 'term_14', 'term_28']:
    #         if i in CatVar1:
    #             CatVar1.remove(i)
    #     features_cat = df[['uid'] + CatVar1]
    #     features_final = pd.merge(features_con_woe[['uid'] + ConVar1], features_cat, how='left', on='uid')
    #     return features_final
    #
    # @classmethod
    # def underSample(self, X, y, minority_ratio=0.5):
    #     minority_label, minority = sorted(y.value_counts().iteritems(), key=lambda x: x[0], reverse=True)[0]
    #     majority_label, majority = sorted(y.value_counts().iteritems(), key=lambda x: x[0], reverse=True)[-1]
    #     minor_index = y[y == minority_label]
    #     major_index = y[y == majority_label]
    #     samples = random.sample(list(major_index.index), int(minority * (1 - minority_ratio) / minority_ratio))
    #     resampled_X = X.loc[samples + list(minor_index.index)]
    #     resampled_y = y.loc[samples + list(minor_index.index)]
    #     return resampled_X, resampled_y
    #
    # @classmethod
    # def fit(self, data, n_round=60, test_size=0.4, feat_chosen_ratio=0.6, penalty='l1', C=5):
    #     lr = LogisticRegression(penalty=penalty, C=C, n_jobs=-1, fit_intercept=False)  #
    #     seed = random.randint(0,10000)
    #     col = data.drop(['label'], axis=1).columns.tolist()
    #     train, val = train_test_split(data, test_size=test_size, random_state=seed)
    #     #     train = pd.DataFrame(preprocessing.scale(train.values),columns = list(train.columns))
    #     aa = np.array([0.0 for i in range(val.shape[0])])
    #     bb = np.array([0.0 for i in range(val.shape[0])])
    #     feature_weight_df = pd.DataFrame(columns=col)
    #     for i in range(n_round):
    #         random_col = random.sample(col, int(feat_chosen_ratio * len(col)))
    #         resampled_X, resampled_y = self.underSample(train[random_col], train.label, minority_ratio=0.5)
    #         lr.fit(resampled_X, resampled_y)
    #
    #         df_tmp = pd.DataFrame(np.array(lr.coef_).reshape((1, -1)), columns=random_col)
    #         feature_weight_df = pd.concat([feature_weight_df, df_tmp])
    #         preds = lr.predict(val[random_col])
    #         tmp = np.array([1.0 if ii >= 0.5 else 0 for ii in preds]) / n_round
    #         tmp1 = np.array(preds) / n_round
    #         aa = aa + np.array(tmp)
    #         bb = bb + np.array(tmp1)
    #     fpr_test, tpr_test, thresholds_test = metrics.roc_curve(val.label, aa)
    #     ks_test = abs(fpr_test - tpr_test).max()
    #     AUC_test = metrics.auc(fpr_test, tpr_test)
    #     print(ks_test, AUC_test)
    #     return ks_test, AUC_test, feature_weight_df
    #
    # @classmethod
    # def get_params(self, data, n_voter=11):
    #     if 'uid' in data.columns:
    #         del data['uid']
    #     data = data.fillna(0)
    #     ks_list = []
    #     auc_list = []
    #     df_list = []
    #     for j in range(n_voter):
    #         aa, bb, cc = self.fit(data)
    #         ks_list.append(aa)
    #         auc_list.append(bb)
    #         df_list.append(cc)
    #     auc_ks = np.array(ks_list) + np.array(auc_list)
    #     for i, ii in zip(auc_ks, df_list):
    #         if i == auc_ks.max():
    #             output = ii
    #             break
    #     return output
    #
    # @classmethod
    # def predict(self, data, params):
    #     params = params.fillna(0)
    #     try:
    #         predict_df = data[['uid']]
    #         for i in params.columns:
    #             a = np.array(data[i]).reshape((-1, 1))
    #             b = np.array(params[i]).reshape((1, -1))
    #             c = np.dot(a, b)
    #             predict_df[i] = [np.mean([jj for jj in j if jj != 0]) for j in c]
    #     except:
    #         print('特征名称不符')
    #         raise
    #     predict_df = predict_df.fillna(0)
    #     predict_df['累加总分'] = sum(predict_df.drop(['uid'], axis=1).values.T)
    #     predict_df['logit总分'] = predict_df['累加总分'].apply(lambda s: round(100.0 / (1.0 + math.exp(-s)), 2))
    #     return predict_df
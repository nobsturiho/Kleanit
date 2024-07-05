# -*- coding: utf-8 -*-
"""
Created on Wed May  1 12:26:23 2024

@author: NobertTurihohabwe
"""

import numpy as np
import pandas as pd
import datetime




def clean(data):
    # ####name_of_borrower to sentence case
    data['name_of_borrower']=data['name_of_borrower'].str.title()
    
    
    
    # ####Line_of_business to sentence case
    data['Line_of_business'] = data['Line_of_business'].str.title()
    
    
    # ####Loan_product_description to sentence case
    data['Loan_product_description'] = data['Loan_product_description'].str.title()
    
    # Insert 'Line_of_business' column next to 'Loan_product_description'
    data.insert(data.columns.get_loc('Loan_product_description')+1, 'Line_of_business', data.pop('Line_of_business'))
    
    
    
    # #### email_of_borrower
    data['email_of_borrower'] = data['email_of_borrower'].fillna('no-email')
    data['email_of_borrower'] = data['email_of_borrower'].str.lower()
    data['email_of_borrower'] = data['email_of_borrower'].str.replace(' ','')
    data['email_of_borrower'] = data.apply(lambda row: 'no-email' if len(str(row['email_of_borrower'])) <= 11 else row['email_of_borrower'], axis=1)
    data['email_of_borrower'] = np.where(data['email_of_borrower'].str.endswith('.com'), data['email_of_borrower'],'no-email')
    
    
    
    # #### highest_education_level
    # Define the characters to remove
    data['highest_education_level']=data['highest_education_level'].astype(str)
    characters_to_remove = ['.', "'", ' ', '-','_']
    
    # Remove the specified characters from each string in the column
    for char in characters_to_remove:
        data['highest_education_level'] = data['highest_education_level'].str.replace(char, '')
    
    educ_keywords = {
        'Not Educated': ['ilit','noschooling','peasant','ill','noformal','never','noeducat','noteducat','noteduacted','noschool',
                         'didnotgo','notqualified','iiiterate','nil','rural','nursary','childhood','none'],
        'Information Not Available': ['nan','notavailable','unclassified','notgiven','0','notprovided','nottracked'
                                      ,'unknown','#value!','#ref!','no'],
        'Primary': ['primary','prima','p1','p2','p3','p4','p5','p6','p7','p8','ple','prmary','rimary','prim','primry'],
        'Secondary': ['alevel','olevel','s1','s2','s3','s4','s5','s6','seconadry','uce','uace','senior',
                      'form1','form2','form3','form4','form5','form6','s,4','secodary','advancedlevel',
                      'ordinarylevel','modirate','secon','advanced'],
        'Tertiary': ['teritary','college','university','degree','diploma','graduate','educated','general education',
                     'certificate','tartia','illletrate','professor','phd','general','guraduate','master',
                     'institution','professionalmanagement','gradaute','bachelors','teaching','nursing','k2',
                     'grade3tr','literate','gradeiv','undergr','grad','techn','tert','12th',
                     'hairdressing','certi','gradev','gradeiii','gradeii','gradethree','sixthgrade']
    }
    
    # Create a new column 'Highest_education_level' and initialize with 'Other'
    data['eductemp'] = 'not_defined'
    
    for index, row in data.iterrows():
        highest_education_level = row['highest_education_level'].lower()
        
        
        # Check for each education level's keywords in the 'Highest_education_level' column
        for educ, keywords in educ_keywords.items():
            for keyword in keywords:
                if keyword in highest_education_level:
                    data.at[index, 'eductemp'] = educ
                    break  # Exit the loop once a highest_education_level is identified for the current row
    
    data.drop(columns = ['highest_education_level'], inplace = True)
    data.rename(columns = {'eductemp':'highest_education_level'}, inplace = True)
    
    # Insert 'highest_education_level' column next to 'email_of_borrower'
    data.insert(data.columns.get_loc('email_of_borrower')+1, 'highest_education_level', data.pop('highest_education_level'))
    
    
    
    # #### employment_status
    data['employment_status'] = 'Self Employed'
    
    
    
    # #### Gender
    data['Gender'] = data['Gender'].str.title()
    data['Gender'] = data['Gender'].str.replace(' ','')
    data['Gender'] = data['Gender'].replace({'F':'Female', 'M':'Male'})
    data['Gender'] = np.where((data['Gender'] == 'Male') | (data['Gender'] == 'Female'), data['Gender'], data['NIN'].str[1])
    data['Gender'] = data['Gender'].replace({'F':'Female', 'M':'Male'})
    
    
    
    # #### Date_of_loan_issue
    data['issuetemp'] = pd.to_numeric(data['Date_of_loan_issue'],errors = 'coerce')
    mask = data['issuetemp'] > 40000
    data.loc[mask, 'Date_of_loan_issue'] = datetime.datetime(1900, 1, 1) + pd.to_timedelta(data.loc[mask, 'issuetemp'] - 2, unit='D')
    data['Date_of_loan_issue'] = pd.to_datetime(data['Date_of_loan_issue'], format='mixed')
    
    
    
    # #### Date_of_birth
    data['Date_of_birth'] = data['Date_of_birth'].replace({'2YRS':'54'})
    mask = (data['Age'].isna())
    data.loc[mask, 'Age'] = data.loc[mask, 'Date_of_birth']
    data['Date_of_birth'] = pd.to_datetime(data['Date_of_birth'], format ='mixed', errors = 'coerce')
    
    
    
    # #### Age
    data['agetemp'] = pd.to_datetime(data['Age'], format = 'mixed', errors = 'coerce')
    data['Age'] = data.apply(lambda row: (row['Date_of_loan_issue'] - row['agetemp']).days//365.25 if len(str(row['Age'])) >= 8 
                             else row['Age'], axis=1)
    
    data['Age'] = pd.to_numeric(data['Age'], errors = 'coerce')
    data['Age'] = np.where((data['Age'] > 18000), ((data['Date_of_loan_issue'].dt.year) - (1900 + data['Age']//365.25)), data['Age'])
    
    maskold = (data['Age'] >80 ) & (data['Age'] < 18000) & (data['NIN'].notna())
    NINdob = pd.to_numeric(data['NIN'].str[2:4], errors = 'coerce')
    data['Age'] = np.where(maskold, data['Date_of_loan_issue'].dt.year - (1900 + NINdob), data['Age'])
    
    mask3 = (((data['Age']<=18)|(data['Age'].isna())) & (NINdob < 20))
    data['Age'] = np.where(mask3, data['Date_of_loan_issue'].dt.year - (2000 + NINdob), data['Age'])
    
    mask4 = (((data['Age']<= 18)|(data['Age'].isna())) & (NINdob > 20))
    data['Age'] = np.where(mask4, data['Date_of_loan_issue'].dt.year - (1900 + NINdob), data['Age'])
    
    
    
    # #### Age_Group
    data["Age_Group"] = np.where(data["Age"] > 35, "Non Youth", "Youth")
    
    #Place the agegroup column next to the Age column
    data.insert(data.columns.get_loc('Age')+1, 'Age_Group', data.pop('Age_Group'))
    
    
    
    # #### Loan_amount
    #Covert Loan amount to Integer
    try:
        data['Loan_amount'] = data['Loan_amount'].str.replace(',','')
    except Exception:
        print('')
        
    data['Loan_amount'] = pd.to_numeric(data['Loan_amount'],errors = 'coerce')
    
    
    
    # #### Date_of_repayments_commencement
    data['repaytemp'] = pd.to_numeric(data['Date_of_repayments_commencement'],errors = 'coerce')
    
    mask = data['repaytemp'] > 40000
    data.loc[mask, 'Date_of_repayments_commencement'] = datetime.datetime(1900, 1, 1) + pd.to_timedelta(data.loc[mask, 'repaytemp'] - 2, unit='D')
    
    data['Date_of_repayments_commencement'] = pd.to_datetime(data['Date_of_repayments_commencement'], format='mixed', errors = 'coerce')
    
    
    
    # #### Interest_rate
    data['Interest_rate'] = data['Interest_rate'].astype(str)
    data['Interest_rate'] = data['Interest_rate'].str.replace('per month','')
    data['Interest_rate'] = data['Interest_rate'].str.replace('%','')
    data['Interest_rate'] = data['Interest_rate'].replace('1.6','16')
    
    data['Interest_red_bal'] = pd.to_numeric(data['Interest_rate'], errors = 'coerce')
    
    for index, row in data.iterrows():
        if row['lender'] == 'ASA Microfinance':
            data.at[index, 'Interest_red_bal'] = row['Interest_red_bal']*12/pd.to_numeric(row['Tenure_of_loan'], errors = 'coerce')
        
        elif row['lender'] == 'Rukiga SACCO' or row['lender'] =='Vision Fund'or row['lender'] =='Butuuro SACCO':
            data.at[index, 'Interest_red_bal'] = row['Interest_red_bal']*0.12
        
        elif row['lender'] == 'EBO SACCO' or row['lender'] =='FINCA Uganda' or row['lender'] =='Hofokam Limited':
            data.at[index, 'Interest_red_bal'] = row['Interest_red_bal']/100
        
        elif row['lender'] == "Letshego Uganda" or row['lender'] =="Kyamuhunga People's SACCO":
            data.at[index, 'Interest_red_bal'] = row['Interest_red_bal']/100
        
        elif row['lender'] == "Mushanga SACCO" or row['lender'] == "Premier Credit" or row['lender'] == "Lyamujungu SACCO":
            data.at[index, 'Interest_red_bal'] = row['Interest_red_bal']/100
            
        elif row['lender'] == 'Finfort': 
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('4.0', '87').replace('5.0', '87').replace('4.5', '87'))/100
        
        elif row['lender'] == 'Flow Uganda':
            data.at[index, 'Interest_red_bal'] = round(round(row['Interest_red_bal']/row['Loan_amount'],3)*365/pd.to_numeric(row['Tenure_of_loan'], errors = 'coerce'),3)
        
        elif row['lender'] == "Nile Microfinance":
            data.at[index, 'Interest_red_bal'] = 0.5
            
        elif row['lender'] == "UGAFODE Microfinance":
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('51.44', '39'))/100
        
        elif row['lender'] == "Pride II" or row['lender'] =='Pride Microfinance Ltd':
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('18.0', '31.5').replace('14.5', '25.5'))/100

        elif row['lender'] == 'KAMRO Capital' and row['Interest_red_bal'] > 100:
            data.at[index, 'Interest_red_bal'] = round(round(row['Interest_red_bal']/row['Loan_amount'],3)*365/pd.to_numeric(row['Tenure_of_loan'], errors = 'coerce'),3)
       
        elif row['lender'] == 'KAMRO Capital' and row['Interest_red_bal'] < 100:
            data.at[index, 'Interest_red_bal'] = round(row['Interest_red_bal']*365/pd.to_numeric(row['Tenure_of_loan'], errors = 'coerce'),3)
        
        elif row['lender'] == 'Development Microfinance':
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('30', '50'))/100
        
        elif row['lender'] == 'Liberation Community F.':
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('2.5', '50').replace('3', '58'))/100
        
        elif row['lender'] == "MAMIDECOT" or row['lender'] == "MAMIDECOT II":
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('18', '32'))/100
        
        elif row['lender'] == "Millennium SACCO 2012":
            data.at[index, 'Interest_red_bal'] = pd.to_numeric(str(row['Interest_red_bal']).replace('21.6', '37.7'))/100
            
        else:
            data.at[index, 'Interest_red_bal'] = row['Interest_red_bal']
    
    # Insert 'Interest_red_bal' column next to 'Interest_rate'
    data.insert(data.columns.get_loc('Interest_rate'), 'Interest_red_bal', data.pop('Interest_red_bal'))
    
    
    
    # #### Tenure_of_loan
    data['Tenure_of_loan'] = data['Tenure_of_loan'].astype(str)
    data['Tenure_of_loan'] = data['Tenure_of_loan'].str.lower()
    data['Tenure_of_loan'] = data['Tenure_of_loan'].replace({'4 quarter(s)':'12'})
    
    characters_to_remove = ['month(s)', "months", 'monthly', 'days','_']
    for char in characters_to_remove:
        data['Tenure_of_loan'] = data['Tenure_of_loan'].str.replace(char, '')
    
    data['Tenure_of_loan'] = pd.to_numeric(data['Tenure_of_loan'], errors = 'coerce')
    
    for index, row in data.iterrows():
        #PFI submits day
        if row['lender'] == 'Lyamujungu SACCO' or row['lender'] == 'Mushanga SACCO'or row['lender'] == 'Development Microfinance'or row['lender'] == 'Millennium SACCO 2012':
            data.at[index, 'Tenure_of_loan'] = round(row['Tenure_of_loan']/30.5,0)
        
        #PFI that submit weeks
        elif row['lender'] == 'Finfort' or row['lender'] =='Pride II' or row['lender'] =='Pride Microfinance Ltd':
            data.at[index, 'Tenure_of_loan'] = row['Tenure_of_loan']/(30/7)
        
        #flow Uganda
        elif row['lender'] == 'Flow Uganda' or row['lender'] == 'KAMRO Capital':
            data.at[index, 'Tenure_of_loan'] = round(row['Tenure_of_loan']/(30), 2)
        
        elif (row['lender'] == 'Hofokam Limited') & (row['Tenure_of_loan'] >36):
            data.at[index, 'Tenure_of_loan'] = round(row['Tenure_of_loan']/30, 2)
        
        elif (row['lender'] == 'Liberation Community F.') & (row['Loan_term_value']=='Weeks'):
            data.at[index, 'Tenure_of_loan'] = round(row['Tenure_of_loan']/4, 2)
    
    
    # #### Loan type
    data['Loan_type'] = data['Loan_type'].str.title()
    
    characters_to_remove = ['Client', "Customer", 'Lending', 'Loan',' ']
    for char in characters_to_remove:
        data['Loan_type'] = data['Loan_type'].str.replace(char, '')
    
    data['Loan_type'] = data['Loan_type'].replace({'Swl':'Individual', 'New':'Individual','Sme':'Individual','Employee':'Individual','Small':'Individual'},regex=True)
    data['Loan_type'] = data['Loan_type'].replace({'Business-Mserf':'Individual','Agriculture-Mserf':'Individual'},regex=True)
    data['Loan_type'] = data['Loan_type'].replace({'I':'Individual','G':'Group','C':'Group','Jlg':'Group'})
    data['Loan_type'] = np.where((data['lender']=='UGAFODE Microfinance') & (data['Loan_product_name'].
                                                                             str[-10:] =='Individual'),'Individual',data['Loan_type']) 
    
    data['Loan_type'] = np.where((data['lender']=='KAMRO Capital'), 'Individual', data['Loan_type'])
    
    data['Loan_type'] = np.where((data['lender']=='UGAFODE Microfinance') & (data['Loan_product_name'].
                                                                             str[-5:] =='Group'),'Group',data['Loan_type']) 
    
    
    
    # #### Loan Term Value
    data['Loan_term_value'] = 'Monthly'
    
    
    
    # #### Loan Purpose
    data['Loan_purpose'] = data['Loan_purpose'].str.title()
    # Insert 'Loan purpose' column next to 'Line of business'
    data.insert(data.columns.get_loc('Line_of_business')+1, 'Loan_purpose', data.pop('Loan_purpose'))
    
    
    
    # #### Loan_cycle
    
    data['Loan_cycle'] = pd.to_numeric(data['Loan_cycle'], errors = 'coerce')
    
    
    # #### Location_of_borrower
    data['Location_of_borrower'] = data['Location_of_borrower'].str.title()
    
    
    # #### Expected_number_of_installments
    data['Expected_number_of_installments'] = data['Expected_number_of_installments'].astype(str)
    data['ENI_temp'] = data['Expected_number_of_installments']
    try:
        data['Expected_number_of_installments'] = data['Expected_number_of_installments'].str.lower()
        data['Expected_number_of_installments'] = data['Expected_number_of_installments'].str.replace("month(s)",'')
    except Exception:
        print('')
        
    data['Expected_number_of_installments'] = data['Expected_number_of_installments'].replace({"4 quarter(s)":'12'})
    data['Expected_number_of_installments'] = data['Expected_number_of_installments'].replace({"months":"","monthly":''},regex=True)
    
    data['Expected_number_of_installments'] = np.where((data['lender']=='ASA Microfinance') & (pd.to_numeric(data['Expected_number_of_installments'],
                    errors ='coerce')>1000),'16', data['Expected_number_of_installments'])
    
    data['Expected_number_of_installments'] = np.where((data['lender']=='Mushanga SACCO') & (pd.to_numeric(data['Expected_number_of_installments'],
                                errors ='coerce')>1000),data['Expected_monthly_installment'], data['Expected_number_of_installments'])

    
    data['Expected_number_of_installments'] = np.where(((data['lender']=='Nile Microfinance') | (data['lender']=='Butuuro SACCO') | (data['lender']=='Vision Fund')) &
                    (pd.to_numeric(data['Expected_number_of_installments'],errors ='coerce')>1000),data['Tenure_of_loan'], data['Expected_number_of_installments'])
    
    data['Expected_number_of_installments'] = round(pd.to_numeric(data['Expected_number_of_installments'], errors = 'coerce'),0).astype('Int64')
    
    
    
    # #### Expected_monthly_installment
    data['Expected_monthly_installment'] = data['Expected_monthly_installment'].astype(str)
    data['Expected_monthly_installment'] = np.where((data['lender']=='Mushanga SACCO') & (pd.to_numeric(data['ENI_temp'], errors ='coerce')>1000), 
                                                    data['ENI_temp'], data['Expected_monthly_installment'])
    
    data['Expected_monthly_installment'] = pd.to_numeric(data['Expected_monthly_installment'].str.replace(',',''), errors = 'coerce')
    
    data['Expected_monthly_installment'] = np.where(data['lender']=='Flow Uganda', data['Loan_amount'] + pd.to_numeric(data['Interest_rate'], 
                                                                                errors = 'coerce'),data['Expected_monthly_installment'])
    data['Expected_monthly_installment'] = np.where(data['Expected_monthly_installment']<100, '', data['Expected_monthly_installment'])
    
    data['Expected_monthly_installment'] = round(pd.to_numeric(data['Expected_monthly_installment'], errors='coerce'),0).astype('Int64')
    
    
    
    # #### Number_of_employees
    data['Number_of_employees'] = data['Number_of_employees'].astype(str)
    try:
        data['Number_of_employees'] = data['Number_of_employees'].str.title()
    except Exception:
        print('')
    
    characters_to_remove = ['   -',' ','Employees','Employee']
    for char in characters_to_remove:
        data['Number_of_employees'] = data['Number_of_employees'].str.replace(char, '')
        
    data['Number_of_employees'] = data['Number_of_employees'].replace({'None':'0','No':'','2-4':'3','5-15':'10',"16-30":'23',
                                        "tAvailable":'',"Notavailable":'',"B":'',"02-Apr":'3',"31-45":'38',"May-15":'',"Tgiven":'',"46-50":'48'},regex=True)
    
    data['Number_of_employees'] = np.where((pd.to_numeric(data['Number_of_employees'], errors='coerce')>100),'', data['Number_of_employees'])
    
    data['Number_of_employees'] = round(pd.to_numeric(data['Number_of_employees'], errors = 'coerce'),0).astype("Int64")
    
    
    
    # #### Rural - Urban
    data['Rural_urban'] = data['Rural_urban'].astype(str)
    data['Rural_urban'] = data['Rural_urban'].str.title()
    data['Rural_urban'] = data['Rural_urban'].replace({'City Centre':'Urban','Wandegeya':'Urban','Nakawa':'Urban',
                                                      'Katwe':'Urban','Bukoto':'Urban'}, regex = True)
    
    characters_to_remove = ['Semi',' ']
    for char in characters_to_remove:
        data['Rural_urban'] = data['Rural_urban'].str.replace(char, '')
    
    data['Rural_urban'] = np.where((data['Rural_urban'] == 'Rural') | (data['Rural_urban'] == 'Urban'), data['Rural_urban'], '')
    
    
    
    # #### Number_of_youth_employees	
    data['Number_of_youth_employees'] = data['Number_of_youth_employees'].astype(str)
    try:
        data['Number_of_youth_employees'] = data['Number_of_youth_employees'].str.title()
    except Exception:
        print('')
    data['Number_of_youth_employees'] = data['Number_of_youth_employees'].replace({"None":'','No':'','    -':'','O':'0'},regex = True)
    data['Number_of_youth_employees'] = data['Number_of_youth_employees'].str.replace(' ','')
    data['Number_of_youth_employees'] = np.where((pd.to_numeric(data['Number_of_youth_employees'], errors='coerce')>100),'', 
                                                 data['Number_of_youth_employees'])
    data['Number_of_youth_employees'] = pd.to_numeric(data['Number_of_youth_employees'], errors = 'coerce').astype("Int64")
    
    
    
    # #### Annual_revenue_of_borrower
    data['Annual_revenue_of_borrower'] = data['Annual_revenue_of_borrower'].astype(str)
    data['Annual_revenue_of_borrower'] = data['Annual_revenue_of_borrower'].str.lower()
    
    data['Annual_revenue_of_borrower'] = data['Annual_revenue_of_borrower'].str.replace(' ','')
    data['Annual_revenue_of_borrower'] = data['Annual_revenue_of_borrower'].replace({"uknown":'',"unknown":''}, regex = True)
    
    data['Annual_revenue_of_borrower'] = round(pd.to_numeric(data['Annual_revenue_of_borrower'], errors = 'coerce'),0)
    data['Annual_revenue_of_borrower'] = np.where((data['Annual_revenue_of_borrower']<0), -data['Annual_revenue_of_borrower'],data['Annual_revenue_of_borrower'])
    data['Annual_revenue_of_borrower'] = np.where((data['Annual_revenue_of_borrower']<10000),'',data['Annual_revenue_of_borrower'])
    
    data['Annual_revenue_of_borrower'] = round(pd.to_numeric(data['Annual_revenue_of_borrower'], errors = 'coerce'),0).astype('Int64')
    
    
    
    
    # #### Length of Time running
    data['Length_of_time_running'] = data['Length_of_time_running'].astype(str)
    data['Length_of_time_running'] = data['Length_of_time_running'].str.lower()
    data['Length_of_time_running'] = data['Length_of_time_running'].str.split('y', expand=True)[0]
    
    # Clean Lyamujungu & Mushanga that submit dates
    data['time_runtemp'] = pd.to_datetime(data["Length_of_time_running"], format='mixed', errors='coerce')
    data["Length_of_time_running"] = np.where((data['time_runtemp'].isna()), data["Length_of_time_running"],
                                                        (data["Date_of_loan_issue"] - data['time_runtemp']).dt.days // 365.25)
    
    #Replace
    data['Length_of_time_running'] = data['Length_of_time_running'].replace({'not available':'','1/2 months':'1','1 - 3':'2',
                                        '4 - 5':'4.5', 'less than':'','6 - 10':'8','more than':'','5months':'1',' ':'','3months':'0',"16weeks":'',"10months":'1',
                                            "8months":'1',"2months":'0',"9month":'1',"2month":'0',"5month":'',"6&half":'6',"2half":'2',"nil":'0',"6ears":'6',
                                                "15mths":'1', "11mth":'1',"1&1/2":'2',"none":'0',"3mon":'0', "1month":'0'},regex =True)
    
    data['Length_of_time_running'] = data['Length_of_time_running'].replace({"i":'',"6months":'1',"1s":'',"2months":'0',"4months":'0',"10s":'1'})
    
    #Clean Vision Fund - They submit months
    data['Length_of_time_running'] = np.where((data['lender'] == 'Vision Fund'), pd.to_numeric(data["Length_of_time_running"], 
                                                                        errors='coerce')//12, data['Length_of_time_running'])
    
    data['Length_of_time_running'] = np.where(((pd.to_numeric(data["Length_of_time_running"], errors = 'coerce')<0) | (pd.to_numeric(data["Length_of_time_running"], errors = 'coerce')>1000)), '', 
                                                                        data['Length_of_time_running'])
    #Convert to numeric
    data['Length_of_time_running'] = (pd.to_numeric(data['Length_of_time_running'], errors = 'coerce').round(0)).astype("Int64")
    
    
    
    
    # #### Person_with_disabilities
    data['Person_with_disabilities'] = data['Person_with_disabilities'].astype(str)
    data['Person_with_disabilities'] = data['Person_with_disabilities'].str.title()
    data['Person_with_disabilities'] = data['Person_with_disabilities'].str.replace(' ','') 
    data['Person_with_disabilities'] = data['Person_with_disabilities'].replace({'False':'No', 'True':'Yes', 'N':'No', '0':'',
                                                                'Y':'Yes','N0':'No','None':'','1':'','Nil':''}).fillna('')
    
    
    
    # #### Number_of_employees_that_are_refugees
    data['Number_of_employees_that_are_refugees'] = data['Number_of_employees_that_are_refugees'].astype(str)
    data['Number_of_employees_that_are_refugees'] = data['Number_of_employees_that_are_refugees'].str.title()
    data['Number_of_employees_that_are_refugees'] = data['Number_of_employees_that_are_refugees'].str.replace(' ','')
    data['Number_of_employees_that_are_refugees'] = data['Number_of_employees_that_are_refugees'].replace({'No':'0',"None":'0',"Non":'0',
                                                                                                          "Nil":'0'})
    data['Number_of_employees_that_are_refugees'] = round(pd.to_numeric(data['Number_of_employees_that_are_refugees'], errors = 'coerce'),0).astype("Int64")
    
    
    
    # #### Number_of_female_employees
    data['Number_of_female_employees'] = data['Number_of_female_employees'].astype(str)
    data['Number_of_female_employees'] = data['Number_of_female_employees'].str.title() 
    data['Number_of_female_employees'] = data['Number_of_female_employees'].replace({'None':'0','     -':'',"No":'0',"Nil":'0',"Yes":''},
                                                                                    regex = True)
    data['Number_of_female_employees'] = data['Number_of_female_employees'].str.replace(' ','')
    data['Number_of_female_employees'] = np.where((pd.to_numeric(data['Number_of_female_employees'], errors='coerce')>100),'', data['Number_of_female_employees'])
    data['Number_of_female_employees'] = round(pd.to_numeric(data['Number_of_female_employees'], errors = 'coerce'),0).astype('Int64')
    
    
    
    # #### Previously_unemployed
    data['Previously_unemployed'] = data['Previously_unemployed'].astype(str)
    data['Previously_unemployed'] = data['Previously_unemployed'].str.title()
    data['Previously_unemployed'] = data['Previously_unemployed'].replace({'None':'0','N0':'','Yes':'',"True":'',"False":'',"Ne":'',
                                                                    "No":'',"Y":'',"2 Employees":'2',"N":'','n':''}, regex = True)
    
    data['Previously_unemployed'] = data['Previously_unemployed'].str.replace(' ','')
    data['Previously_unemployed'] = np.where((pd.to_numeric(data['Previously_unemployed'], errors='coerce')>100),'', data['Previously_unemployed'])
    
    data['Previously_unemployed'] = round(pd.to_numeric(data['Previously_unemployed'], errors = 'coerce'),0).astype('Int64')
    
    
    
    # #### Number_of_employees_with_disabilities
    data['Number_of_employees_with_disabilities'] = data['Number_of_employees_with_disabilities'].astype(str)	
    data['Number_of_employees_with_disabilities'] = data['Number_of_employees_with_disabilities'].str.lower()
    data['Number_of_employees_with_disabilities'] = data['Number_of_employees_with_disabilities'].replace({'none':'0','     -':'',
                                                                                "no":'0',"nil":'0',"yes":''},regex = True)
    data['Number_of_employees_with_disabilities'] = data['Number_of_employees_with_disabilities'].str.replace(' ','')
    
    data['Number_of_employees_with_disabilities'] = round(pd.to_numeric(data['Number_of_employees_with_disabilities'], errors = 'coerce'),0).astype('Int64')
    
    
    
    # #### Loan_cycle_fund_specific
    data['Loan_cycle_fund_specific']  = data['Loan_cycle_fund_specific'].astype(str)
    data['Loan_cycle_fund_specific'] = data['Loan_cycle_fund_specific'].str.title()
    data['Loan_cycle_fund_specific'] = data['Loan_cycle_fund_specific'].replace({'N':'',"Fsd Uganda":''})
    data['Loan_cycle_fund_specific'] = (pd.to_numeric(data['Loan_cycle_fund_specific'], errors = 'coerce').round(0)).astype('Int64')
    
    
    
    # #### Sectors
    sector_keywords = {
        'wholesale & retail business':['working capital'],
        'real Estate': ['rent'],
        'Food & Beverage': ['bakery','confection','fast food','restaurant','baker','cook','bar','disco','beverage'],
        'Other': ['other other','commuinty and social services3','social and other services','commuinty and social services','nan',
                  'purchase of assets','otherworking','otherother','otherportfolio','restructuring of facility','memebership organisations',
                 'rehabilitation','green leaf','proprietrural','computer purchase','proprietservices','purchasemachinery/equipmen','rural mix',
                 'water tank','other activities','other services','other reasons'],
        
        'services':['service'],
        'health': ['pharmac'],
        'financial services': ['financ'],
        
        'Wholesale & Retail Business': ['trade trade','merchandise','stall','cottage industry','trading','retail','boutique','wholesale',
                'hawk','business','sell''shop', 'agribusiness','buying stock','cloth selling','water selling',
                'textile','super market','supply of produce','clothes','stationeries shop','trade and commerc','motocycle spare',
                'proprietaryservice','butchery','raw materialsbss','spare parts','general supplies','book shop','general commerce',
                'tradeworking','whole sale','trade and commerce','proprietary trade','tradeother','trad&com','propriet trade',
                'garments','cosmetics','tradeportfolio','trade 3','timber & wood sales','proprietarytrade','propriettrade',
                                        'trade trade','trade','hardware'],
        
        'Financial Services': ['banking', 'investment','mobile money','mobilemoney','consumer lending','personal loans and household','banks','saccos'],
        
        'Services': ['weldding','welding','saloon','salon','laundry','mechanic','tailor','print','weaving','proprietary services','phone and fax',
                    'baby care','garages','internet caf','events management','beauty parlour','propriet services','clearing and forwarding',
                    'electricians','marketing and advertisement','import consumer','telecommunications','photography','electricity,lighting',
                    'plumber','house cleaning','decorations'],
        
        'Health': ['health', 'medical', 'diagnos','drug screening','drug shop'],
        'Agriculture & Agro processing': ['agriculture','crops', 'maize','rice', 'agro products','animal', 'farm', 'rearing',
                'vegetable', 'fish','poultry','coffee','beef','cattle','banana','livestock','agro input','maize','paultry',
                'sugar cane','diary','fattening','irish','legume','fertilizer','crop products','agri fruits','piggery','seedlings',
                'eggsworking','bee keeping','fertilizer','insecticide','agro produce','agroproduce','agri processing',
                'raw materialsagr','agriculttrade','crop production','beans','cassava','grinding mill','millet milling machine',
                'maize processing','fruit selling','grain selling','meat shop','agri equipment','agricult','matooke','laying hens',
                'pesticides/chem.fertilize','battle leaf','grocery','oil mill','live stock','other goat','mushroom cultivation',
                                        'tomatoes','tea production','add in produce','irrigation','goat restocking','produce'],
        
        'Technology': ['technology', 'software'],

        'Manufacturing': ['manufactur','factory','productionproduction','production production','proprietarts & crafts', 'handicraft',
                          'engineering workshop','furniture making','bamboo and cane work','jute work','wood products and furniture',
                          'arts & crafts','leather workshop','non-metal and metal produ'],
        
        'Education & Skills': ['educat','school','tuition','train','nurserynursery'],
        
        'Tourism & Hospitality': ['hotel','tour','recreational cultural','guest house'],
        
        'Energy': ['coal','energy','petrolium & gas'],
        
        'Real Estate': ['construct', 'estate','house renovation','house completion','carpentry','house improveme','home improve',
                        'building and working','purchaseland','completing housebusines','renovating house','land purchase',
                        'building inspection','completing house','constraction','housing development','land acquisition','brick laying'],
        
        'Transport': ['transport','boda','motorcycle','van/matatu','auto richshaw'],
        
        'Mining': ['mining','mineral','quarry'],
        # Add more sectors and their associated keywords as needed
    }
        
        
    data['sectortemp'] = data['Line_of_business']+data['Loan_purpose']+data['Loan_product_description']
    
    data['sectortemp']=data['sectortemp'].astype(str)
    
    # Create a new column 'sector' and initialize with 'Other'
    data['Sector'] = 'not_defined'
    
    # Iterate over each row in the DataFrame
    for index, row in data.iterrows():
        line_of_business = row['sectortemp'].lower()
        
        # Check for each sector's keywords in the 'line_of_business' column
        for sector, keywords in sector_keywords.items():
            for keyword in keywords:
                if keyword in line_of_business:
                    data.at[index, 'Sector'] = sector
                    break  # Exit the loop once a sector is identified for the current row
    
                    
    
    # Insert 'Sector' column next to 'Loan purpose'
    data.insert(data.columns.get_loc('Loan_purpose')+1, 'Sector', data.pop('Sector'))
    #title case    
    data['Sector'] = data['Sector'].str.title()
    
    
    # #### Districts
    district_keywords = {
        'luwero':['sempa'],
        'mbarara': ['rwizi'],
        'wakiso': ['zana'],
        'Lwengo': ['lwengo','mbirizi','kyamuyunga','bukyanagandi','kapochi','katuulo','kyasenya','mweru','kanku','lubaale b',
                  'nakyenyi','lubanda','kitawuluzi','buyingo','misenyi'],
        'Kalungu': ['kalungu','lukaya','kibisi','bugonzi','mulo','kyamulibwa','bukulula',' lusango','kiweesa'],
        'Kyenjojo': ['kyenjojo','kasiina','kihura','kaija','mabale'],
        'Kazo': ['kazo', 'magondo', 'rwemikoma', 'kyabahura','Kyenshebashebe','ntambazi','kyabahura','bijengye'],
        'Kaberamaido': ['kaberamaido','kaberimaido','olobo'],
        'Kyankwanzi': ['kyankwanzi','muziranduru','byerima a','kigambanankwale','lwanjale b','guwe','byerima','kiryamusunku',
                      'bulamula'],
        'Bulambuli': ['bulambuli','buyaga'],
        'Gulu': ['gulu','bwonagweno','agwee cel','vanguard','tegwana','obiya east','pece lukung','techo','unyama b','lukodi','kanyagoga',
                'gowans','obalwat','te got','layibi','iriaga','agwee','aloyajong','paromo','oguru','patuda'],
        'Lamwo': ['limu'],
        'Kyegegwa': ['kyegegwa','kyeggegwa','kigambo','baranywa','nyabwingiri','kaingani','kidogodo','kako'],
        'Luweero': ['luwero','luweero','wobulenzi','kiwogozi','musaale','nakikoota','nakabiito','kalongo miti','kabakedi',
                    'bukambagga','ttimba','bombo','+0.705010,+32534343','ssenyomo','bowa','wakatayi','kagogo','buzibweera',
                    'ndibulungi','kibanyi','mabuye','nkiga','lumu','bunyaaka','lusenke','mawu-nsavu','kasana ',' binyonyi','kasaala'],
        
        'Lira': ['lira','te-dam cel','senior quarters','ojwina','kakoge','oweera a','awita village','atego a','woromite','tekulu',
                'starch f','ireda central','central park','ayere cell','obanga pe','obutwelo'],
        'Serere': ['serere','amese','ochorai','kamurojo','kakus','apapai'],
        'Tororo': ['tororo','amoni','asinge ward','kalait','molo','kirewa','pombelo','nabuyoga','adumai','pajwenda','iyolwa',
                  'malaba','katandi','pabone','angorom','opule'],
        'Kole': ['kole'],
        'Kumi': ['kumi','munyal','agule'],
        'Apac': ['apac'],
        'Maracha': ['maracha','komendaku','obooa','ondukani','angazi'],
        'Omoro': ['omoro'],
        'Amuru':['amuru','pukure'],
        'Zombo': ['zombo', 'paidha','warr','alangi','zeu','omua'],
        'Arua': ['arua','teremo','lobuju','nsymbia','nunu','oli health centre','pokea','enjeva','logiri','oluodri','komite',
                'muni','ombavu','kijoro kubo','polota','ediofe','ociba','azind','ocodri','ombau','ewuata','ambala','mvara','adraka',
                'adrua','eroko','chongolan','odrani village','ekaligo','odivu','manibe','pamuro','awindiri','buluku','oyooze',
                'komendaku','olevu','elefe','onzivu'],
        'Masaka': ['masaka','nyendo','kiyujja','buchulo','mpugwe','kiyimbwe','sserinya','kyantale','kimanya','kisaaka','bwala',
                  'kirinda','buyinja','bukunda','kabonera','mirundu',' nakayiba',' soweto'],
        'Abim': ['abim'],
        'Moyo': ['moyo','lefori','palorinya','palujo','oraa','onyire','pageribe','vura madulu'],
        'Kamwenge': ['kamwenge', 'kyabandara','bwizi t c','kamwen','biguli','nkoma','kicheche','bwitankanja','kyahalimu','rwempikye',
                    'kaliza','kabambiro',' bunoga',"bwizi  t"],
        'Mukono': ['mukono','seeta','kalagi','kyampisi','ngandu','nyenje','namawojjolo','namilyango','goma, +0.400000','kigunga',
                  'kibaati','ham mukasa','kasala','nakisunga','nangwa','katoogo','lwazi lc1','nakasagazi','mbiiko','mpata','namakomo',
                   'lutengo','kasokoso','namayiba','ntawo','kyetume','lusera','kakukuulu','kimenyedde','nakifuma','kasawo'],
        'Mpigi': ['mpigi','buwama','buyala,','kayabwe','katende','katiiti','kataba','jjanya','wassozi','busese','ssango a',
                  'bujuuko','kwaba','ndugu','mbazzi','mbizinya','lwera','kawansenyi'],
        'Mbarara': ['mbarara', 'kinoni t/c', 'kitunguru', 'ruhunga','rubaya', 'bwizibwera', 'kakoba', 'rwebishekye','kyandahi','kakoma', 
                    'rwanyamahembe', 'kakoba', 'rwentondo', 'rubingo','rukiro', 'kashari', 'rwentojo', 'nyarubungo','bukiro',
                    'katyazo', 'rutooma', 'ngango','kagongi', 'nkaaka', 'rugarama','katete','nyamitanga', 'mwizi','rwampara',
                    'omukagyera,','mirongo','Kashare', 'omukagyera','kamushoko', 'bubaare','kyantamba','rwanyampazi','kamukuzi',
                   'kashaka','kobwoba','igorora t/c','ntuura','kashenyi','nyabisirira','rubindi','byanamira','nchune','kariro',
                    'rwebikoona','mitoozo','bunenero','nyantungu','hospital zone','makenke','biharwe','rwemigina','katojo','nyabugando',
                   'kahingo','kyatamba','mwengura','kaiba','rwobuyenje','nyanja','kakyerere','kakiika','buteraniro','rugando',
                   'rugarura','karwensanga','nombe','nyamiriro','mugarutsya'],
        
        'Wakiso': ['wakiso', 'kyaliwajjala', 'nansana', 'entebbe', 'abayita', 'kireka', 'matuga','kyengera','kasangati','bweyogerere',
                  'gayaza','nakawuka','bunono','masajja b','namagooma','bulamago','bukasa','kisimu','nangabo','kasanje','katooke',
                  'kiwafu','kalambi','busiro','bwebaja','0.139684, 32.563611','nakedde','namugongo','namayumba','kakiri','buddo','bunamwaya',
                  'ssumbwe','matugga','busaabala','manyangwa','nsangi','lyamutundwe','mpala abaita','kawanda','buloba','kiwenda',
                  '+0.212189,+32.615876','+0.424610,+32.559016','0.475201, 32.598245','0.199356, 32.545538','nsanvu','kijjudde','sempya c',
                  'lukwanga','zimuddi','najjemba','kyegobo','kikubapanga','kakunyu','kisimbiri','kikubampanga','naggalabi','serinyabbi',
                  'nabbingo','namulanda','ddewe','najjera','masooli','wattuba lc1','kabanyoro','gobero','magigye','namyumba',
                   'mwererwe','kikokiro','lunyo','bbaka','kiira','masajja','ttaba kamunye','namagola','buzzi','kasngati','nabweru',
                  'ndejje','kajjansi','kanaala','kiryamuli','kigoma','abaita ababiri','maganjo b','lutette','kawuku'],
        
        'Kampala': ['kampala', 'mpala','ben kiwanuka', 'nateete', 'katwe','city centre','kawempe','kabalagala','nakulabye','nakawa',
                    'entebbe road','kalerwe','bulenga','kansanga','wandegeya', 'ntinda', 'acacia', 'bukoto', 'najjanankumbi',
                    'makindye','najja','kitintale','kibuli','kasubi','central ward','nsambya','bwaise','kisaasi','kira town council',
                   'mutungo','masanafu','kanyanya','madrisa','lunguja','kitende','lungujja','muyenga','mulago','luzira','luthuli',
                   'kisasi','bulabira','kabuusu','namirembe','kavule','kibuye','nakasero','kifumbira','kyambogo','gogonya',
                    'salaama','nakinyuguzi','kyebando','kitante','kirombe','kabakanjagala','rubaga'],
        
        'Kiruhura': ['kiruhura', 'kasaana', 'kinoni', 'rushere', 'kyabagyenyi','shwerenkye','kayonza', 'kikatsi',
                     'kihwa','kiguma','burunga','rwanyangwe','nyakashashara','ekikoni','kyenshama','kagando','kashongi','nkungu',
                    'obwengara','rwempiri','kyampangara','kijuma','nshwere empango','kenshunga','akajumbura','bugarihe'],
        
        'Ibanda': ['ibanda', 'katongore','bihanga', 'rwetweka','mushunga','ishongororo', 'kikyenkye','nyakigando','nyarukiika',
                   'kagongo','bwengure','kabaare','kashangura','kyeikucu','kabura','nyabuhikye','igorora','keihangara','nyaburama',
                  'kanyarugiri','kyabarende','kayenje','rwemereire','ryakatumba','katafari','mashuri'],
        
        'Bushenyi': ['ishaka', 'bushenyi', 'kijumo','kabare','kakanju', 'nyamirembe','nkanga','nyabubare','bwekingo','kibaare',
                    '-0.547617+30.173673','nyakabirizi','kyabugimbi','kiyagaara','kyanyamutungu','kibutamo','kyeizooba','bushen'],
        
        'Isingiro': ['isingiro', 'bushozi','Kabaare','ngarama','rwembogo','kabuyanda','kigaragara','rwentuha','humura'],
        
        
        'Kibingo': ['buringo', 'masheruka','bwayegamba','karera','kyangyenyi','kibingo'],
        'Sheema': ['sheema','kabwohe', 'rwanama','mashojwa','rushoroza','rushogashoga','kigarama','rwanyinakihaire','katanoga',
                   'kagango','rweibaare','rweigaga'],
        'Ntungamo': ['ntungamo','ntugam','kyaruhanga','rubaare','katomi','dembe','nyaruhaga'],
        'Rukiga': ['rukiga', 'nyakambu','rwenyangye','kamwezi','kawawu'],
        'Rukungiri': ['rukungiri','kihihi','rwampuga','mabanga','kanyanyegayegye','-0.853340 +30.017587','bikulungu','kitengyento'],
        'Iganga': ['iganga','namufuma','bulubandi','busembatia','0.840531, 33.498'],
        'Amuria':['amuria','ococai','omoratok'],
        'Buikwe': ['buikwe','lugazi','nkokonjeru',', njeru','0.472706, 33.157','makonge','wabaale','nkokohjeru','bugoba','namalili'],
        'Bugiri': ['bugiri'],
        'Soroti': ['soroti','gweri acuma','nakatunya ward','okuku','oderai','samuk','opiyai','orwadai'],
        'Kagadi':['kagadi','0.907898, 30.883805','mabaale','kihingana'],
        'Kabale': ['kabale', 'nyakashebeya','katungu','bubare tc','kable','kengoma'],
        'Kayunga': ['kayunga','+0.630971,+32994','bukolooto','bukujju','wantete a','nabagali','kiteredde','ntenjeru'],
        'Mbale': ['mbale','magale','nakaloke','bumbobi','busiu','busano','bukonde','malukhu b','kitwe'],
        'Pader': ['pader'],
        'Kamuli': ['kamuli','namwendwa','0.955676, 33.130','buliji','namunyagwe'],
        'Namayingo': ['namayingo'],
        'Koboko': ['koboko'],
        'Mityana': ['mityana','busunju','kitongo','nakanyenya','kakindu','mbaliga','kikandwa','kannyagoga','kiryokya','mpiriggwa',
                   'kyesengeze','kawanga','nakitolo','mpirigwa','zigoti','gginzi','lukugga','kiry0kya','bukumula','busimbi'],
        'Hoima': ['hoima','kiryatete','kigaaga','mukabara','kabaale','kigorobya','kitabona','kasingo','kiryawanga','kijwenge','kiryamboga','kanenankumba',
                 'lusaka upper'],
        'Nakasongola': ['nakasongola','kakooge','rwabyata','kalungi','kiweewa','wabitosi'],
        'Kasese': ['kasese', 'bwera','kakogha','rukoki','kogere','kinyabisiki'],
        'Masindi': ['masindi','bukooba','kikwanana'],
        'Buhweju': ['buhweju','kabegaramire'],
        'Butambala': ['butambala','kalamba','kankeesa','lwangiri'],
        'Rakai': ['rakai','kasensero','mitukula','kiruuli','kabaseke','kiyooza','lwentulege',' baloole',' kyango'],
        'Sembabule': ['sembabule', 'sembambule','ssmbabule','kikondeka','katoma','lwembogo'],
        'Rubanda': ['rubanda'],
        'Gomba': ['gomba','kanoni','maddu','6097, centr','kindimunda','kabulasoke'],
        'Bundibugyo': ['bundibugyo'],
        'Kiryandongo': ['kiryandongo', 'bweyale','karuma'],
        'Nwoya': ['pawatomero','owak cell','paja a','coorom','tenam'],
        'Oyam': ['oyam','kamdini','alyec','alati a','atapara corner','adag fitina','bar ilakat','teduka cell','dam apiny','opatoyere',
                'abang imalo','abako east','acamolaki','apurkec','akatakata','agengi cell','ocampar'],
        'Mitooma': ['mitooma', 'bitereko','nyakatooma','kashenshero'],
        'Rubirizi': ['rubirizi','kichwamba'],
        'Lyantonde': ['lyantonde','kyemamba','lyatonde'],
        'Bukwo': ['bukwo','bukwa'],
        'Busia': ['busia','namungodi','masafu','busiko','0.45245, 34.0883'],
        'Mubende': ['mubende','kasambya','kyakatebe','ntuuma','kiyuni','kasenyi caltex','kyawooga','road, +0.4983','kisekende','nakduduma',
                   'kabamba','mugobwa b','kibyamirizi','kisoolo','lwabagabo','bakule','kyengeza a'],
        'Kitagwenda': ['kitagwenda','kitagwe'],
        'Mayuge': ['mayuge','musita'],
        'Sironko': ['sironko','budadiri','londa east'],
        'Kibaale': ['kibale', 'kibaale','kabalungi','rubazi','muziizi','kiryanjagi','kirume','kisiita','bigodi','kikwaya','nturagi'],
        'Bukomansimbi': ['bukomansimbi','ndebwe','kisagazi','butenga b','kigungumika'],
        'Budaka': ['budaka'],
        'Fort Portal':['fort port','rwimi'],
        'Bunyangabu': ['bunyangabu','bunyangabo'],
        'Pallisa': ['pallisa'],
        'Manafwa': ['manafwa','bubulo','buwekanda'],
        'Kakumiro': ['kakumiro','igayaza','kamugaba','kyerimira'],
        'Kitgum': ['kitgum'],
        'Kanungu': ['kanung'],
        'Kiboga': ['kiboga','kikooba','kiganzi cell','kikajjo east','masodde','kajjere','namunyuka','bukomero','busaasa','temanakali',
                  'bamusuuta','maggi village','kitangaala','kambugu'],
        'Kapchorwa': ['kapchorwa'],
        'Kween':['kween'],
        'Kaliro': ['kaliro','kalilo'],
        'Dokolo': ['dokolo','bobol'],
        'Nebbi': ['nebbi'],
        'Alebtong':['alebtong','okoto','olanoamuk'],
        'Kibuku':['kibuku'],
        'Kyotera': ['kyotera','buwenge','mutukula','kakuto','kalisizo','kiwumulo','kabira'],
        'Jinja': ['jinja','bugembe','kyamagwa','budondo,','karongo','mpumudde','butembe','magamaga','kakira','mafubila','namaganga'],
        'Kabarole': ['kabarole','kitesweka','rwenkuba','buhesi','buhesesi','nyamirima','kabonero','kasekero','kyanga','kabagara',
                     'kyeganywa','rweitano','iruhura','kiboota','nyabweya'],
        'Luuka':['luuka'],
        'Kisoro':['kisoro','muhanga'],
        'Buvuma': ['buvuma'],
        'Madi Okollo': ['madi okollo'],
        'Kikuube': ['kikuube'],
        'Katakwi':['katakwii','katakwi','oleroi','guyaguya'],
        'Ngora': ['ngora','ariet'],
        'Nakaseke': ['nakaseke','kiwaguzi b','lumpewe','kivumu','bujuubya','magoma','butikwa','butiikwa','kiwoko','zigula'],
        'Kasanda': ['kasanda'],
        'Obongi':['obongi'],
        'Yumbe': ['yumbe','awoba','yangani','tuliki','ataboo','otche'],
        'Moroto': ['moroto'],
        'Bukedea': ['bukedea','kwarikwari'],
        'Namisindwa': ['namisindwa'],
        'Butaleja': ['butaleja','buwesa','nakwiga','hisoho','dumba a'],
        'Butebo': ['butebo'],
        'Bugweri': ['bugweri'],
        'Otuke': ['otuke','barlwala'],
        'Napak': ['napak'],
        'Amolatar': ['amolatar','amolata'],
        'Buyende': ['buyende'],
        'Bududa': ['bududa'],
        'Pakwach': ['pakwach'],
        'Amudat': ['amudat'],
        'Adjumani': ['adjumani','minia west'],
        'Terego': ['terego','yinga'],
        'Kassanda': ['kassanda'],
        'Kwania': ['kwania','aduku'],
        'Namutumba': ['namutumba','namutumba','magada','kisiiro'],
        'Agago': ['kalongo','caweng'],
        'Buliisa': ['kinyala'],
        'Nakapiripirit': ['nakapiripirit'],
        'Ntoroko': ['ntoroko']
        # Add more districts and their associated keywords as needed
    
    }
    
    
    # Create a new column 'district' and initialize with 'Other'
    data['District'] = 'Not_Available'
    data['Location_of_borrower'] = data['Location_of_borrower'].astype(str)
    
    # Iterate over each row in the DataFrame
    for index, row in data.iterrows():
        location = row['Location_of_borrower'].lower()
        
        # Check for each sector's keywords in the 'location' column
        for district, keywords in district_keywords.items():
            for keyword in keywords:
                if keyword in location:
                    data.at[index, 'District'] = district
                    break  # Exit the loop once a sector is identified for the current row
    
    # Insert 'District' column next to 'Location of borrower'
    data.insert(data.columns.get_loc('Location_of_borrower')+1, 'District', data.pop('District'))
    #title case    
    data['District'] = data['District'].str.title()
    
    
    # #### Regions
    region_keywords = {
        'Western': ['hoima','masindi','kyenjojo','kyegegwa','kibaale','kikuube','kitagwenda','kamwenge','kasese','bundibugyo',
                   'kagadi','fort portal','kiryandongo','kabarole','bunyangabu','buliisa','ntoroko'],
        'West Nile': ['arua','madi okollo','zombo','moyo','obongi','yumbe','nebbi','koboko','pakwach','maracha','adjumani','terego'],
        
        'South Western': ['bushenyi', 'mbarara', 'rukungiri', 'ntungamo', 'kanungu', 'kabale', 'kiruhura', 'kisoro', 'mitooma',
                          'isingiro','rubirizi', 'sheema','ibanda','rubanda','rukiga','kazo','buhweju','kibingo'],
        
        'Central': ['kampala','luwero','kyotera','masaka','kayunga','mityana','sembabule','nakasongola','mukono','bukomansimbi',
                    'rakai','wakiso','mpigi','buikwe','gomba','lwengo','mayuge','butambala','lyantonde','mubende','kalungu',
                    'kiboga','butambala','buvuma','nakaseke','kyankwanzi','kasanda','luweero','kassanda'],
        
        'Eastern': ['jinja','iganga','bugiri','soroti','mbale','kamuli','namayingo','sironko','budaka','busia','bukwo',
                    'bulambuli','tororo','serere','pallisa','manafwa','kumi','kapchorwa','kaliro','kibuku','katakwi',"amuria",
                    "bududa",'bukedea','luuka','kaberamaido','ngora','namutumba','kween','namisindwa','butaleja','butebo','bugweri',
                   'buyende'],
        
        'Karamoja': ['moroto','napak','amudat','abim','nakapiripirit'],
        'Northern': ['gulu','lira','nwoya','apac','oyam','kole','kitgum','dokolo','alebtong','otuke','amolatar','pader','amuru',
                     'omoro','kwania','agago','lamwo']
    
        # Add more regions and their associated keywords as needed
    }
    
    # Create a new column 'region' and initialize with 'Other'
    data['Region'] = 'Other'
    
    # Iterate over each row in the DataFrame
    for index, row in data.iterrows():
        location = row['District'].lower()
        
        # Check for each district's keywords in the 'District' column
        for region, district in region_keywords.items():
            for keyword in district:
                if keyword in location:
                    data.at[index, 'Region'] = region
                    break  # Exit the loop once a sector is identified for the current row
    
    data['Region'] = np.where((data['Location_of_borrower']=='Central'), 'Central', data['Region'])
    data['Region'] = np.where((data['Location_of_borrower']=='North'), 'Northern', data['Region'])
    data['Region'] = np.where((data['Location_of_borrower']=='East'), 'Eastern', data['Region'])
    
    data['Region'] = np.where(((data['lender']=='Nile Microfinance') & (data['District']=='Not_Available')), 'West Nile', data['Region'])
    data['Region'] = np.where(((data['lender']=='EBO SACCO') & (data['District']=='Not_Available')), 'South Western', data['Region'])
    data['Region'] = np.where(((data['lender']=="Kyamuhunga People's SACCO") & (data['District']=='Not_Available')), 'South Western', data['Region'])
    
    # Insert 'Region' column next to 'District'
    data.insert(data.columns.get_loc('District')+1, 'Region', data.pop('Region'))
    
    #Rename columns
    data.rename(columns = {'Interest_rate':'Interest_rate(As submitted by PFI)', 'Interest_red_bal':'Annual_Interest_red_bal-Cleaned',
                           'Tenure_of_loan':'Tenure_of_loan(months)'}, inplace = True)
    
    # #### Delete dummy columns
    dummies = ['issuetemp','agetemp','repaytemp','ENI_temp','time_runtemp','sectortemp','created']
    data.drop(columns = dummies, inplace = True)
    
    return data


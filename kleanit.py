# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 15:36:11 2023

@author: Nobert Turihohabwe
"""


#pip install streamlit
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import ALPFI_Data_func as fx
   
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
    
#Add Sidebar to DashBoard
add_sidebar = st.sidebar.selectbox('Category',('Data_Cleaning','Check Data Issues'))

#Data Cleaning
if add_sidebar == 'Data_Cleaning':
    
    st.markdown(
        """
        <div style="padding: 20px; border: 2px solid darkblue; border-radius: 5px;">
            <h2>Project Kleanit (MSE Recovery Fund)</h1>
            <h3>About The Fund</h2>
            <p>
                The Micro and Small Enterprises (MSE) Recovery Fund is a 5-year, USD 22MN (approximately UGX 80 Bn)
                initiative under the Mastercard Foundation Young Africa Works program, established in partnership with
                Financial Sector Deepening (FSD) Uganda to offset the shocks of the COVID-19 pandemic on the economy of
                Uganda through investments in Micro and Small Enterprises, via Tier III and Tier IV financial institutions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    st.subheader('Import file to clean')
    
    #Add file uploader widget
    uploaded_file = st.file_uploader("Choose an excel file", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        # Read the file file into a DataFrame
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        lender = df['lender'].unique()
        
        # Display lenders as a horizontal list
        st.write("The PFIS are:")
        st.write(lender.tolist(), type='list')
        
        # Display the DataFrame
        st.subheader("Preview of the raw data:")
        st.write("The number of loans is: ",df.shape[0])
        st.write("The number of columns is: ",df.shape[1])
        st.write(df.head())
        
        
        #Add Data Cleaning Button
        if st.button("Click to Clean Data"):
            
            #Clean the data
            df = fx.clean(df)
            
    
            #Print the cleaned dataframe
            st.subheader('Preview the Clean Data')
            try:
                st.write('The shape is: ',df.shape)
            except Exception as e:
                print(e)
            try:
                st.write(df.head())
            except Exception as e:
                print(e)
            
            #Export Clean File
            st.subheader('Export Clean File')
            
            # Create an expandable section for additional export options
            with st.expander("Export Clean Data"):
                
                import calendar
                month = df[df['year']==df['year'].max()]['month'].max()
                month = calendar.month_name[int(month)]
                if len(lender) == 1:
                    PFI = lender[0]
                else:
                    PFI="as of"
                
                #Add button to Download Data
                st.download_button(
                    label="Click to Download Clean File",
                    data=df.to_csv(index=False),  # Convert DataFrame to Excel data
                    file_name= f"Clean Data - {PFI} - {month} {df['year'].max()}.csv",  # Set file name
                )
                
            
            #Add Portfolio Monitoring Fields
            st.subheader('Portfolio Monitoring')
            st.write('Impact Measurement')
            
            #Add Columns
            col1, col2, col3 = st.columns(3)
            with col1:
                Loans = df['Loan_ID'].count()
                st.metric('Number of Loans', Loans,0)
            with col2:
                Amount = format(round(df['Loan_amount'].sum()/1000000,3), ',')
                st.metric('Loan Amount (UGX M)', Amount, 0)
            with col3:
                Ticket = format(round(df['Loan_amount'].mean(),0), ',')
                st.metric('Avg Tickets (UGX)', Ticket, 0)
            with col1:
                borrrowers = len(df['Unique_id'].unique())
                st.metric('Number of borrowers', borrrowers,0)
            with col2:
                Gender = pd.DataFrame(df.groupby(by ='Gender').count()['year']).rename(columns = {'year':'Number'})
                Women = (Gender.iloc[0,0]/(Gender['Number'].sum())*100).round(1)
                st.metric('Pct Women Loans (%)', Women, 0)
            with col3:
                Age_Group = pd.DataFrame(df.groupby(by ='Age_Group').count()['year']).rename(columns = {'year':'Number'})
                Youths = (Age_Group.iloc[-1,0]/(Age_Group['Number'].sum())*100).round(1)
                st.metric('Pct Youths Loans (%)', Youths, 0)
            with col1:
                Interest_red = round((df['Annual_Interest_red_bal-Cleaned'].mean())*100,1)
                st.metric('Average Interest Red bal Annual (%)', Interest_red, 0)
            
            with col2:
                Interest = round((pd.to_numeric(df['Interest_rate(As submitted by PFI)'], errors='coerce').mean()),2)
                st.metric('Average Interest (As submitted)', Interest, 0)
            with col3:
                st.write("")
            with col1:
                young_women = len(df[(df['Age_Group'] == "Youth") & (df['Gender'] == "Female")]['Unique_id'].unique())
                st.metric('No of young women', young_women, 0)
    
            with col2:
                pct_women = round((young_women/borrrowers)*100, 2)
                st.metric('Pct of young women (%)', pct_women, 0)
            with col3:
                st.write("")
                
                
            st.subheader('Loan Type')     
            Loan_type = pd.DataFrame(df.groupby('Loan_type')['Loan_amount'].count())
            Loan_type = Loan_type.rename(columns = {"Loan_amount":"Number"})
            Loan_type["Percent (%)"] = (Loan_type["Number"]*100/sum(Loan_type["Number"])).round(2)
            st.write(Loan_type)
            
            
            st.subheader('Number of Women Loans')
            try:
                Gender_df = pd.DataFrame(df.groupby('Gender')['Loan_amount'].count())
                Gender_df = Gender_df.rename(columns = {"Loan_amount":"Number"})
                Gender_df["Percent (%)"] = (Gender_df["Number"]*100/sum(Gender_df["Number"])).round(2)
                st.write(Gender_df)
            except Exception:
                st.write("Error")
                
                
            st.subheader('Number of Youth Loans')
            try:
                Age_Group_df = pd.DataFrame(df.groupby('Age_Group')['Loan_amount'].count())
                Age_Group_df = Age_Group_df.rename(columns = {"Loan_amount":"Number"})
                Age_Group_df["Percent (%)"] = (Age_Group_df["Number"]*100/sum(Age_Group_df["Number"])).round(2)
                st.write(Age_Group_df)
            except Exception:
                st.write("Error")
                
                
            st.subheader('No. of Loans by Economic Sector')
            try:
                Sector_df = pd.DataFrame(df.groupby('Sector')['Loan_amount'].count())
                Sector_df = Sector_df.rename(columns = {"Loan_amount":"Number"})
                Sector_df["Percent (%)"] = (Sector_df["Number"]*100/sum(Sector_df["Number"])).round(2)
                st.write(Sector_df.sort_values('Number', ascending=False))
            except Exception:
                st.write("Error")
            
            
            st.subheader('Number of Loans by Regions Served')
            try:
                Region_df = pd.DataFrame(df.groupby('Region')['Loan_amount'].count())
                Region_df = Region_df.rename(columns = {"Loan_amount":"Number"})
                Region_df["Percent (%)"] = (Region_df["Number"]*100/sum(Region_df["Number"])).round(2)
                st.write(Region_df.sort_values('Number', ascending=False))
            except Exception:
                st.write("Error")
            
    
            #Add Columns
            col1, col2, col3 = st.columns(3)
            with col1:
               st.subheader('Revenue of Borrowers')
               try:
                   Annual_Revenue = format(round(df['Annual_revenue_of_borrower'].mean(), 0), ',')
                   st.metric('Average Revenue (UGX)',Annual_Revenue)
               except Exception:
                   st.write("Error")
                
            with col2:
                st.subheader('Number of Employees')
                try:
                    employees = round(df['Number_of_employees'].mean(), 0)
                    st.metric('Average number of employees:', employees)
                except Exception:
                    st.write("Error")
            
            with col3:
                st.subheader('Ticket Size')
                Ticket = format(round(df['Loan_amount'].mean(),0), ',')
                st.metric('Avg Tickets (UGX)', Ticket, 0)
                
            with col1:
                try:
                    Median_Revenue = format(round(df['Annual_revenue_of_borrower'].median(), 0), ',')
                    st.metric('Median Revenue (UGX)',Median_Revenue)
                except Exception:
                    st.write("Error")
               
            with col2:
                try:
                    median_employees = round(df['Number_of_employees'].mean(), 0)
                    st.metric('Median number of employees:', median_employees)
                except Exception:
                    st.write("Error")
                
            with col3:
                median_Ticket = format(round(df['Loan_amount'].median(),0), ',')
                st.metric('Median Tickets (UGX)', median_Ticket, 0)
            
            with col1:
                try:
                    mode_Revenue = format(round(df['Annual_revenue_of_borrower'].mode()[0], 0), ',')
                    st.metric('Mode Revenue (UGX)',mode_Revenue)
                except Exception:
                    st.write("Error")
               
            with col2:
                try:
                    mode_employees = round(df['Number_of_employees'].mode()[0], 0)
                    st.metric('Mode number of employees:', mode_employees)
                except Exception:
                    st.write("Error")
                    
            with col3:
                try:
                    mode_Ticket = format(round(df['Loan_amount'].mode()[0], 0), ',')
                    st.metric('Mode Tickets (UGX)', mode_Ticket, 0)
                except Exception:
                    st.write("Error")
    
    
    
            st.subheader('Regional Analytics')
            grouped_data = df.groupby('Region').agg({'id': 'count',
                                                        'Gender': lambda x: (x == 'Female').sum(),
                                                    'Age_Group': lambda x: (x == 'Youth').sum(),
                                                       'Loan_amount': ['mean', 'sum']})
    
            # Rename the columns
            grouped_data.columns = 'Number of loans', 'No. of women loans', 'No. of youths loans','Average Ticket Size (UGX 000)','Total Amount Disbursed (UGX M)'
            
            # Reset the index to make 'Region' a column
            grouped_data.reset_index(inplace=True)
            grouped_data['Average Ticket Size (UGX 000)'] = round(grouped_data['Average Ticket Size (UGX 000)']/1000,3)
            grouped_data['Total Amount Disbursed (UGX M)'] = round(grouped_data['Total Amount Disbursed (UGX M)']/1000000,2)
            
            grouped_data['Pct women (%)'] = round((grouped_data['No. of women loans']/grouped_data['Number of loans'])*100,2)
            grouped_data.insert(grouped_data.columns.get_loc('No. of women loans')+1, 'Pct women (%)', grouped_data.pop('Pct women (%)'))
            
            grouped_data['Pct youths (%)'] = round((grouped_data['No. of youths loans']/grouped_data['Number of loans'])*100,2)
            grouped_data.insert(grouped_data.columns.get_loc('No. of youths loans')+1, 'Pct youths (%)', grouped_data.pop('Pct youths (%)'))
            grouped_data = grouped_data.sort_values('Number of loans', ascending=False)
            
            # Display the resulting DataFrame
            st.write(grouped_data)
            
            
            st.subheader('Number of Loans by District')
            districts = pd.DataFrame(df.groupby(['District'])['id'].count())
            districts.rename(columns={'id': 'Number of loans'}, inplace=True)
            districts = districts.sort_values('Number of loans', ascending=False)
            st.write(districts)
            
            
            
            
#Check data issues
if add_sidebar == 'Check Data Issues':
        

    st.subheader('Import file to Analyse')
    
    #Add file uploader widget
    uploaded_file2 = st.file_uploader("Choose a file", type=["xlsx", "csv"])
    
    if uploaded_file2 is not None:
        # Read the file file into a DataFrame
        if uploaded_file2.type == 'text/csv':
            df = pd.read_csv(uploaded_file2)
        else:
            df = pd.read_excel(uploaded_file2)

        df = pd.read_csv('Disbursement-2024-09-06.csv')
        
        st.subheader('Check for loans that do not belong to the month of submission')
        df['Date_of_loan_issue'] = pd.to_datetime(df['Date_of_loan_issue'], format="mixed", errors = "coerce")
        diffmonths = df[df['Date_of_loan_issue'].dt.month != df['month']]
        st.write(diffmonths)
        
        
        st.subheader('Check for repeated loans')
        df['nin-loan'] = df['NIN']+df['Loan_ID']
        df['countnin-loan'] = df['nin-loan'].map(df['nin-loan'].value_counts())
        repeated = df[(df['countnin-loan']!= 1) & (df['NIN'].notna())].sort_values('NIN')
        st.write(repeated)
        
        
        st.header('NINs')
        st.subheader('Borrowers with NINs of less than 14 characters or greater than 14')
        dfnin1 = df[(df['NIN'].str.replace(' ','').str.len() < 14) | (df['NIN'].str.replace(' ','').str.len() > 14)]
        print(dfnin1.shape)
        st.write(dfnin1)
        
        st.subheader('Borrowers with no NINs')
        nonin = df[(df['NIN'].isna())]
        st.write(nonin)
        
        
        st.subheader('Borrowers with NINs that do not start with CF or CM or PM or PF')
        Ninchar = (df["NIN"].str.upper()).str.replace(' ','').str[0:2]
        dfnin2 = df[(Ninchar != "CM") & (Ninchar != "CF") & (Ninchar != "PF") & (Ninchar != "PM")]
        print(dfnin2.shape)
        st.write(dfnin2)
        
        
        st.subheader('Combined Dataframe of all NIN issues')
        combined_df = pd.concat([dfnin1, dfnin2, nonin])
        combined_df = combined_df.drop_duplicates()
        st.write(combined_df)
        
        
        st.subheader('NINs that do not correspond to Gender')
        dfnin3 = df[((df["NIN"].str.upper()).str.replace(' ','').str[1:2] != (df["Gender"].str.upper()).str.replace(' ','').str[0:1]) & 
                   ((df["NIN"].str.upper().str.replace(' ','').str[1:2] =="F")| (df["NIN"].str.upper().str.replace(' ','').str[1:2]=="M"))]
        st.write(dfnin3)
        
        
        st.header('Phone Numbers')
        st.subheader('Phone numbers less than 9 characters')
        phone = df[(df["Phone_number"].astype(str).str.len()<9) | (df['Phone_number'].isna())]
        st.write(phone)
        
        
        st.header('Borrower Names')
        st.subheader('Loans with no borrower Name')
        noname = df[(df['name_of_borrower'].isna()) | (df['name_of_borrower'].str.len()<4)]
        st.write(noname)
        
        
        st.subheader('Loans with same names but Different NINs - check to ensure its different borrowers')
        df['name_of_borrowertemp'] = df['name_of_borrower'].str.replace(' ','')
        df['NINtemp'] = df['NIN'].str.replace(' ','')
        
        df['countnames'] = df['name_of_borrowertemp'].map(df['name_of_borrowertemp'].value_counts())
        df['name-nin'] = df['NINtemp'] + df['name_of_borrowertemp']
        df['countname-nin'] = df['name-nin'].map(df['name-nin'].value_counts())
        dfnamenin = df[(df['countnames'] != df['countname-nin']) & df['NIN'].notna() & df['name_of_borrower'].notna()]
        dfnames1 = dfnamenin.sort_values('name_of_borrower')
        st.write(dfnames1)
        
        
        st.subheader('Loans with same NINs but Different borrower names')
        df['countnin'] = df['NINtemp'].map(df['NINtemp'].value_counts())
        dfrepnin = df[(df['countnin'] != df['countname-nin']) & df['NIN'].notna() & df['name_of_borrower'].notna()]
        dfnames2 = dfrepnin.sort_values('NIN')
        st.write(dfnames2)
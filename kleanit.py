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
                PFI = lender
            else:
                PFI="as of"
            
            #Add button to Download Data
            st.download_button(
                label="Click to Download Clean File",
                data=df.to_csv(index=False),  # Convert DataFrame to Excel data
                file_name= f"Clean Data {PFI} - {month} {df['year'].max()} - MSE RF.csv",  # Set file name
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
            Interest = round((df['Annual_Interest_red_bal-Cleaned'].mean())*100,1)
            st.metric('Average Interest (%)', Interest, 0)
        with col2:
            Gender = pd.DataFrame(df.groupby(by ='Gender').count()['year']).rename(columns = {'year':'Number'})
            Women = (Gender.iloc[0,0]/(Gender['Number'].sum())*100).round(1)
            st.metric('Pct Women (%)', Women, 0)
        with col3:
            Age_Group = pd.DataFrame(df.groupby(by ='Age_Group').count()['year']).rename(columns = {'year':'Number'})
            Youths = (Age_Group.iloc[-1,0]/(Age_Group['Number'].sum())*100).round(1)
            st.metric('Pct Youths (%)', Youths, 0)
            
            
        st.subheader('Loan Type')     
        Loan_type = pd.DataFrame(df.groupby('Loan_type')['Loan_amount'].count())
        Loan_type = Loan_type.rename(columns = {"Loan_amount":"Number"})
        Loan_type["Percent (%)"] = (Loan_type["Number"]*100/sum(Loan_type["Number"])).round(2)
        st.write(Loan_type)
        
        
        st.subheader('Number of Women Borrowers')
        try:
            Gender_df = pd.DataFrame(df.groupby('Gender')['Loan_amount'].count())
            Gender_df = Gender_df.rename(columns = {"Loan_amount":"Number"})
            Gender_df["Percent (%)"] = (Gender_df["Number"]*100/sum(Gender_df["Number"])).round(2)
            st.write(Gender_df)
        except Exception:
            st.write("Error")
            
            
        st.subheader('Number of Youth Borrowers')
        try:
            Age_Group_df = pd.DataFrame(df.groupby('Age_Group')['Loan_amount'].count())
            Age_Group_df = Age_Group_df.rename(columns = {"Loan_amount":"Number"})
            Age_Group_df["Percent (%)"] = (Age_Group_df["Number"]*100/sum(Age_Group_df["Number"])).round(2)
            st.write(Age_Group_df)
        except Exception:
            st.write("Error")
            
            
        st.subheader('Economic Sectors Served')
        try:
            Sector_df = pd.DataFrame(df.groupby('Sector')['Loan_amount'].count())
            Sector_df = Sector_df.rename(columns = {"Loan_amount":"Number"})
            Sector_df["Percent (%)"] = (Sector_df["Number"]*100/sum(Sector_df["Number"])).round(2)
            st.write(Sector_df.sort_values('Number', ascending=False))
        except Exception:
            st.write("Error")
        
        
        st.subheader('Regions Served')
        try:
            Region_df = pd.DataFrame(df.groupby('Region')['Loan_amount'].count())
            Region_df = Region_df.rename(columns = {"Loan_amount":"Number"})
            Region_df["Percent (%)"] = (Region_df["Number"]*100/sum(Region_df["Number"])).round(2)
            st.write(Region_df.sort_values('Number', ascending=False))
        except Exception:
            st.write("Error")
        
        
        st.subheader('Average Revenue of Borrowers')
        try:
            Annual_Revenue = format(round(df['Annual_revenue_of_borrower'].mean(), 0), ',')
            st.metric('Average Revenue (UGX)',Annual_Revenue)
        except Exception:
            st.write("Error")
        
        
        st.subheader('Average Number of Employees')
        try:
            employees = round(df['Number_of_employees'].mean(), 0)
            st.metric('Average number of employees:', employees)
        except Exception:
            st.write("Error")
         
            
                
        st.subheader('Regional Analytics')
        grouped_data = df.groupby('Region').agg({'id': 'count',
                                                    'Gender': lambda x: (x == 'Female').sum(),
                                                'Age_Group': lambda x: (x == 'Youth').sum(),
                                                   'Loan_amount': ['mean', 'sum']})

        # Rename the columns
        grouped_data.columns = 'Number of loans', 'Number of women', 'Number of youths','Average Ticket Size (UGX 000)','Total Amount Disbursed (UGX M)'
        
        # Reset the index to make 'Region' a column
        grouped_data.reset_index(inplace=True)
        grouped_data['Average Ticket Size (UGX 000)'] = round(grouped_data['Average Ticket Size (UGX 000)']/1000,3)
        grouped_data['Total Amount Disbursed (UGX M)'] = round(grouped_data['Total Amount Disbursed (UGX M)']/1000000,2)
        
        grouped_data['Pct women (%)'] = round((grouped_data['Number of women']/grouped_data['Number of loans'])*100,2)
        grouped_data.insert(grouped_data.columns.get_loc('Number of women')+1, 'Pct women (%)', grouped_data.pop('Pct women (%)'))
        
        grouped_data['Pct youths (%)'] = round((grouped_data['Number of youths']/grouped_data['Number of loans'])*100,2)
        grouped_data.insert(grouped_data.columns.get_loc('Number of youths')+1, 'Pct youths (%)', grouped_data.pop('Pct youths (%)'))
        grouped_data = grouped_data.sort_values('Number of loans', ascending=False)
        
        # Display the resulting DataFrame
        st.write(grouped_data)
        
        
        st.subheader('Districts Served')
        districts = pd.DataFrame(df.groupby(['District'])['id'].count())
        districts.rename(columns={'id': 'Number of loans'}, inplace=True)
        districts = districts.sort_values('Number of loans', ascending=False)
        st.write(districts)
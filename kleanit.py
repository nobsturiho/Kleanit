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
            The Micro and Small Enterprises (MSE) Recovery Fund is a 5-year, USD 20MN (approximately UGX 70 Bn)
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
    st.write("The shape is: ",df.shape)
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
            month = calendar.month_name[int(df['month'].max())]
            #Add button to Download Data
            st.download_button(
                label="Click to Download Clean File",
                data=df.to_csv(index=False),  # Convert DataFrame to Excel data
                file_name= f"Clean_Data_{month}-{df['year'].max()}_Clean_Data.csv",  # Set file name
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
            Interest = round((df['Interest_red_bal'].mean())*100,1)
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
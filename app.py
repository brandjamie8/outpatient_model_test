import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# Function to upload and process CSV file
def upload_data():
   uploaded_file = st.file_uploader("Upload last year's outpatient data", type=['csv'])
   if uploaded_file is not None:
       df = pd.read_csv(uploaded_file)
       st.write("Data Preview:", df.head())
       return df
   return None
# Function to filter data by specialty
def filter_by_specialty(data):
   specialties = data['specialty'].unique()
   selected_specialty = st.sidebar.selectbox("Select Specialty", specialties)
   filtered_data = data[data['specialty'] == selected_specialty]
   st.write(f"### Data for Specialty: {selected_specialty}")
   st.write(filtered_data.head())
   return filtered_data
# Function to predict next year's referrals based on last year's data
def predict_referrals(last_year_data):
   growth_rate = st.slider("Select expected growth rate for referrals (%)", 0, 50, 10)
   last_year_referrals = last_year_data['referrals'].sum()
   next_year_referrals = last_year_referrals * (1 + growth_rate / 100)
   st.write(f"Predicted referrals for next year: {next_year_referrals:.0f}")
   return next_year_referrals, growth_rate
# Function to calculate required appointments to manage expected demand
def calculate_required_appointments(last_year_data, predicted_referrals, growth_rate):
   first_appointments = last_year_data['first_appointments'].sum()
   follow_up_appointments = last_year_data['follow_up_appointments'].sum()
   discharges = last_year_data['discharges'].sum()
   st.write("### Last Year Summary")
   st.write(f"Total First Appointments: {first_appointments}")
   st.write(f"Total Follow-Up Appointments: {follow_up_appointments}")
   st.write(f"Total Discharges: {discharges}")
   # Visualization: Last Year Summary
   summary_data = pd.DataFrame({
       'Category': ['First Appointments', 'Follow-Up Appointments', 'Discharges'],
       'Total': [first_appointments, follow_up_appointments, discharges]
   })
   fig = px.bar(summary_data, x='Category', y='Total', title='Last Year Summary')
   st.plotly_chart(fig)
   st.write("### Next Year Projections")
   desired_waiting_list_reduction = st.number_input("Enter number of patients to reduce the waiting list by", min_value=0, value=100)
   total_appointments_needed = predicted_referrals + desired_waiting_list_reduction
   st.write(f"Total appointments needed to handle new referrals and reduce the backlog: {total_appointments_needed:.0f}")
   # Visualization: Projected Appointments
   projection_data = pd.DataFrame({
       'Category': ['Predicted Referrals', 'Backlog Reduction'],
       'Total': [predicted_referrals, desired_waiting_list_reduction]
   })
   fig = px.bar(projection_data, x='Category', y='Total', title='Next Year Projections')
   st.plotly_chart(fig)
   # Additional table summarizing the percentage change in appointments needed
   summary_table = pd.DataFrame({
       'Metric': ['Predicted Referrals', 'Backlog Reduction', 'Total Appointments Needed'],
       'Total': [predicted_referrals, desired_waiting_list_reduction, total_appointments_needed],
       'Percentage Change': [f"{growth_rate}%", "N/A", f"{(total_appointments_needed / first_appointments - 1) * 100:.2f}%"]
   })
   st.write("### Summary Table")
   st.dataframe(summary_table)
   return total_appointments_needed, summary_table
# Main Streamlit app
def main():
   st.set_page_config(page_title="Outpatient Activity Planning Tool", layout="wide")
   st.title("Outpatient Activity Planning Tool")
   st.sidebar.title("Navigation")
   page = st.sidebar.radio("Select a page", ["Upload & Predict", "Plan Next Year's Activity", "Visualize Data"])
   if page == "Upload & Predict":
       st.header("Upload Last Year's Data and Predict Referrals")
       last_year_data = upload_data()
       if last_year_data is not None and 'specialty' in last_year_data.columns:
           last_year_data = filter_by_specialty(last_year_data)
           st.write("### Predict Next Year's Referrals")
           predicted_referrals, growth_rate = predict_referrals(last_year_data)
   elif page == "Plan Next Year's Activity":
       st.header("Plan Required Outpatient Activity")
       last_year_data = upload_data()
       if last_year_data is not None and 'specialty' in last_year_data.columns:
           last_year_data = filter_by_specialty(last_year_data)
           st.write("### Calculate Required Appointments")
           predicted_referrals, growth_rate = predict_referrals(last_year_data)
           total_appointments_needed, summary_table = calculate_required_appointments(last_year_data, predicted_referrals, growth_rate)
           # Option to download projections as a CSV file
           csv = summary_table.to_csv(index=False).encode('utf-8')
           st.download_button(
               label="Download Projections as CSV",
               data=csv,
               file_name='projections_summary.csv',
               mime='text/csv',
           )
   elif page == "Visualize Data":
       st.header("Visualize Data Insights")
       last_year_data = upload_data()
       if last_year_data is not None and 'specialty' in last_year_data.columns:
           last_year_data = filter_by_specialty(last_year_data)
           st.write("### Data Distributions and Trends")
           # Visualization: Referrals over time
           if 'date' in last_year_data.columns and 'referrals' in last_year_data.columns:
               last_year_data['date'] = pd.to_datetime(last_year_data['date'])
               fig = px.line(last_year_data, x='date', y='referrals', title='Referrals Over Time')
               st.plotly_chart(fig)
           # Visualization: Scatter plot of appointments vs discharges
           if 'first_appointments' in last_year_data.columns and 'discharges' in last_year_data.columns:
               fig = px.scatter(last_year_data, x='first_appointments', y='discharges', title='First Appointments vs. Discharges')
               st.plotly_chart(fig)
           # Analysis for seasonality effects on referrals and appointments
           if 'date' in last_year_data.columns:
               last_year_data['month'] = last_year_data['date'].dt.month
               monthly_summary = last_year_data.groupby('month').agg({'referrals': 'sum', 'first_appointments': 'sum', 'follow_up_appointments': 'sum'}).reset_index()
               fig = px.line(monthly_summary, x='month', y=['referrals', 'first_appointments', 'follow_up_appointments'], title='Seasonality Analysis of Referrals and Appointments')
               st.plotly_chart(fig)
if __name__ == "__main__":
   main()

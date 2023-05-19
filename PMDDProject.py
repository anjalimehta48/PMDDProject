import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
# Create an empty DataFrame to store data
def create_drsp_data():
    drsp_data = pd.DataFrame(
        columns=["record_id", "redcap_event_name", "cycleday", "drsp_spotting_menses", "date_drsp", "value", "drsp_q1", "drsp_q2", "drsp_q3", "drsp_q4", "drsp_q5", "drsp_q6", "drsp_q7", "drsp_q8", "drsp_q9", "drsp_q10", "drsp_q11", "drsp_q12", "drsp_q13", "drsp_q14"]
    )
    drsp_data['date_drsp'] = pd.to_datetime(drsp_data['date_drsp']).dt.date
    return drsp_data


def calculations(drsp_data):
    # Filter for rows with cycleday not equal to NA, 0, or 1
    filtered_data = drsp_data[~drsp_data['cycleday'].isna() & (drsp_data['cycleday'] != 0) & (drsp_data['cycleday'] != 1)]

    # Select the required columns
    columns = ['date_drsp', 'drsp_q1', 'drsp_q2', 'drsp_q3', 'drsp_q4', 'drsp_q5', 'drsp_q6', 'drsp_q7', 'drsp_q8', 'drsp_q9', 'drsp_q10', 'drsp_q11', 'drsp_q12', 'drsp_q13', 'drsp_q14']
    extracted_data = filtered_data[columns]

    # Split the extracted data into two tables for cycle 1 and cycle 2
    cycle1_data = extracted_data.iloc[:14]
    cycle2_data = extracted_data.iloc[-14:]

    # Transpose the tables
    cycle1_data = cycle1_data.set_index('date_drsp').transpose()
    cycle2_data = cycle2_data.set_index('date_drsp').transpose()

    # Split Cycle 1 and Cycle 2 into first 7 columns and last 7 columns for F phase and L phase
    cycleF1_data = cycle1_data.iloc[:, :7]
    cycleL1_data = cycle1_data.iloc[:, -7:]

    cycleF2_data = cycle2_data.iloc[:, :7]
    cycleL2_data = cycle2_data.iloc[:, -7:]
    
    # Calculate sum of F and L phase for cycle 1
    cycleF1_data['F1_sum'] = cycleF1_data.sum(axis=1)
    cycleL1_data['L1_sum'] = cycleL1_data.sum(axis=1)
    
    # Calculate sum of F and L phase for cycle 2
    cycleF2_data['F2_sum'] = cycleF2_data.sum(axis=1)
    cycleL2_data['L2_sum'] = cycleL2_data.sum(axis=1)
    
    # Calculate mean of F and L phase for cycle 1
    cycleF1_data['F1_mean'] = cycleF1_data.mean(axis=1)
    cycleL1_data['L1_mean'] = cycleL1_data.mean(axis=1)
    
    # Calculate mean of F and L phase for cycle 2
    cycleF2_data['F2_mean'] = cycleF2_data.mean(axis=1)
    cycleL2_data['L2_mean'] = cycleL2_data.mean(axis=1)

    # Calculate percent increase for Cycle 1
    percent_increase_cycle1 = ((cycleL1_data['L1_mean'] - cycleF1_data['F1_mean']) / cycleF1_data['F1_mean']) * 100
    
    # Calculate percent increase for Cycle 2
    percent_increase_cycle2 = ((cycleL2_data['L2_mean'] - cycleF2_data['F2_mean']) / cycleF2_data['F2_mean']) * 100

    # Display cycle 1 data
    st.subheader("Cycle 1")
    st.write("Cycle 1 Follicular Phase")
    st.write(cycleF1_data)
    st.write("Cycle 1 Luteal Phase")
    st.write(cycleL1_data)
    st.write("Cycle 1 total DRSP score for the follicular (days 5-11) phase:", cycleF1_data['F1_sum'].sum())
    st.write("Cycle 1 total DRSP score for luteal (days -7 to -1) phase:", cycleL1_data['L1_sum'].sum())
    st.write("Percent Increase for Cycle 1")
    st.write(percent_increase_cycle1)
    

    # Display cycle 2 data
    st.subheader("Cycle 2")
    st.write("Cycle 2 Follicular Phase")
    st.write(cycleF2_data)
    st.write("Cycle 2 Luteal Phase")
    st.write(cycleL2_data)
    st.write("Cycle 2 total DRSP score for the follicular (days 5-11) phase:", cycleF2_data['F2_sum'].sum())
    st.write("Cycle 2 total DRSP score for luteal (days -7 to -1) phase:", cycleL2_data['L2_sum'].sum())
    st.write("Percent Increase for Cycle 2")
    st.write(percent_increase_cycle2)
    
    return cycleF1_data, cycleL1_data, cycleF2_data, cycleL2_data


# Define function for uploading data via CSV
def upload_csv(drsp_data):
    st.header("Upload Dateshift Cycles CSV")
    # Get CSV file from user
    uploaded_file = st.file_uploader("Browse files or drag and drop CSV", type="csv") 

    if uploaded_file is not None:
        # Load CSV into DataFrame
        csv_data = pd.read_csv(uploaded_file)

        # Append CSV data to DRSP data
        drsp_data = drsp_data.append(csv_data, ignore_index=True)
        drsp_data['date_drsp'] = pd.to_datetime(drsp_data['date_drsp']).dt.date
        
        # Display data
        st.write("Table extracted from CSV")
        st.write(drsp_data)
        
        st.header("DRSP Plots")
        q_num = st.slider('Select which question you want to see', 1, 14, 1) #find which question to plot
        date = csv_data["date_drsp"].iloc[10:60]
        col_name = "drsp_q" + str(q_num)#loop q_num from 1 to 14
        drsp = csv_data[col_name].iloc[10:60]


        fig, ax = plt.subplots()
        fig.text(0.6, 0.7, 'Moderate symptoms', style = 'italic',fontsize = 12,color = "red")
        fig.text(0.6, 0.3, 'Mild symptoms', style = 'italic',fontsize = 12,color = "green")
        ax.axhline(y=3, color='r', linestyle='--')# Add a reference line at y=3
        plt.title('Individual participant daily menstrual cycle data')
        plt.plot(date, drsp)
        plt.ylim([0, 6])
        plt.legend(['reference line',col_name])
        plt.xticks(rotation=90)
        plt.xticks(fontsize=6)

        # Plot should bracket or shadow the follicular-green(days 5-11) and luteal-orange(days -7 to -1) phases 
        cycle = csv_data['cycleday'].iloc[10:60]
        for i in range(0,len(cycle)):
            if cycle.iloc[i]!= 'NaN':
                if cycle.iloc[i] in range(5,12):
                    ax.axvspan(i, i+1, alpha=0.3, color='green')
                if cycle.iloc[i] in range(-7,0):
                    ax.axvspan(i, i+1, alpha=0.3, color='orange')
        st.write('Green as follicular part and orange as luteal part')
        st.pyplot(fig)

        # Mood/Physical
        rb_mood_physical = st.radio("Pick you want to see mood or physical data",
         ('Mood(Q1-6)', 'Physical(Q7-11)','Mood+Physical(Q12-14)'))
        # rb_mood_physical = 'Physical(Q7-11)'
        if rb_mood_physical == 'Mood(Q1-6)':
            fig, ax = plt.subplots()
            leg = list()
            date = csv_data["date_drsp"].iloc[10:60]
            for q_num in range(0,5): #question 1-5
                col_name = "drsp_q" + str(q_num+1)#loop q_num from 1 to 14
                drsp = csv_data[col_name].iloc[10:60]
                plt.plot(date, drsp)
                drsp = []
                leg.append(col_name)
            plt.ylim([0, 6])
            plt.legend(leg)
            plt.xticks(rotation=90)
            plt.xticks(fontsize=6)
            st.pyplot(fig)
        if rb_mood_physical == 'Physical(Q7-11)':
            fig, ax = plt.subplots()
            leg = list()
            date = csv_data["date_drsp"].iloc[10:60]
            for q_num in range(6,11): #question 7-11
                col_name = "drsp_q" + str(q_num+1)#loop q_num from 1 to 14
                drsp = csv_data[col_name].iloc[10:60]
                plt.plot(date, drsp)
                drsp = []
                leg.append(col_name)
            plt.ylim([0, 6])
            plt.legend(leg)
            plt.xticks(rotation=90)
            plt.xticks(fontsize=6)
            st.pyplot(fig)
        if rb_mood_physical == 'Mood+Physical(Q12-14)':
            fig, ax = plt.subplots()
            leg = list()
            date = csv_data["date_drsp"].iloc[10:60]
            for q_num in range(11,14): #question 12-14
                col_name = "drsp_q" + str(q_num+1)#loop q_num from 1 to 14
                drsp = csv_data[col_name].iloc[10:60]
                plt.plot(date, drsp)
                drsp = []
                leg.append(col_name)
            plt.ylim([0, 6])
            plt.legend(leg)
            plt.xticks(rotation=90)
            plt.xticks(fontsize=6)
            st.pyplot(fig)
            
        st.header("DRSP Scores and Calculations")
        calculations(drsp_data)
        
        

    return drsp_data

# THE APP
def main():
    # Add title
    st.title("DRSP Cycle Data Plots and Calculations")
    st.caption("This app generates visualizations of symptoms across the menstrual cycle and calculates scores from the DRSP  menstrual symptom rating tool.")
    st.write('Group Project - Liying Zhu, Kiara Mayhand, Anjali Mehta, Nicole Walch')

    
    # Add input field for record_id
    record_id = st.number_input("Enter record ID", min_value=0, step=1)

    # Create or load DRSP data
    if "drsp_data" not in st.session_state:
        st.session_state.drsp_data = create_drsp_data()
    drsp_data = st.session_state.drsp_data

    # Filter data by record_id
    if record_id > 0:
        drsp_data_filtered = drsp_data[drsp_data["record_id"] == record_id]

        # Display data for record_id
        st.write(drsp_data_filtered)

        # Ask user to choose upload method
        drsp_data = upload_csv(drsp_data)
        
        
    else:
        st.write("No record ID has been entered. Type a record ID into the box and press enter to move on to the next screen that allows data entry.")


if __name__ == "__main__":
    main()
    
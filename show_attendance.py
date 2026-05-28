import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get()
        if Subject == "":
            t = 'Please enter the subject name.'
            text_to_speech(t)
            return

        
        filenames = glob(
            f"Attendance\\{Subject}\\*.csv" 
        )
        
        if not filenames:
            t = f"No attendance records found for subject: {Subject}"
            text_to_speech(t)
            print(t)
            return

        all_data = []
        # Path to the StudentDetails file
        student_details_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "StudentDetails", "studentdetails.csv")
        
        for f in filenames:
            base_name = os.path.basename(f)
            parts = base_name.split('_')
            
            # Extract the date part (e.g., '2025-11-04')
            date_str = None
            if len(parts) >= 3:
                date_str = parts[1] # Subject_YYYY-MM-DD_Time.csv
            elif len(parts) >= 2:
                 # Fallback for simpler names like Subject_Date.csv
                 date_str = parts[1].split('.')[0] 

            if not date_str or len(date_str.split('-')) != 3:
                 print(f"Warning: Skipping file '{base_name}' as date format is unreliable.")
                 continue

            try:
                df = pd.read_csv(f)
            except Exception as e:
                print(f"Error reading file {base_name}: {e}")
                continue
            
            if len(df.columns) >= 3:
                attendance_column = df.columns[2]
                
                # CRITICAL FIX: Rename the dynamic attendance column (the timestamp)
                # to just the date string (YYYY-MM-DD).
                df.rename(columns={attendance_column: date_str}, inplace=True)
                
                all_data.append(df)
            else:
                print(f"Warning: Skipping file '{base_name}' as it does not contain enough columns.")
                

        if not all_data:
            t = f"Error: No valid attendance records could be processed for {Subject}."
            text_to_speech(t)
            print(t)
            return

        # 2. Initial Merge of all time-stamped records
        newdf = all_data[0]
        for i in range(1, len(all_data)):
            newdf = newdf.merge(all_data[i], on=['Enrollment', 'Name'], how="outer")
        
        # --- FIX 1: Clean Name Column (Remove brackets/quotes) ---
        if 'Name' in newdf.columns:
            newdf['Name'] = newdf['Name'].astype(str).str.strip("[]'").str.strip('"')

        # 3. Consolidate duplicate date columns (fixes _x, _y errors)
        data_columns = [col for col in newdf.columns if col not in ['Enrollment', 'Name']]
        unique_dates = sorted(list(set([col.split('_')[0] for col in data_columns])))
        
        # 4. FIX 2: Merge Student Details (Fixes missing names)
        if os.path.exists(student_details_path):
            try:
                details_df = pd.read_csv(student_details_path, skip_blank_lines=True, dtype={'Enrollment': str})
                
                if len(details_df.columns) >= 2 and details_df.columns[0] == 'Enrollment' and details_df.columns[1] == 'Name':
                    details_df = details_df[['Enrollment', 'Name']].drop_duplicates(subset=['Enrollment'])
                    
                    newdf['Enrollment'] = newdf['Enrollment'].astype(str)
                    
                    newdf = newdf.drop(columns=['Name'], errors='ignore')
                    
                    newdf = pd.merge(newdf, details_df, on='Enrollment', how='left')
                    
                    newdf['Name'] = newdf['Name'].fillna('')
                
            except Exception as e:
                print(f"CRITICAL ERROR: Failed to read or merge student details. Details: {e}")
        
        # Ensure Enrollment and Name are the first columns
        newdf = newdf[['Enrollment', 'Name'] + [col for col in newdf.columns if col not in ['Enrollment', 'Name']]]
        
        # 5. Consolidate Attendance (1.0 = Present)
        consolidated_data = newdf[['Enrollment', 'Name']].copy()
        
        for date in unique_dates:
            related_columns = [col for col in newdf.columns if col.startswith(date) and col not in ['Enrollment', 'Name']]
            
            # Use max(axis=1) across the related columns: 1.0 (Present) > 0.0 (Absent)
            consolidated_data[date] = newdf[related_columns].max(axis=1).fillna(0.0)

        newdf = consolidated_data
        
        # 6. Final Calculations and Output
        newdf.fillna(0, inplace=True)
        
        date_columns = [col for col in newdf.columns if col not in ['Enrollment', 'Name']]

        newdf.insert(len(newdf.columns), 'Attendance', '0%')

        for i in range(len(newdf)):
            if date_columns:
                attendance_mean = newdf.loc[i, date_columns].mean()
                if not pd.isna(attendance_mean):
                    newdf.loc[i, "Attendance"] = str(int(round(attendance_mean * 100))) + '%'
                else:
                    newdf.loc[i, "Attendance"] = '0%'
            else:
                 newdf.loc[i, "Attendance"] = '0%'

        newdf.to_csv(f"Attendance\\{Subject}\\attendance.csv", index=False)

        # ------------------ Tkinter GUI Display ------------------
        
        root = tkinter.Tk()
        root.title("Attendance of "+Subject)
        root.configure(background="black")
        cs = f"Attendance\\{Subject}\\attendance.csv"
        
        if not os.path.exists(cs):
            t = f"Error: Failed to create aggregate attendance file at {cs}"
            text_to_speech(t)
            print(t)
            return
            
        with open(cs) as file:
            reader = csv.reader(file)
            r = 0

            for col in reader:
                c = 0
                for row in col:
                    label = tkinter.Label(
                        root,
                        width=10,
                        height=1,
                        fg="yellow",
                        font=("times", 15, " bold "),
                        bg="black",
                        text=row,
                        relief=tkinter.RIDGE,
                    )
                    label.grid(row=r, column=c)
                    c += 1
                r += 1
        root.mainloop()

    # ------------------ Subject Chooser GUI ------------------
    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")
    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)
    
    titl = tk.Label(
        subject,
        text="Which Subject of Attendance?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=100, y=12)

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                os.startfile(
                f"Attendance\\{sub}"
                )
            except FileNotFoundError:
                t = f"Attendance folder for subject '{sub}' not found. Please create it first."
                text_to_speech(t)
                print(t)


    attf = tk.Button(
        subject,
        text="Check Sheets",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=10,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    sub = tk.Label(
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub.place(x=50, y=100)

    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_a = tk.Button(
        subject,
        text="View Attendance",
        command=calculate_attendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)
    subject.mainloop()
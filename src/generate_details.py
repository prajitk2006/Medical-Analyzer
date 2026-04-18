import pandas as pd
import json
import random

def generate_details():
    df = pd.read_csv('data/processed/patient_journey_enriched.csv')
    
    # Take a subset of 500 recent patients for the dashboard to be performant
    df['Admission_Date'] = pd.to_datetime(df['Admission_Date'])
    df = df.sort_values(by='Admission_Date', ascending=False).head(500)
    
    departments = df['Department'].unique()
    
    # Generate Staff
    staff_list = []
    staff_id_counter = 1
    
    for dept in departments:
        # Create 3 doctors and 5 nurses per department
        for i in range(3):
            staff_list.append({
                "Staff_ID": f"S{staff_id_counter:03d}",
                "Name": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'])}",
                "Role": "Attending Physician",
                "Department": dept
            })
            staff_id_counter += 1
            
        for i in range(5):
            staff_list.append({
                "Staff_ID": f"S{staff_id_counter:03d}",
                "Name": f"Nurse {random.choice(['Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Wood', 'Lewis'])}",
                "Role": "Registered Nurse",
                "Department": dept
            })
            staff_id_counter += 1
            
    # Map staff by department for assignment
    dept_staff_map = {}
    for staff in staff_list:
        if staff['Department'] not in dept_staff_map:
            dept_staff_map[staff['Department']] = []
        dept_staff_map[staff['Department']].append(staff)
        
    # Medications mapping based on diagnosis
    med_map = {
        'HEART FAILURE': ['Lisinopril', 'Furosemide', 'Metoprolol', 'Spironolactone'],
        'STROKE': ['Alteplase', 'Aspirin', 'Clopidogrel', 'Atorvastatin'],
        'PNEUMONIA': ['Azithromycin', 'Amoxicillin', 'Levofloxacin', 'Ceftriaxone'],
        'FRACTURE': ['Ibuprofen', 'Acetaminophen', 'Oxycodone', 'Morphine'],
        'DIABETES': ['Insulin Glargine', 'Metformin', 'Glipizide', 'Empagliflozin'],
        'ASTHMA': ['Albuterol', 'Budesonide', 'Montelukast', 'Prednisone'],
        'APPENDICITIS': ['Cefoxitin', 'Piperacillin', 'Morphine', 'Ondansetron']
    }
    
    detailed_patients = []
    
    for _, row in df.iterrows():
        dept = row['Department']
        diag = row['Diagnosis']
        
        # Assign 1 Doctor and 1 Nurse
        dept_staff = dept_staff_map.get(dept, [])
        doctors = [s for s in dept_staff if s['Role'] == 'Attending Physician']
        nurses = [s for s in dept_staff if s['Role'] == 'Registered Nurse']
        
        assigned_doc = random.choice(doctors) if doctors else None
        assigned_nurse = random.choice(nurses) if nurses else None
        
        # Assign Medications
        possible_meds = med_map.get(diag, ['Ibuprofen', 'Acetaminophen'])
        patient_meds = random.sample(possible_meds, k=random.randint(1, min(3, len(possible_meds))))
        
        detailed_patients.append({
            "Patient_ID": row['Patient_ID'],
            "Admission_Date": str(row['Admission_Date']),
            "Department": dept,
            "Diagnosis": diag,
            "Wait_Time_Minutes": row['Wait_Time_Minutes'],
            "Length_of_Stay_Days": row['Length_of_Stay_Days'],
            "Readmission_Risk": row['Readmission'],
            "Assigned_Doctor_ID": assigned_doc['Staff_ID'] if assigned_doc else "Unknown",
            "Assigned_Doctor_Name": assigned_doc['Name'] if assigned_doc else "Unknown",
            "Assigned_Nurse_ID": assigned_nurse['Staff_ID'] if assigned_nurse else "Unknown",
            "Assigned_Nurse_Name": assigned_nurse['Name'] if assigned_nurse else "Unknown",
            "Medications": patient_meds
        })
        
    with open('data/processed/staff_details.json', 'w') as f:
        json.dump(staff_list, f, indent=4)
        
    with open('data/processed/detailed_patients.json', 'w') as f:
        json.dump(detailed_patients, f, indent=4)
        
    print("Successfully generated staff_details.json and detailed_patients.json")

if __name__ == "__main__":
    generate_details()

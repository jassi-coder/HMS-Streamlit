import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date, time

# ================= DB CONFIG ==================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "jassi@123"   # 👈 अपना पासवर्ड डालो
DB_NAME = "hospital_db"

# ================= DB SETUP ==================
def get_connection(create_db=False):
    if create_db:
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
    return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)

def init_db():
    conn = get_connection(create_db=True)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.commit()
    cur.close()
    conn.close()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        gender VARCHAR(10),
        contact VARCHAR(15)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        specialization VARCHAR(100),
        contact VARCHAR(15)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        doctor_id INT,
        appt_date DATE,
        appt_time TIME,
        FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
    )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ============== CRUD FUNCTIONS ==============
def add_patient(name, age, gender, contact):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO patients (name,age,gender,contact) VALUES (%s,%s,%s,%s)", (name,age,gender,contact))
    conn.commit()
    conn.close()

def get_patients():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM patients", conn)
    conn.close()
    return df

def add_doctor(name, specialization, contact):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO doctors (name,specialization,contact) VALUES (%s,%s,%s)", (name,specialization,contact))
    conn.commit()
    conn.close()

def get_doctors():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM doctors", conn)
    conn.close()
    return df

def book_appointment(pid, did, appt_date, appt_time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO appointments (patient_id,doctor_id,appt_date,appt_time) VALUES (%s,%s,%s,%s)",
                (pid,did,appt_date,appt_time))
    conn.commit()
    conn.close()

def get_appointments():
    conn = get_connection()
    q = """
    SELECT a.appointment_id, p.name AS patient, d.name AS doctor, d.specialization, a.appt_date, a.appt_time
    FROM appointments a
    JOIN patients p ON a.patient_id=p.patient_id
    JOIN doctors d ON a.doctor_id=d.doctor_id
    ORDER BY a.appt_date DESC
    """
    df = pd.read_sql(q, conn)
    conn.close()
    return df

# ============== STREAMLIT UI =================
def main():
    st.set_page_config(page_title="Hospital Management System", layout="wide")
    st.title("🏥 Hospital Management System")

    init_db()

    menu = ["Dashboard","Patients","Doctors","Appointments"]
    choice = st.sidebar.radio("Menu", menu)

    # Dashboard
    if choice=="Dashboard":
        st.subheader("📊 Dashboard")
        pcount = len(get_patients())
        dcount = len(get_doctors())
        acount = len(get_appointments())
        c1,c2,c3 = st.columns(3)
        c1.metric("Total Patients", pcount)
        c2.metric("Total Doctors", dcount)
        c3.metric("Appointments", acount)

    # Patients
    elif choice=="Patients":
        st.subheader("👨 Patients")
        tab1,tab2 = st.tabs(["Add Patient","View Patients"])
        with tab1:
            with st.form("pform"):
                name = st.text_input("Name")
                age = st.number_input("Age",1,120,25)
                gender = st.selectbox("Gender",["Male","Female","Other"])
                contact = st.text_input("Contact")
                submit = st.form_submit_button("Save")
                if submit:
                    add_patient(name,age,gender,contact)
                    st.success("✅ Patient added")
        with tab2:
            st.dataframe(get_patients(), use_container_width=True)

    # Doctors
    elif choice=="Doctors":
        st.subheader("👨‍⚕️ Doctors")
        tab1,tab2 = st.tabs(["Add Doctor","View Doctors"])
        with tab1:
            with st.form("dform"):
                name = st.text_input("Name")
                specialization = st.text_input("Specialization")
                contact = st.text_input("Contact")
                submit = st.form_submit_button("Save")
                if submit:
                    add_doctor(name,specialization,contact)
                    st.success("✅ Doctor added")
        with tab2:
            st.dataframe(get_doctors(), use_container_width=True)

    # Appointments
    elif choice=="Appointments":
        st.subheader("📅 Appointments")
        tab1,tab2 = st.tabs(["Book Appointment","View Appointments"])
        with tab1:
            patients = get_patients()
            doctors = get_doctors()
            if patients.empty or doctors.empty:
                st.warning("Add patients and doctors first!")
            else:
                with st.form("aform"):
                    pid = st.selectbox("Select Patient", patients.apply(lambda r:f"{r.patient_id}-{r.name}",axis=1))
                    did = st.selectbox("Select Doctor", doctors.apply(lambda r:f"{r.doctor_id}-{r.name}",axis=1))
                    appt_date = st.date_input("Date", value=date.today())
                    appt_time = st.time_input("Time")
                    submit = st.form_submit_button("Book")
                    if submit:
                        pid = int(pid.split("-")[0])
                        did = int(did.split("-")[0])
                        book_appointment(pid,did,appt_date,appt_time)
                        st.success("✅ Appointment booked")
        with tab2:
            st.dataframe(get_appointments(), use_container_width=True)

if __name__=="__main__":
    main()



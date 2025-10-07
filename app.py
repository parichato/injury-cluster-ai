import streamlit as st
import pandas as pd
import joblib

scaler = joblib.load("scaler.pkl")
kmeans = joblib.load("injury_cluster.pkl")

st.title("🚑 ระบบจำแนกกลุ่มผู้บาดเจ็บ")
st.write("กรอกข้อมูล แล้วระบบจะจำแนกกลุ่มผู้บาดเจ็บให้โดยอัตโนมัติ")

age = st.number_input("อายุ (ปี)", 0, 120, 25)
sex = st.selectbox("เพศ", ["ชาย", "หญิง"])
is_night = st.selectbox("ช่วงเวลาเกิดเหตุ", ["กลางวัน", "กลางคืน"])
head_injury = st.selectbox("บาดเจ็บศีรษะหรือไม่", ["ไม่", "ใช่"])
risk1 = st.selectbox("ขับขี่เร็ว/เสี่ยง", ["ไม่", "ใช่"])
cannabis = st.selectbox("ใช้กัญชา", ["ไม่", "ใช่"])
amphetamine = st.selectbox("ใช้ยาบ้า", ["ไม่", "ใช่"])
drugs = st.selectbox("ใช้ยาอื่น ๆ", ["ไม่", "ใช่"])

X_new = pd.DataFrame([{
    "age": age,
    "sex": 1 if sex == "ชาย" else 0,
    "is_night": 1 if is_night == "กลางคืน" else 0,
    "head_injury": 1 if head_injury == "ใช่" else 0,
    "risk1": 1 if risk1 == "ใช่" else 0,
    "risk2": 0, "risk3": 0, "risk4": 0, "risk5": 0,
    "cannabis": 1 if cannabis == "ใช่" else 0,
    "amphetamine": 1 if amphetamine == "ใช่" else 0,
    "drugs": 1 if drugs == "ใช่" else 0
}])

X_scaled = scaler.transform(X_new)
cluster = int(kmeans.predict(X_scaled)[0])

if st.button("จำแนกกลุ่ม"):
    if cluster == 0:
        desc = "กลุ่มความเสี่ยงต่ำ (บาดเจ็บเล็กน้อย)"
    elif cluster == 1:
        desc = "กลุ่มความเสี่ยงปานกลาง (บาดเจ็บทั่วไป)"
    else:
        desc = "กลุ่มความเสี่ยงสูง (ชายอายุน้อย, กลางคืน, มีสารเสพติด)"
    st.success(f"ผลลัพธ์: กลุ่มที่ {cluster} → {desc}")

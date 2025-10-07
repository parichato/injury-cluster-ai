
import streamlit as st
import pandas as pd
import joblib, json

# ===============================
# 🔹 โหลดโมเดลทั้งหมด
# ===============================
cat_model = joblib.load("predict_catboost_multi.pkl")
scaler_pred = joblib.load("predict_scaler_multi.pkl")
kmeans = joblib.load("cluster_kmeans.pkl")
scaler_cluster = joblib.load("cluster_scaler.pkl")
rules = pd.read_csv("association_rules.csv")
metrics = json.load(open("catboost_metrics.json"))

# ===============================
# 🔹 ตั้งค่าเบื้องต้นของหน้าเว็บ
# ===============================
st.set_page_config(page_title="🏥 AI Injury Analysis Dashboard", layout="wide")
st.title("🏥 AI Injury Analysis Dashboard")
st.caption("ระบบวิเคราะห์ผู้บาดเจ็บด้วย AI 3 รูปแบบ: Prediction • Clustering • Association Rules")

# ===============================
# 🔹 Dropdown เลือกโมเดล
# ===============================
model_choice = st.selectbox(
    "เลือกโมเดลที่ต้องการใช้:",
    ["Predict (CatBoost Multi-Class)", "Cluster (K-Means)", "Association Rules"]
)

# ===============================
# 🔹 Sidebar: กรอกข้อมูลผู้บาดเจ็บ
# ===============================
st.sidebar.header("📋 ข้อมูลผู้บาดเจ็บ")

# ข้อมูลพื้นฐาน
age = st.sidebar.number_input("อายุ (ปี)", 0, 100, 25)
sex = st.sidebar.selectbox("เพศ", ["ชาย", "หญิง"])
is_night = st.sidebar.selectbox("ช่วงเวลาเกิดเหตุ", ["กลางวัน", "กลางคืน"])
head_injury = st.sidebar.selectbox("บาดเจ็บศีรษะหรือไม่", ["ไม่", "ใช่"])

# ปัจจัยเสี่ยง (risk1–risk5)
st.sidebar.markdown("### ⚠️ ปัจจัยเสี่ยง")
risk1 = st.sidebar.selectbox("Risk 1: ไม่สวมหมวก/เข็มขัดนิรภัย", ["ไม่", "ใช่"])
risk2 = st.sidebar.selectbox("Risk 2: เมาสุรา", ["ไม่", "ใช่"])
risk3 = st.sidebar.selectbox("Risk 3: ใช้โทรศัพท์/ขับเร็ว", ["ไม่", "ใช่"])
risk4 = st.sidebar.selectbox("Risk 4: ฝ่าฝืนกฎจราจร", ["ไม่", "ใช่"])
risk5 = st.sidebar.selectbox("Risk 5: ยาเสพติด/พฤติกรรมอื่น", ["ไม่", "ใช่"])

# สารเสพติด
st.sidebar.markdown("### 💊 สารเสพติด")
cannabis = st.sidebar.selectbox("ใช้กัญชา", ["ไม่", "ใช่"])
amphetamine = st.sidebar.selectbox("ใช้ยาบ้า", ["ไม่", "ใช่"])
drugs = st.sidebar.selectbox("ใช้ยาอื่น ๆ", ["ไม่", "ใช่"])

# เตรียมข้อมูล input
X_input = pd.DataFrame([{
    "age": age,
    "sex": 1 if sex == "ชาย" else 0,
    "is_night": 1 if is_night == "กลางคืน" else 0,
    "head_injury": 1 if head_injury == "ใช่" else 0,
    "risk1": 1 if risk1 == "ใช่" else 0,
    "risk2": 1 if risk2 == "ใช่" else 0,
    "risk3": 1 if risk3 == "ใช่" else 0,
    "risk4": 1 if risk4 == "ใช่" else 0,
    "risk5": 1 if risk5 == "ใช่" else 0,
    "cannabis": 1 if cannabis == "ใช่" else 0,
    "amphetamine": 1 if amphetamine == "ใช่" else 0,
    "drugs": 1 if drugs == "ใช่" else 0
}])

# ===============================
# 🧠 1. Prediction (CatBoost)
# ===============================
if model_choice == "Predict (CatBoost Multi-Class)":
    st.subheader("🧠 การทำนายระดับความรุนแรง (CatBoost Multi-Class)")
    st.write(f"📊 **Model Performance:** Accuracy: `{metrics['accuracy']}` | Weighted F1: `{metrics['f1_weighted']}` | CV-F1: `{metrics['cv_f1_mean']}`")

    if st.button("🔍 ทำนายระดับความรุนแรง"):
        X_scaled = scaler_pred.transform(X_input)
        pred_class = int(cat_model.predict(X_scaled)[0])

        severity_map = {
            0: ("🟢 บาดเจ็บเล็กน้อย (Minor)", "success"),
            1: ("🟡 บาดเจ็บรุนแรง (Severe)", "warning"),
            2: ("🔴 เสียชีวิต (Fatal)", "error")
        }

        msg, style = severity_map[pred_class]
        st.markdown(f"### ผลการทำนาย: {msg}")

        if style == "success":
            st.success("ความเสี่ยงต่ำ ระบบแนะนำให้เฝ้าระวังทั่วไป 🟢")
        elif style == "warning":
            st.warning("ความเสี่ยงปานกลาง ควรเตรียมการดูแลเพิ่มเติม 🟡")
        else:
            st.error("ความเสี่ยงสูง ควรจัดทีมแพทย์ฉุกเฉินด่วน 🔴")

        st.info("💡 โมเดลนี้ช่วยให้โรงพยาบาลสามารถคัดกรองผู้บาดเจ็บที่มีแนวโน้มรุนแรง \
ได้รวดเร็วขึ้น เพื่อวางแผนทรัพยากรและทีมแพทย์ให้เหมาะสม")

# ===============================
# 📊 2. Clustering (K-Means)
# ===============================
elif model_choice == "Cluster (K-Means)":
    st.subheader("📊 การจำแนกกลุ่มผู้บาดเจ็บ (K-Means Clustering)")

    if st.button("🔍 จำแนกกลุ่ม"):
        X_scaled = scaler_cluster.transform(X_input)
        cluster = int(kmeans.predict(X_scaled)[0])

        cluster_desc = {
            0: ("🟢 กลุ่มความเสี่ยงต่ำ (Low-risk)", "success"),
            1: ("🟡 กลุ่มความเสี่ยงปานกลาง (Moderate-risk)", "warning"),
            2: ("🔴 กลุ่มความเสี่ยงสูง (High-risk)", "error")
        }

        msg, style = cluster_desc[cluster]
        st.markdown(f"### ผลการจัดกลุ่ม: {msg}")

        if style == "success":
            st.success("กลุ่มนี้มีลักษณะผู้บาดเจ็บที่ความรุนแรงต่ำโดยเฉลี่ย 🟢")
        elif style == "warning":
            st.warning("กลุ่มนี้อยู่ในระดับปานกลาง ควรเฝ้าระวัง 🟡")
        else:
            st.error("กลุ่มนี้เป็นกลุ่มความเสี่ยงสูง ต้องให้ความสำคัญมากที่สุด 🔴")

        st.caption("🔎 การจำแนกกลุ่มช่วยให้ผู้บริหารวางแผนทรัพยากรและจัดลำดับความสำคัญของเคสได้อย่างมีประสิทธิภาพ")

# ===============================
# 🔗 3. Association Rules
# ===============================
elif model_choice == "Association Rules":
    st.subheader("🔗 การค้นหาความสัมพันธ์ของปัจจัยเสี่ยง (Apriori Association Rules)")

    min_conf = st.slider("เลือกค่า Confidence ขั้นต่ำ:", 0.5, 1.0, 0.6)
    filtered = rules[rules["confidence"] >= min_conf].sort_values("lift", ascending=False).head(10)

    st.markdown("#### 📋 กฎความสัมพันธ์ที่พบบ่อยที่สุด")
    st.dataframe(filtered[["antecedents","consequents","support","confidence","lift"]])

    if not filtered.empty:
        top_rule = filtered.iloc[0]
        st.info(f"💡 **Insight:** จากข้อมูล พบว่าปัจจัย `{top_rule['antecedents']}` มักสัมพันธ์กับ `{top_rule['consequents']}` \
(Confidence: {round(top_rule['confidence'],2)}, Lift: {round(top_rule['lift'],2)})")
    else:
        st.warning("ไม่พบกฎที่ตรงตามเงื่อนไขที่กำหนด")

    st.caption("กฎเหล่านี้ช่วยให้องค์กรเข้าใจพฤติกรรมเสี่ยงที่มักเกิดร่วมกัน \
เพื่อนำไปออกนโยบายหรือรณรงค์ด้านความปลอดภัย")

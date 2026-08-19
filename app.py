import streamlit as st
import math

st.set_page_config(page_title="سیستم بهینه‌سازی خط اسپیرال", layout="wide")

st.title("⚙️ محاسبه و پیش‌بینی خط تولید لوله اسپیرال")
st.markdown("---")

# ۱. مشخصات پایه پروژه
st.header("۱. مشخصات پایه پروژه")
col1, col2, col3 = st.columns(3)

with col1:
    grade = st.text_input("گرید ورق", value="ST37")
    strip_width = st.number_input("عرض ورق (میلی‌متر)", value=1500.0, step=10.0)

with col2:
    strip_thickness = st.number_input("ضخامت ورق (میلی‌متر)", value=10.0, step=0.5)
    pipe_diameter = st.number_input("سایز / قطر بیرونی لوله (میلی‌متر)", value=1200.0, step=10.0)

with col3:
    pipe_length = st.number_input("طول هر شاخه لوله (میلی‌متر)", value=12000.0, step=100.0)
    min_t_distance = st.number_input("حد مجاز فاصله T تا خط برش (میلی‌متر)", value=500.0, step=50.0)

st.markdown("---")

# ۲. مشخصات کلاف استارت
st.header("۲. مشخصات کلاف جاری (استارت)")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    current_weight = st.number_input("وزن کلاف استارت (کیلوگرم)", value=12000.0, step=100.0)
with col_s2:
    current_end_crop = st.number_input("مقدار برش آخر کلاف (میلی‌متر)", value=300.0, step=10.0)
with col_s3:
    current_t_dist = st.number_input("فاصله T تا برش فعلی (میلی‌متر)", value=4500.0, step=50.0)

st.markdown("---")

# ۳. بانک کلاف‌های پروژه
st.header("۳. بانک کلاف‌های پروژه")
coils_input = st.text_area(
    "وزن کلاف‌های بعدی به کیلوگرم (با کاما یا اینتر جدا کنید):",
    value="12000, 12500, 11800, 12200"
)

# تبدیل متن ورودی کلاف‌ها به لیست اعدادی
try:
    coils_bank = [float(w.strip()) for w in coils_input.replace("\n", ",").split(",") if w.strip()]
except ValueError:
    st.error("لطفاً وزن کلاف‌ها را فقط به صورت عدد وارد کنید.")
    coils_bank = []

# دکمه محاسبه
if st.button("🚀 محاسبه و پردازش پیش‌بینی"):
    
    # فرمول محاسبه طول ورق (میلی‌متر) بر اساس وزن
    def get_strip_length(weight_kg, width, thickness):
        density = 7.85e-6  # kg/mm³
        volume = weight_kg / density
        return volume / (width * thickness)

    # محاسبه زاویه حلزونی
    sin_alpha = strip_width / (math.pi * pipe_diameter)
    alpha = math.asin(sin_alpha)

    # بررسی کلاف استارت
    start_valid = current_t_dist >= min_t_distance and (pipe_length - current_t_dist) >= min_t_distance
    
    st.markdown("### 📊 نتایج پردازش کلاف استارت")
    if start_valid:
        st.success(f"وضعیت کلاف استارت: ✅ مجاز | فاصله T تا برش: {current_t_dist:.1f} mm")
    else:
        st.error(f"وضعیت کلاف استارت: ⚠️ غیرمجاز (تداخل T با برش) | فاصله T تا برش: {current_t_dist:.1f} mm")

    # محاسبه نقطه اثر برای کلاف‌های بعدی
    start_strip_len = get_strip_length(current_weight, strip_width, strip_thickness) - current_end_crop
    start_pipe_len = start_strip_len / math.cos(alpha)
    accumulated_pipe_len = (current_t_dist + start_pipe_len) % pipe_length

    st.markdown("### 📋 پیش‌بینی فاصله T تا برش برای کلاف‌های بعدی")
    
    results = []
    for idx, weight in enumerate(coils_bank, 1):
        coil_strip_len = get_strip_length(weight, strip_width, strip_thickness)
        coil_pipe_len = coil_strip_len / math.cos(alpha)
        
        t_distance = (accumulated_pipe_len + coil_pipe_len) % pipe_length
        
        is_valid = (t_distance >= min_t_distance) and ((pipe_length - t_distance) >= min_t_distance)
        status = "✅ مجاز" if is_valid else "⚠️ غیرمجاز"
        
        results.append({
            "شماره کلاف": f"کلاف {idx:02d}",
            "وزن کلاف (kg)": f"{weight:,.0f}",
            "فاصله T تا برش (mm)": f"{t_distance:,.1f}",
            "وضعیت": status
        })
        
        accumulated_pipe_len = t_distance

    # نمایش جدول نهایی
    st.table(results)

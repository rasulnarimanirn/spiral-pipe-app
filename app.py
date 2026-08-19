import streamlit as st
import math

st.set_page_config(page_title="سیستم بهینه‌سازی خط اسپیرال", layout="wide")
st.title("⚙️ سیستم مدیریت تولید و محاسبات T-Joint لوله اسپیرال")
st.markdown("---")

# حافظه موقت برای ذخیره لیست وزن کلاف‌ها
if "coils_list" not in st.session_state:
    st.session_state.coils_list = []

# ۱. مشخصات پایه پروژه
st.header("۱. مشخصات پایه پروژه")
c1, c2, c3 = st.columns(3)

with c1:
    steel_grades = ["ST37", "ST52", "X42", "X52", "X60", "X65", "X70"]
    selected_grade = st.selectbox("گرید ورق فولادی", steel_grades, index=0)
    strip_width = st.number_input("عرض ورق - W (mm)", value=1500.0, step=10.0)

with c2:
    strip_thickness = st.number_input("ضخامت ورق - t (mm)", value=10.0, step=0.5)
    pipe_diameter = st.number_input("قطر بیرونی لوله - D (mm)", value=1200.0, step=10.0)

with c3:
    pipe_length = st.number_input("طول هر شاخه لوله - L (mm)", value=12020.0, step=10.0)
    min_t_distance = st.number_input("حد مجاز فاصله T تا خط برش (mm)", value=300.0, step=50.0)

# محاسبات اتوماتیک هندسه لوله
mean_diameter = pipe_diameter - strip_thickness
pi_d = math.pi * mean_diameter
sin_alpha = strip_width / pi_d
alpha_rad = math.asin(sin_alpha)
alpha_deg = math.degrees(alpha_rad)
weld_pitch = strip_width / math.cos(alpha_rad)

# نمایش پارامترهای استخراج‌شده
st.markdown("---")
st.header("📐 پارامترهای هندسی استخراج‌شده (خودکار)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("گرید انتخاب‌شده", selected_grade)
m2.metric("قطر متوسط (mm)", f"{mean_diameter:.1f}")
m3.metric("زاویه هلیکس (°)", f"{alpha_deg:.2f}°")
m4.metric("گام جوش - Pitch (mm)", f"{weld_pitch:.1f}")

st.markdown("---")

# ۲. مشخصات کلاف استارت
st.header("۲. مشخصات کلاف جاری (استارت)")
s1, s2, s3 = st.columns(3)
with s1:
    start_weight = st.number_input("وزن کلاف استارت (kg)", value=12000.0, step=100.0)
with s2:
    start_crop = st.number_input("برش آخر کلاف (mm)", value=300.0, step=10.0)
with s3:
    start_t_dist = st.number_input("فاصله آخرین T تا برش فعلی (mm)", value=500.0, step=10.0)

st.markdown("---")

# ۳. بانک کلاف‌های پروژه (ورود، اصلاح و حذف)
st.header("۳. بانک کلاف‌های پروژه")

# فرم افزودن کلاف جدید
col_add1, col_add2 = st.columns([3, 1])

with col_add1:
    new_coil_weight = st.number_input("وزن کلاف جدید (kg):", value=12000.0, step=100.0, key="input_coil_w")

with col_add2:
    st.write("")
    st.write("")
    if st.button("➕ افزودن کلاف"):
        st.session_state.coils_list.append(new_coil_weight)
        st.rerun()

# لیست پویای کلاف‌ها با قابلیت اصلاح و حذف تکی
if len(st.session_state.coils_list) > 0:
    st.subheader("📋 لیست کلاف‌های اضافه شده:")
    
    indices_to_remove = []
    
    for idx, weight in enumerate(st.session_state.coils_list):
        col_num, col_val, col_del = st.columns([1, 4, 1])
        
        with col_num:
            st.markdown(f"### **.{idx + 1}**")
            
        with col_val:
            # امکان اصلاح مستقیم وزن کلاف
            updated_weight = st.number_input(
                label=f"وزن (kg)",
                value=float(weight),
                step=100.0,
                key=f"coil_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.coils_list[idx] = updated_weight
            
        with col_del:
            if st.button("🗑️", key=f"del_{idx}"):
                indices_to_remove.append(idx)

    # حذف مواردی که دکمه سطل زباله آن‌ها زده شده است
    if indices_to_remove:
        for index in reversed(indices_to_remove):
            st.session_state.coils_list.pop(index)
        st.rerun()
        
    st.write("")
    if st.button("❌ پاک‌کردن کل لیست"):
        st.session_state.coils_list = []
        st.rerun()

else:
    st.info("هنوز کلافی اضافه نشده است.")

st.markdown("---")

# ۴. پردازش و محاسبات نهایی
if st.button("🚀 محاسبه و پردازش پیش‌بینی T-Joint"):
    
    # بررسی وضعیت کلاف استارت
    rem_pitch = start_t_dist % weld_pitch
    is_start_safe = (rem_pitch >= min_t_distance) and (rem_pitch <= (weld_pitch - min_t_distance))

    st.markdown("### 📊 وضعیت کلاف جاری (استارت)")
    if is_start_safe:
        st.success(f"✅ وضعیت مجاز | فاصله تا نزدیک‌ترین خط جوش گام: {rem_pitch:.1f} mm")
    else:
        st.error(f"❌ غیرمجاز (تداخل T یا جوش اسپیرال با برش) | فاصله تا خط جوش: {rem_pitch:.1f} mm")

    # بررسی بانک کلاف‌ها
    if len(st.session_state.coils_list) > 0:
        density = 7.85e-6 # kg/mm3
        
        def get_pipe_len_from_weight(w_kg):
            strip_len = w_kg / (density * strip_width * strip_thickness)
            return strip_len / math.cos(alpha_rad)

        start_pipe_len = get_pipe_len_from_weight(start_weight) - (start_crop / math.cos(alpha_rad))
        accumulated_len = start_t_dist + start_pipe_len

        st.markdown("### 📋 پیش‌بینی فاصله T تا برش برای کلاف‌های بعدی")
        
        results = []
        for idx, weight in enumerate(st.session_state.coils_list, 1):
            coil_pipe_len = get_pipe_len_from_weight(weight)
            accumulated_len += coil_pipe_len
            
            dist_to_cut = accumulated_len % pipe_length
            rem_p = dist_to_cut % weld_pitch
            is_safe = (rem_p >= min_t_distance) and (rem_p <= (weld_pitch - min_t_distance))
            
            status = "✅ مجاز" if is_safe else "⚠️ تداخل با برش"
            
            results.append({
                "ردیف": f".{idx}",
                "گرید": selected_grade,
                "وزن (kg)": f"{weight:,.0f}",
                "موقعیت T روی لوله (mm)": f"{dist_to_cut:,.1f}",
                "فاصله تا خط جوش گام (mm)": f"{rem_p:,.1f}",
                "وضعیت": status
            })

        st.table(results)

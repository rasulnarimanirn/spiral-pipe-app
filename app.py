import streamlit as st
import math

# ==========================================
# تنظیمات صفحه
# ==========================================
st.set_page_config(
    page_title="مدیریت تولید لوله اسپیرال",
    layout="wide"
)

st.title("سیستم مدیریت کلاف و محل جوش T-Joint")
st.markdown("---")

# ==========================================
# بخش ۱: مشخصات پایه پروژه
# ==========================================
st.header("۱. مشخصات پایه پروژه")

col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    D_outer = st.number_input("قطر خارجی لوله - D (mm)", value=1800.0, step=1.0)
with col_p2:
    t_wall = st.number_input("ضخامت ورق - t (mm)", value=14.2, step=0.1)
with col_p3:
    W_strip = st.number_input("عرض ورق - W (mm)", value=1500.0, step=1.0)
with col_p4:
    L_branch = st.number_input("طول شاخه استاندارد (mm)", value=12020.0, step=10.0)

# چگالی فولاد (kg/mm^3)
STEEL_DENSITY = 7.85e-6 

# محاسبات هندسی پایه
D_mean = D_outer - t_wall  # قطر متوسط
Perimeter = math.pi * D_mean  # محیط (mm)
sin_alpha = W_strip / Perimeter
alpha_deg = math.degrees(math.asin(sin_alpha))
Pitch = W_strip / math.cos(math.radians(alpha_deg))  # گام جوش (mm)

# نمایش پارامترهای محاسبه شده
st.info(
    f"**پارامترهای هندسی محاسبه شده:** "
    f"قطر متوسط: **{D_mean:.2f} mm** | "
    f"محیط (C): **{Perimeter:.2f} mm ({Perimeter/1000:.3f} m)** | "
    f"زاویه هلیکس (&alpha;): **{alpha_deg:.2f}°** | "
    f"گام جوش (P): **{Pitch:.2f} mm**"
)

st.markdown("---")

# ==========================================
# بخش ۲: کلاف جاری (استارت)
# ==========================================
st.header("۲. مشخصات کلاف استارت و کالیبراسیون T-Joint")

col_c1, col_c2 = st.columns(2)

with col_c1:
    coil_weight_kg = st.number_input("وزن کلاف جاری (kg)", value=23000.0, step=500.0)
    T_actual_mm = st.number_input("فاصله واقعی T تا برش (mm)", value=400.0, step=10.0)

with col_c2:
    st.write("**کنترل برش غیر استاندارد (تست یا فرار از تداخل T):**")
    custom_branch_active = st.checkbox(
        "فعال‌سازی طول غیر استاندارد برای شاخه آخر"
    )
    
    if custom_branch_active:
        L_actual_branch = st.number_input(
            "طول واقعی شاخه برش‌خورده (mm)",
            value=L_branch,
            step=10.0
        )
    else:
        L_actual_branch = L_branch

# محاسبات کلاف جاری
L_strip_total = coil_weight_kg / (W_strip * t_wall * STEEL_DENSITY)
L_pipe_total = L_strip_total * sin_alpha
T_theoretical_mm = L_pipe_total % L_branch

# محاسبات ضایعات
L_loss_pipe_mm = T_theoretical_mm - T_actual_mm
if L_loss_pipe_mm < 0:
    L_loss_pipe_mm += L_branch 

L_loss_pipe_m = L_loss_pipe_mm / 1000.0
Scrap_Area_m2 = L_loss_pipe_m * (Perimeter / 1000.0)
Scrap_Weight_kg = Scrap_Area_m2 * (t_wall / 1000.0) * 7850.0

length_offset_mm = L_actual_branch - L_branch

# نمایش نتایج کلاف جاری
st.subheader("تحلیل کلاف جاری")

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("خروجی کل لوله (نظری)", f"{L_pipe_total / 1000.0:.2f} m")
    st.metric("موقعیت نظری T", f"{T_theoretical_mm:.2f} mm")

with col_r2:
    st.metric("طول لوله ضایعات", f"{L_loss_pipe_m:.2f} m ({L_loss_pipe_mm:.0f} mm)")
    st.metric("مساحت ورق ضایعات", f"{Scrap_Area_m2:.2f} m²")

with col_r3:
    st.metric("وزن ضایعات", f"{Scrap_Weight_kg:.1f} kg")
    st.metric("جبران طول شاخه", f"{length_offset_mm:+.1f} mm")

st.markdown("---")

# ==========================================
# بخش ۳: پیش‌بینی کلاف‌های بانک
# ==========================================
st.header("۳. بانک کلاف‌ها و پیش‌بینی T-Joint بعدی")

st.markdown("وزن کلاف‌های بعدی را وارد کنید تا موقعیت T در شاخه‌های آینده پیش‌بینی شود.")

num_coils = st.number_input("تعداد کلاف‌های بعدی برای پیش‌بینی", min_value=1, max_value=10, value=3)

coil_inputs = []
cols = st.columns(min(num_coils, 4))
for i in range(num_coils):
    with cols[i % 4]:
        w = st.number_input(f"وزن کلاف #{i+2} (kg)", value=23000.0, step=500.0, key=f"coil_{i}")
        coil_inputs.append(w)

current_accumulated_pipe_mm = (L_pipe_total - L_loss_pipe_mm) + length_offset_mm

st.subheader("جدول پیش‌بینی")

prediction_data = []

for idx, w_kg in enumerate(coil_inputs, start=2):
    strip_len = w_kg / (W_strip * t_wall * STEEL_DENSITY)
    pipe_len = strip_len * sin_alpha
    
    current_accumulated_pipe_mm += pipe_len
    
    predicted_T_position_mm = current_accumulated_pipe_mm % L_branch
    branch_number = int(current_accumulated_pipe_mm // L_branch) + 1
    
    prediction_data.append({
        "شماره کلاف": f"کلاف #{idx}",
        "وزن کلاف (kg)": f"{w_kg:,.0f}",
        "خروجی لوله (m)": f"{pipe_len / 1000.0:.2f}",
        "موقعیت T روی شاخه (mm)": f"{predicted_T_position_mm:.2f}",
        "شماره شاخه هدف": f"{branch_number}"
    })

st.table(prediction_data)

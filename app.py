import streamlit as st
import math

# ==========================================
# تنظیمات صفحه
# ==========================================
st.set_page_config(
    page_title="مدیریت تولید لوله اسپیرال",
    layout="wide"
)

st.title("سیستم جامع مدیریت کلاف و محل جوش T-Joint")
st.markdown("---")

# ==========================================
# مدیریت وضعیت بانک کلاف‌ها (Session State)
# ==========================================
if "coils_bank" not in st.session_state:
    st.session_state.coils_bank = [
        {"id": 2, "weight": 23000.0, "used": False},
        {"id": 3, "weight": 23000.0, "used": False},
        {"id": 4, "weight": 23000.0, "used": False}
    ]

# ==========================================
# بخش ۱: مشخصات پایه پروژه و استانداردهای کیفی
# ==========================================
st.header("۱. مشخصات پایه پروژه")

col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    D_outer = st.number_input("قطر خارجی لوله - D (mm)", value=1800.0, step=1.0)
    steel_grade = st.selectbox(
        "گرید بین‌المللی ورق (Steel Grade)",
        options=[
            "API 5L Grade B",
            "API 5L X42",
            "API 5L X52",
            "API 5L X60",
            "API 5L X65",
            "API 5L X70",
            "EN 10208-2 (L245/L290/L360/L415)",
            "DIN 17100 (St 37-2 / St 52-3)",
            "سفارشی / سایر"
        ]
    )

with col_p2:
    t_wall = st.number_input("ضخامت ورق - t (mm)", value=14.2, step=0.1)
    if steel_grade == "سفارشی / سایر":
        steel_density_g_cm3 = st.number_input("چگالی سفارشی (g/cm³)", value=7.85, step=0.01)
    else:
        steel_density_g_cm3 = 7.85

with col_p3:
    W_strip = st.number_input("عرض ورق - W (mm)", value=1500.0, step=1.0)
    T_limit_mm = st.number_input("حد مجاز فاصله T از خط برش (mm)", value=300.0, step=50.0)

with col_p4:
    L_branch = st.number_input("طول شاخه استاندارد (mm)", value=12020.0, step=10.0)

# چگالی فولاد بر حسب kg/mm^3
STEEL_DENSITY = steel_density_g_cm3 * 1e-6 

# محاسبات هندسی پایه
D_mean = D_outer - t_wall  
Perimeter = math.pi * D_mean  
sin_alpha = W_strip / Perimeter
alpha_deg = math.degrees(math.asin(sin_alpha))
Pitch = W_strip / math.cos(math.radians(alpha_deg))  

st.info(
    f"**پارامترهای پایه پروژه:** "
    f"گرید: **{steel_grade}** | "
    f"قطر متوسط: **{D_mean:.2f} mm** | "
    f"محیط (C): **{Perimeter:.2f} mm ({Perimeter/1000:.3f} m)** | "
    f"زاویه هلیکس (&alpha;): **{alpha_deg:.2f}°** | "
    f"گام جوش (P): **{Pitch:.2f} mm** | "
    f"حد مجاز T: **{T_limit_mm:.0f} mm**"
)

st.markdown("---")

# ==========================================
# بخش ۲: مشخصات کلاف استارت (جاری)
# ==========================================
st.header("۲. مشخصات کلاف استارت و کالیبراسیون T-Joint")

col_c1, col_c2 = st.columns(2)

with col_c1:
    coil_weight_kg = st.number_input("وزن کلاف جاری (kg)", value=23000.0, step=500.0)
    T_actual_mm = st.number_input("فاصله واقعی T تا برش روی خط (mm)", value=400.0, step=10.0)
    head_cut_mm = st.number_input("اندازه برش سر کلاف (mm)", value=0.0, step=50.0)

with col_c2:
    tail_cut_mm = st.number_input("اندازه برش ته کلاف (mm)", value=0.0, step=50.0)
    
    st.write("**کنترل برش غیر استاندارد (تست کیفیت یا فرار از تداخل T با تیغه):**")
    custom_branch_active = st.checkbox(
        "فعال‌سازی طول غیر استاندارد برای شاخه آخر کلاف"
    )
    
    if custom_branch_active:
        L_actual_branch = st.number_input(
            "طول واقعی شاخه بریده‌شده (mm)",
            value=L_branch,
            step=10.0
        )
    else:
        L_actual_branch = L_branch

# محاسبات کلاف جاری
L_strip_total = coil_weight_kg / (W_strip * t_wall * STEEL_DENSITY)
L_pipe_total = L_strip_total * sin_alpha
T_theoretical_mm = L_pipe_total % L_branch

# محاسبات ضایعات با احتساب برش سر و ته
L_loss_pipe_mm = (T_theoretical_mm - T_actual_mm) + head_cut_mm + tail_cut_mm
if L_loss_pipe_mm < 0:
    L_loss_pipe_mm += L_branch 

L_loss_pipe_m = L_loss_pipe_mm / 1000.0

# طول ورق ضایعاتی بازشده بر پایه زاویه هلیکس
L_strip_loss_mm = L_loss_pipe_mm / sin_alpha
L_strip_loss_m = L_strip_loss_mm / 1000.0

Scrap_Area_m2 = L_strip_loss_m * (W_strip / 1000.0)
Scrap_Weight_kg = L_strip_loss_mm * W_strip * t_wall * STEEL_DENSITY

length_offset_mm = L_actual_branch - L_branch

is_start_conflict = (T_actual_mm <= T_limit_mm) or (T_actual_mm >= (L_branch - T_limit_mm))
start_status_msg = "⚠️ خطر تداخل T با برش" if is_start_conflict else "✅ وضعیت عادی"

st.subheader("تحلیل کلاف جاری")

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("خروجی کل لوله (نظری)", f"{L_pipe_total / 1000.0:.2f} m")
    st.metric("موقعیت نظری T", f"{T_theoretical_mm:.2f} mm")

with col_r2:
    st.metric("طول کل لوله ضایعات", f"{L_loss_pipe_m:.2f} m ({L_loss_pipe_mm:.0f} mm)")
    st.metric("طول ورق ضایعاتی بازشده", f"{L_strip_loss_m:.2f} m")
    st.metric("مساحت ورق ضایعات", f"{Scrap_Area_m2:.2f} m²")

with col_r3:
    st.metric("وزن خالص ضایعات", f"{Scrap_Weight_kg:.1f} kg")
    st.metric("وضعیت تداخل T", start_status_msg)

st.markdown("---")

# ==========================================
# بخش ۳: بانک کلاف‌ها و پیش‌بینی T-Joint بعدی (دینامیک)
# ==========================================
st.header("۳. بانک کلاف‌ها و پیش‌بینی T-Joint بعدی")

# افزودن کلاف جدید
col_add1, col_add2 = st.columns([3, 1])
with col_add1:
    new_weight = st.number_input("وزن کلاف جدید (kg)", value=23000.0, step=500.0, key="new_coil_weight")
with col_add2:
    st.write(" ")
    st.write(" ")
    if st.button("➕ افزودن کلاف به لیست", use_container_width=True):
        next_id = st.session_state.coils_bank[-1]["id"] + 1 if st.session_state.coils_bank else 2
        st.session_state.coils_bank.append({"id": next_id, "weight": new_weight, "used": False})
        st.rerun()

st.markdown("#### مدیریت و لیست کلاف‌های ثبت‌شده")

# نمایش و مدیریت کلاف‌ها
if not st.session_state.coils_bank:
    st.warning("هیچ کلافی در بانک ثبت نشده است.")
else:
    for idx, coil in enumerate(st.session_state.coils_bank):
        c_col1, c_col2, c_col3, c_col4 = st.columns([1.5, 2.5, 2, 1])
        
        with c_col1:
            st.markdown(f"**کلاف #{coil['id']}**")
        
        with c_col2:
            new_w = st.number_input(
                f"وزن (kg)",
                value=coil["weight"],
                step=500.0,
                key=f"w_{coil['id']}_{idx}"
            )
            st.session_state.coils_bank[idx]["weight"] = new_w
            
        with c_col3:
            is_used = st.checkbox("مصرف‌شده", value=coil["used"], key=f"u_{coil['id']}_{idx}")
            st.session_state.coils_bank[idx]["used"] = is_used
            
        with c_col4:
            if st.button("🗑️ حذف", key=f"del_{coil['id']}_{idx}"):
                st.session_state.coils_bank.pop(idx)
                st.rerun()

# پیش‌بینی T-Joint بر اساس کلاف‌های فعال (مصرف‌نشده)
st.subheader("جدول پیش‌بینی T-Joint (فقط کلاف‌های فعال)")

accumulated_position_mm = T_actual_mm + length_offset_mm
prediction_data = []

active_coils = [c for c in st.session_state.coils_bank if not c["used"]]

if not active_coils:
    st.info("تمام کلاف‌های بانک مصرف شده‌اند یا کلافی وجود ندارد.")
else:
    for coil in active_coils:
        w_kg = coil["weight"]
        strip_len = w_kg / (W_strip * t_wall * STEEL_DENSITY)
        pipe_len = strip_len * sin_alpha
        
        accumulated_position_mm = (accumulated_position_mm + pipe_len) % L_branch
        
        has_conflict = (accumulated_position_mm <= T_limit_mm) or (accumulated_position_mm >= (L_branch - T_limit_mm))
        status_str = "⚠️ خطر تداخل با برش" if has_conflict else "✅ وضعیت عادی"
        
        prediction_data.append({
            "شماره کلاف": f"کلاف #{coil['id']}",
            "وزن کلاف (kg)": f"{w_kg:,.0f}",
            "خروجی لوله (m)": f"{pipe_len / 1000.0:.2f}",
            "موقعیت T روی شاخه (mm)": f"{accumulated_position_mm:.2f}",
            "حد مجاز (mm)": f"{T_limit_mm:.0f}",
            "وضعیت تداخل T با برش": status_str
        })

    st.table(prediction_data)

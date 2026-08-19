import streamlit as st
import math

# تنظیمات اولیه صفحه
st.set_page_config(page_title="مدیریت برش لوله اسپیرال", layout="wide")
st.title("⚙️ سیستم هوشمند بهینه‌سازی برش و T-Joint لوله اسپیرال")

# --- بخش اول: تنظیمات ثابت پروژه (Sidebar) ---
st.sidebar.header("📌 تنظیمات پایه پروژه")

# ۱. انتخاب گرید و چگالی
grades_density = {
    "ST37": 7850,
    "ST52": 7850,
    "X60": 7850,
    "X65": 7850,
    "X70": 7860
}
selected_grade = st.sidebar.selectbox("گرید فولاد:", list(grades_density.keys()))
density = grades_density[selected_grade]

# ۲. مشخصات هندسی لوله و کلاف
st.sidebar.subheader("ابعاد هندسی")
outer_diameter_mm = st.sidebar.number_input("قطر خارجی لوله (mm):", value=1800.0)
thickness_mm = st.sidebar.number_input("ضخامت ورق (mm):", value=4.2)
strip_width_mm = st.sidebar.number_input("عرض ورق (mm):", value=1500.0)

# ۳. استانداردهای برش
st.sidebar.subheader("استانداردهای برش")
min_t_joint_clearance_m = st.sidebar.number_input("حداقل فاصله مجاز T-Joint تا برش (m):", value=0.50, step=0.05)
main_pipe_len = st.sidebar.number_input("طول قالب اصلی (m):", value=12.02)

# --- محاسبات پایه ریاضی ---
# تبدیل واحدها به متر
D = outer_diameter_mm / 1000.0
t = thickness_mm / 1000.0
W = strip_width_mm / 1000.0

# وزن هر متر لوله (کیلوگرم)
weight_per_meter = math.pi * (D - t) * t * density

st.info(f"💡 **اطلاعات محاسبه‌شده سایز جاری:** وزن هر متر لوله = **{weight_per_meter:.2f} kg/m** | گرید: **{selected_grade}**")

# --- بخش دوم: پنل ثبت کلاف‌ها ---
st.header("📋 ثبت کلاف و بازمحاسبه آنلاین")

col1, col2 = st.columns(2)
with col1:
    coil_weight_kg = st.number_input("وزن کلاف جدید (kg):", value=22850.0, step=100.0)
with col2:
    manual_t_joint_pos = st.number_input("موقعیت واقعی/اصلاحی T-Joint تا سر لوله (m) [اختیاری]:", value=0.0, help="در صورت ایجاد ضایعات یا عیب، فاصله فعلی T-Joint تا سر لوله را وارد کنید.")

if st.button("🧮 محاسبه الگوی برش بهینه"):
    # طول کل لوله حاصل از کلاف
    total_pipe_length = coil_weight_kg / weight_per_meter
    
    st.subheader(f"طول کل لوله حاصل از کلاف: **{total_pipe_length:.2f} متر**")
    
    # بررسی اصلاحیه دستی ضایعات
    if manual_t_joint_pos > 0:
        scrap_length = total_pipe_length - manual_t_joint_pos
        scrap_weight = scrap_length * weight_per_meter
        st.warning(f"⚠️ **ضایعات/قطع اصلاحی ثبت شد:** میزان ضایعات = **{scrap_length:.2f} متر** ({scrap_weight:.1f} kg)")
        effective_length = manual_t_joint_pos
    else:
        effective_length = total_pipe_length

    # الگوریتم بررسی T-Joint و پیشنهاد برش
    # تست حالت استاندارد (برش سر کلاف 0.75m)
    std_trim = 0.75
    remaining_len = effective_length - std_trim
    num_main_pipes = int(remaining_len // main_pipe_len)
    last_cut_pos = std_trim + (num_main_pipes * main_pipe_len)
    t_joint_distance = effective_length - last_cut_pos

    st.markdown("---")
    st.subheader("💡 پیشنهاد سیستم برای این کلاف:")

    if t_joint_distance >= min_t_joint_clearance_m:
        st.success(f"✅ **حالت استاندارد ایمن است:**")
        st.write(f"- **برش سر کلاف:** 0.75 متر")
        st.write(f"- **تعداد شاخه‌های ۱۲.۰۲ متری:** {num_main_pipes} عدد")
        st.write(f"- **برش ته کلاف (پرت/اضافه):** {t_joint_distance:.2f} متر")
        st.write(f"- **فاصله T-Joint تا آخرین برش:** **{t_joint_distance:.2f} متر** (بیشتر از حد مجاز {min_t_joint_clearance_m}m)")
    else:
        # اگر فاصله کم بود، اولویت اول: تغییر برش سر کلاف (بین 0.40 تا 1.00)
        needed_shift = min_t_joint_clearance_m - t_joint_distance
        adjusted_trim = std_trim - needed_shift
        
        if 0.40 <= adjusted_trim <= 1.00:
            st.warning(f"⚠️ **اصلاح با تغییر برش سر کلاف (اولویت ۱):**")
            st.write(f"- **برش سر کلاف پیشنهادی:** **{adjusted_trim:.2f} متر** (به جای 0.75m)")
            st.write(f"- **تعداد شاخه‌های ۱۲.۰۲ متری:** {num_main_pipes} عدد")
            st.write(f"- **فاصله جدید T-Joint تا خط برش:** **{min_t_joint_clearance_m:.2f} متر** (ایمن)")
        else:
            st.error(f"🚨 **اصلاح با طول متغیر (اولویت ۲):** تغییر برش سر کلاف به تنهایی کافی نیست.")
            st.write("پیشنهاد: استفاده از یک شاخه ۱۱.۵۵ متری یا ۱۲.۵۲ متری در بین شاخه‌ها.")

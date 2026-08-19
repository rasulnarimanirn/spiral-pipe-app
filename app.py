import streamlit as st
import math

st.set_page_config(page_title="سیستم مدیریت خط تولید لوله اسپیرال", layout="wide")

st.title("⚙️ سیستم هوشمند برنامه‌ریزی کلاف و کنترل T-Joint")
st.subheader("پروژه تولید لوله اسپیرال")

# --- بخش اول: مشخصات فنی پروژه ---
st.sidebar.header("📋 مشخصات فنی پروژه")
pipe_diameter = st.sidebar.number_input("قطر بیرونی لوله (mm)", value=1800.0, step=10.0)
wall_thickness = st.sidebar.number_input("ضخامت ورق (mm)", value=14.2, step=0.1)
strip_width = st.sidebar.number_input("عرض کلاف (mm)", value=1500.0, step=10.0)
target_pipe_length = st.sidebar.number_input("طول استاندارد هر شاخه لوله (m)", value=12.0, step=0.1)
min_safe_t_dist = st.sidebar.number_input("حداقل فاصله ایمن T تا برش (cm)", value=50.0, step=5.0)

# محاسبات اولیه هندسی اسپیرال
# D_m = قطر متوسط
d_mean = pipe_diameter - wall_thickness
# زاویه حلزونی (Helix Angle)
sin_alpha = strip_width / (math.pi * d_mean)
alpha_rad = math.asin(sin_alpha)
# وزن هر متر ورق (کیلوگرم بر متر)
# W = 7.85 * width(m) * thickness(mm)
weight_per_meter_strip = 7.85 * (strip_width / 1000.0) * wall_thickness

st.sidebar.markdown("---")
st.sidebar.info(f"📐 **زاویه حلزونی:** {math.degrees(alpha_rad):.2f} درجه\n\n⚖️ **وزن هر متر ورق:** {weight_per_meter_strip:.2f} kg/m")

# --- بخش دوم: ثبت مشخصات کلاف‌ها ---
st.header("📦 ثبت اطلاعات کلاف‌های پروژه")

num_coils = st.number_input("تعداد کلاف‌های پروژه:", min_value=1, max_value=50, value=12, step=1)

coil_data = []
col1, col2 = st.columns(2)

with col1:
    st.write("### مشخصات کلاف‌ها")
    for i in range(int(num_coils)):
        c_cols = st.columns(3)
        with c_cols[0]:
            weight = st.number_input(f"وزن کلاف {i+1} (تن):", value=15.0 + (i % 3), step=0.5, key=f"w_{i}")
        with c_cols[1]:
            head_crop = st.number_input(f"برش سر کلاف {i+1} (cm):", value=50.0, step=5.0, key=f"hc_{i}")
        with c_cols[2]:
            tail_crop = st.number_input(f"برش ته کلاف {i+1} (cm):", value=30.0, step=5.0, key=f"tc_{i}")
        
        # طول کل کلاف بر اساس وزن
        strip_length_m = (weight * 1000.0) / weight_per_meter_strip
        usable_strip_m = strip_length_m - (head_crop / 100.0) - (tail_crop / 100.0)
        # طول لوله حاصل از این کلاف (با در نظر گرفتن زاویه حلزونی)
        pipe_length_m = usable_strip_m / sin_alpha
        
        coil_data.append({
            'id': i + 1,
            'weight_ton': weight,
            'head_crop_m': head_crop / 100.0,
            'tail_crop_m': tail_crop / 100.0,
            'strip_length_m': strip_length_m,
            'pipe_length_m': pipe_length_m
        })

# --- بخش سوم: تحلیل و شبیه‌سازی خط تولید ---
if st.button("🚀 تحلیل زنجیره تولید و بررسی T-Joint‌ها", type="primary"):
    st.markdown("---")
    st.header("📊 نتایج شبیه‌سازی و وضعیت T-Joint‌ها")
    
    current_position_in_pipe = 0.0 # موقعیت لوله جاری نسبت به خط برش
    total_pipes_produced = 0
    total_scrap_weight_kg = 0.0
    total_useful_pipe_length_m = 0.0
    
    warnings = []
    
    for idx, coil in enumerate(coil_data):
        st.subheader(f"🌀 کلاف شماره {coil['id']} (وزن: {coil['weight_ton']} تن)")
        
        # محاسبه ضایعات سر و ته کلاف
        head_tail_scrap_kg = (coil['head_crop_m'] + coil['tail_crop_m']) * weight_per_meter_strip
        total_scrap_weight_kg += head_tail_scrap_kg
        
        coil_pipe_len = coil['pipe_length_m']
        remaining_in_coil = coil_pipe_len
        
        st.write(f"- **طول لوله حاصل از این کلاف:** {coil_pipe_len:.2f} متر")
        
        # بررسی T-Joint اتصال کلاف قبلی به این کلاف
        if idx > 0:
            # موقعیت T دقیقاً در نقطه‌ای است که کلاف قبلی تمام شده و کلاف جدید شروع شده
            t_distance_to_next_cut = target_pipe_length - current_position_in_pipe
            
            st.info(f"📍 **موقعیت T-Joint (جوش وصله کلاف {coil['id']-1} به {coil['id']}):** {t_distance_to_next_cut:.2f} متر قبل از خط برش بعدی")
            
            if t_distance_to_next_cut < (min_safe_t_dist / 100.0) or (target_pipe_length - t_distance_to_next_cut) < (min_safe_t_dist / 100.0):
                st.error(f"⚠️ **هشدار برخورد T به برش!** در اتصال کلاف {coil['id']-1} به {coil['id']}، فاصله T تا خط برش تنها {t_distance_to_next_cut*100:.1f} سانتی‌متر است.")
                
                # ارائه راهکار برون‌رفت
                shift_needed_cm = (min_safe_t_dist) - (t_distance_to_next_cut * 100.0)
                st.warning(f"""
                💡 **راهکارهای پیشنهادی برون‌رفت از مشکل:**
                1. **تغییر برش سرکلاف:** مقدار برش سر کلاف شماره {coil['id']} را به میزان **{abs(shift_needed_cm):.1f} سانتی‌متر** تغییر (افزایش/کاهش) دهید.
                2. **تغییر طول برش شاخه قبل:** طول شاخه لوله قبل از T را به جای {target_pipe_length} متر، برابر **{(target_pipe_length - (shift_needed_cm/100.0)):.2f} متر** برش بزنید.
                """)
        
        # شاخه‌بندی کلاف
        while (current_position_in_pipe + remaining_in_coil) >= target_pipe_length:
            needed_to_complete = target_pipe_length - current_position_in_pipe
            remaining_in_coil -= needed_to_complete
            current_position_in_pipe = 0.0
            total_pipes_produced += 1
            total_useful_pipe_length_m += target_pipe_length
            
        current_position_in_pipe += remaining_in_coil
        st.write(f"- **باقیمانده کلاف روی شاخه جاری:** {current_position_in_pipe:.2f} متر")
        st.markdown("---")
        
    # --- بخش چهارم: گزارش پایانی ضایعات و عملکرد ---
    st.header("📈 گزارش نهایی پروژه")
    
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    
    total_project_weight_ton = sum(c['weight_ton'] for c in coil_data)
    total_pipe_weight_ton = (total_useful_pipe_length_m * weight_per_meter_strip * sin_alpha) / 1000.0
    
    col_res1.metric("تعداد کل شاخه‌های ۱۲ متری", f"{total_pipes_produced} شاخه")
    col_res2.metric("متراژ کل لوله مفید", f"{total_useful_pipe_length_m:.2f} متر")
    col_res3.metric("کل ضایعات پروژه", f"{total_scrap_weight_kg:.1f} kg")
    col_res4.metric("بازدهی مصرف ورق", f"{((total_pipe_weight_ton/total_project_weight_ton)*100):.1f}%")

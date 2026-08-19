import math

class SpiralPipeOptimizer:
    def __init__(self):
        # ۱. مشخصات پایه پروژه
        self.project_specs = {}
        # ۲. بانک کلاف‌های موجود (kg)
        self.coils_bank = []
        # ۳. اطلاعات کلاف جاری
        self.current_coil = {}

    def set_project_specs(self, grade, strip_width, strip_thickness, pipe_diameter, pipe_length, min_t_distance):
        """ثبت مشخصات پایه پروژه (همه طول‌ها به میلی‌متر)"""
        self.project_specs = {
            "grade": grade,
            "strip_width": strip_width,        # mm
            "strip_thickness": strip_thickness, # mm
            "pipe_diameter": pipe_diameter,    # mm
            "pipe_length": pipe_length,        # mm
            "min_t_distance": min_t_distance   # mm (حد مجاز T تا برش)
        }

    def add_coils_to_bank(self, weights_list):
        """افزودن لیست وزن کلاف‌ها (به کیلوگرم)"""
        self.coils_bank.extend(weights_list)

    def set_current_coil(self, weight_kg, end_crop_mm, t_to_cut_distance_mm):
        """ثبت اطلاعات کلاف جاری (استارت)"""
        self.current_coil = {
            "weight_kg": weight_kg,
            "end_crop_mm": end_crop_mm,
            "t_to_cut_distance_mm": t_to_cut_distance_mm
        }

    def _calculate_coil_length(self, weight_kg):
        """محاسبه طول ورق کلاف (میلی‌متر) بر اساس وزن، ضخامت و عرض (چگالی فولاد 7.85g/cm3)"""
        density = 7.85e-6  # kg/mm³
        volume = weight_kg / density
        length_mm = volume / (self.project_specs["strip_width"] * self.project_specs["strip_thickness"])
        return length_mm

    def _calculate_helix_angle(self):
        """محاسبه زاویه حلزونی (آلفا)"""
        # sin(alpha) = strip_width / (pi * pipe_diameter)
        sin_alpha = self.project_specs["strip_width"] / (math.pi * self.project_specs["pipe_diameter"])
        return math.asin(sin_alpha)

    def run_analysis(self):
        """محاسبه و پیش‌بینی فاصله T تا برش برای کلاف‌های بعدی"""
        alpha = self_angle = self._calculate_helix_angle()
        pipe_len = self.project_specs["pipe_length"]
        min_t_dist = self.project_specs["min_t_distance"]

        print("\n" + "="*50)
        print("   نتایج پردازش و پیش‌بینی خط تولید لوله اسپیرال")
        print("="*50)

        # محاسبه برای کلاف جاری
        curr_len = self._calculate_coil_length(self.current_coil["weight_kg"]) - self.current_coil["end_crop_mm"]
        # تبدیل طول ورق به طول لوله روی محور اسپیرال
        curr_pipe_produced = curr_len / math.cos(alpha)
        
        # محاسبه فاصله اولین T کلاف بعدی تا خط برش
        rem_distance = (curr_pipe_produced - self.current_coil["t_to_cut_distance_mm"]) % pipe_len
        next_t_dist = (pipe_len - rem_distance) % pipe_len

        print(f"\n[کلاف جاری - استارت]")
        print(f"• وزن: {self.current_coil['weight_kg']} kg")
        print(f"• فاصله T فعلی تا برش: {self.current_coil['t_to_cut_distance_mm']} mm")
        
        status = "مجاز" if self.current_coil["t_to_cut_distance_mm"] >= min_t_dist else "❌ غیرمجاز (تداخل T با برش)"
        print(f"• وضعیت T فعلی: {status}")

        print("\n" + "-"*50)
        print("پیش‌بینی فاصله T تا برش برای کلاف‌های بانک داده:")
        print("-"*50)

        accumulated_pipe_len = self.current_coil["t_to_cut_distance_mm"]
        
        for idx, weight in enumerate(self.coils_bank, 1):
            coil_strip_len = self._calculate_coil_length(weight)
            coil_pipe_len = coil_strip_len / math.cos(alpha)
            
            # فاصله T این کلاف تا برش
            t_distance = (accumulated_pipe_len + coil_pipe_len) % pipe_len
            
            is_valid = t_distance >= min_t_dist and (pipe_len - t_distance) >= min_t_dist
            flag = "✅ مجاز" if is_valid else "⚠️ غیرمجاز (نیاز به اصلاح برش/طول)"

            print(f"کلاف شماره {idx:02d} | وزن: {weight} kg | فاصله T تا برش: {t_distance:.1f} mm | وضعیت: {flag}")
            
            # بروزرسانی نقطه مبنا برای کلاف بعدی
            accumulated_pipe_len = t_distance


# --- نمونه اجرای آزمایشی ---
if __name__ == "__main__":
    app = SpiralPipeOptimizer()

    # ۱. ثبت مشخصات پروژه (طول‌ها به میلی‌متر)
    app.set_project_specs(
        grade="ST37",
        strip_width=1500,       # mm
        strip_thickness=10,     # mm
        pipe_diameter=1200,     # mm
        pipe_length=12000,      # mm
        min_t_distance=500      # mm (حد مجاز فاصله T تا برش)
    )

    # ۲. ورود کلاف‌های باقی‌مانده پروژه (kg)
    app.add_coils_to_bank([12000, 12500, 11800, 12200])

    # ۳. ورود مشخصات کلاف جاری (استارت)
    app.set_current_coil(
        weight_kg=12000,
        end_crop_mm=300,        # mm برش آخر کلاف
        t_to_cut_distance_mm=4500 # mm فاصله T فعلی تا برش
    )

    # ۴. اجرای خروجی اولیه
    app.run_analysis()

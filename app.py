import streamlit as st
import math

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Spiral Pipe Production & T-Joint Tracker",
    layout="wide"
)

st.title("Spiral Pipe Coil & T-Joint Management System")
st.markdown("---")

# ==========================================
# SECTION 1: BASE PROJECT SPECIFICATIONS
# ==========================================
st.header("1. Base Project Specifications")

col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    D_outer = st.number_input("Outer Diameter - D (mm)", value=1800.0, step=1.0)
with col_p2:
    t_wall = st.number_input("Wall Thickness - t (mm)", value=14.2, step=0.1)
with col_p3:
    W_strip = st.number_input("Strip Width - W (mm)", value=1500.0, step=1.0)
with col_p4:
    L_branch = st.number_input("Standard Branch Length (mm)", value=12020.0, step=10.0)

# Steel Density in kg/mm^3
STEEL_DENSITY = 7.85e-6 

# Base Geometry Calculations
D_mean = D_outer - t_wall  # Mean Diameter
Perimeter = math.pi * D_mean  # Perimeter (mm)
sin_alpha = W_strip / Perimeter
alpha_deg = math.degrees(math.asin(sin_alpha))
Pitch = W_strip / math.cos(math.radians(alpha_deg))  # Weld Pitch (mm)

# Display Calculated Geometry Info
st.info(
    f"**Calculated Base Parameters:** "
    f"Mean Diameter: **{D_mean:.2f} mm** | "
    f"Perimeter (C): **{Perimeter:.2f} mm ({Perimeter/1000:.3f} m)** | "
    f"Helix Angle (&alpha;): **{alpha_deg:.2f}°** | "
    f"Weld Pitch (P): **{Pitch:.2f} mm**"
)

st.markdown("---")

# ==========================================
# SECTION 2: CURRENT COIL (START COIL)
# ==========================================
st.header("2. Current Coil Setup & T-Joint Calibration")

col_c1, col_c2 = st.columns(2)

with col_c1:
    coil_weight_kg = st.number_input("Current Coil Weight (kg)", value=23000.0, step=500.0)
    T_actual_mm = st.number_input("Actual T-Joint Position from Cut (mm)", value=400.0, step=10.0)

with col_c2:
    st.write("**Non-Standard Cut Control (T-Joint Avoidance / Testing):**")
    custom_branch_active = st.checkbox(
        "Enable Custom Length for Final Branch",
        value=False,
        help="Check this if the last pipe branch was cut shorter or longer to avoid T-joint interference or for quality testing."
    )
    
    if custom_branch_active:
        L_actual_branch = st.number_input(
            "Actual Cut Length of Final Branch (mm)",
            value=L_branch,
            step=10.0
        )
    else:
        L_actual_branch = L_branch

# Calculations for Current Coil
# 1. Total Strip Length from Weight
L_strip_total = coil_weight_kg / (W_strip * t_wall * STEEL_DENSITY)

# 2. Total Theoretical Pipe Length
L_pipe_total = L_strip_total * sin_alpha

# 3. Theoretical T-Joint Position (Modulo with standard branch length)
T_theoretical_mm = L_pipe_total % L_branch

# 4. Startup Scrap Calculation
L_loss_pipe_mm = T_theoretical_mm - T_actual_mm
if L_loss_pipe_mm < 0:
    L_loss_pipe_mm += L_branch  # Adjust if actual T crossed into next cycle

L_loss_pipe_m = L_loss_pipe_mm / 1000.0
Scrap_Area_m2 = L_loss_pipe_m * (Perimeter / 1000.0)
Scrap_Weight_kg = Scrap_Area_m2 * (t_wall / 1000.0) * 7850.0

# 5. Offset Shift Calculation for Next Coil
# Difference between actual cut length and standard project length
length_offset_mm = L_actual_branch - L_branch

# Display Results for Current Coil
st.subheader("Current Coil Analysis Results")

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("Total Pipe Output (Theoretical)", f"{L_pipe_total / 1000.0:.2f} m")
    st.metric("Theoretical T Position", f"{T_theoretical_mm:.2f} mm")

with col_r2:
    st.metric("Pipe Scrap Length", f"{L_loss_pipe_m:.2f} m ({L_loss_pipe_mm:.0f} mm)")
    st.metric("Scrap Sheet Area", f"{Scrap_Area_m2:.2f} m²")

with col_r3:
    st.metric("Scrap Weight", f"{Scrap_Weight_kg:.1f} kg")
    st.metric("Branch Offset Applied", f"{length_offset_mm:+.1f} mm")

st.markdown("---")

# ==========================================
# SECTION 3: NEXT COIL T-JOINT PREDICTION
# ==========================================
st.header("3. Bank Coils & Next T-Joint Prediction")

st.markdown("Enter weights for upcoming coils to predict T-Joint locations on future pipe branches.")

num_coils = st.number_input("Number of Upcoming Coils to Predict", min_value=1, max_value=10, value=3)

coil_inputs = []
cols = st.columns(min(num_coils, 4))
for i in range(num_coils):
    with cols[i % 4]:
        w = st.number_input(f"Coil #{i+2} Weight (kg)", value=23000.0, step=500.0, key=f"coil_{i}")
        coil_inputs.append(w)

# Calculation of Next Coils Predictions
current_accumulated_pipe_mm = (L_pipe_total - L_loss_pipe_mm) + length_offset_mm

st.subheader("Prediction Schedule")

prediction_data = []

for idx, w_kg in enumerate(coil_inputs, start=2):
    # Strip & Pipe length for this coil
    strip_len = w_kg / (W_strip * t_wall * STEEL_DENSITY)
    pipe_len = strip_len * sin_alpha
    
    current_accumulated_pipe_mm += pipe_len
    
    # Calculate T-Joint position relative to standard branch cuts
    predicted_T_position_mm = current_accumulated_pipe_mm % L_branch
    branch_number = int(current_accumulated_pipe_mm // L_branch) + 1
    
    prediction_data.append({
        "Coil Number": f"Coil #{idx}",
        "Coil Weight (kg)": f"{w_kg:,.0f}",
        "Pipe Length Yield (m)": f"{pipe_len / 1000.0:.2f}",
        "Predicted T Position on Branch (mm)": f"{predicted_T_position_mm:.2f}",
        "Target Pipe Branch #": f"{branch_number}"
    })

st.table(prediction_data)

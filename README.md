# 📊 Hospital Operations Analytics Dashboard

## Overview
This project is an end-to-end data analytics and predictive modeling dashboard designed to help hospital administrators and clinical directors optimize operations, reduce clinician workload, and anticipate patient flow. The dashboard transforms complex hospital data into actionable operational intelligence.

The project highlights the transition from standard analytics to **predictive analytics** by forecasting bed occupancy and offering concrete, data-driven recommendations to reduce administrative burdens—mirroring solutions demanded by modern healthcare environments.

## 🎨 UI/UX Design

The dashboard features a **Tactile Editorial Layout** blended with modern **Glassmorphism**, carefully crafted to feel human-made, creative, and distinct from generic AI-generated templates.

### Key Design Features:
- **Glassmorphism Sidebar:** The primary navigation features a frosted glass effect (`backdrop-filter: blur`) that beautifully overlays the textured page background, providing a premium, depth-aware interface.
- **High-Contrast Typography:** 
  - **Playfair Display (Serif)** is used for headers, numbers, and key data points to provide an elegant, magazine-style editorial feel.
  - **Inter (Sans-Serif)** is utilized for dense data, tables, and functional text to ensure maximum legibility.
- **Organic Color Palette:** Moved away from harsh neon/dark modes to a warm, off-white bone background with a subtle paper noise texture. Accents include earthy, tactile colors like Forest Green, Terracotta, Ochre, and Slate Blue.
- **Tactile Layout Elements:** Asymmetrical "bento-box" rounded corners, crisp 1px borders, and soft directional shadows make the dashboard cards look like physical printed elements.

## 💻 Webpage Features & Details

The dashboard is structured into four primary intelligence views:

### 1. Dashboard (Clinician Workload & Patient Flow)
- **Insight Banner:** Highlights a critical operational insight and an immediate action required.
- **Department Wait Times:** A time-series chart showing average wait times across key departments (ED, Radiology, Surgery, etc.).
- **Peak Arrival Heatmap:** A visual matrix highlighting patient load by hour and day to easily identify workflow bottlenecks.
- **Readmission by Age:** A bar chart identifying high-risk demographics for readmission.
- **Occupancy Forecast:** A dual-axis line chart comparing historical 14-day occupancy with a 7-day predicted forecast.

### 2. Staffing (Staffing Intelligence)
- **24-Hour Staffing Needs:** A layered area chart recommending hourly staffing levels separated by department.
- **Staff Directory & Assignments:** An interactive directory of attending physicians and nurses. Clicking a staff member reveals their currently assigned patients, diagnosis details, and readmission risk levels.

### 3. Occupancy (Bed Utilization)
- **Detailed Forecast Chart:** An expanded view overlaying historical occupancy bars with a dashed predictive trend line.
- **Utilization Ring:** A clean doughnut chart displaying current bed utilization vs. availability.
- **Live Metrics:** Quick-glance statistic cards showing exact numbers for Occupied Beds, Available Beds, Utilization Rate, and the 7-Day Forecast Change percentage.

### 4. Reports (Operational Reports & Patient Records)
- **Concrete Recommendations:** Three actionable editorial cards detailing evidence-based solutions (e.g., "Reallocate Staff to ED", "Senior Follow-up Protocol").
- **Patient Journey History:** A complete tabular view of active patient records. Clicking a row dynamically expands a detailed panel showing the patient's entire journey, including admission date, diagnosis, wait times, risk factors, and prescribed medications.

## 🛠️ Technical Stack
- **Frontend UI:** HTML5, Vanilla CSS3 (Custom Design System), JavaScript
- **Data Visualization:** Chart.js
- **Backend / ETL:** Python, Pandas (used to clean, process, and forecast raw hospital data into the structured JSON consumed by the dashboard)
- **Deployment:** GitHub Pages

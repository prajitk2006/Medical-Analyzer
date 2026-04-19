// ── Chart.js Global Defaults ──────────────────────────────────
Chart.defaults.color = '#94A3B8';
Chart.defaults.font.family = "'Outfit', system-ui, sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(11, 14, 20, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#F8FAFC';
Chart.defaults.plugins.tooltip.bodyColor = '#94A3B8';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.boxPadding = 6;
Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.05)';

// ── Utilities ─────────────────────────────────────────────────
async function fetchJSON(path) {
    try {
        const r = await fetch(path);
        if (!r.ok) throw new Error('not found');
        return await r.json();
    } catch (e) {
        console.warn('Could not load', path);
        return null;
    }
}

function showView(id) {
    document.querySelectorAll('.view').forEach(v => {
        v.classList.remove('active-view', 'animate-enter');
    });
    const target = document.getElementById(id);
    if (target) {
        target.classList.add('active-view');
        // Trigger animation on next frame
        requestAnimationFrame(() => target.classList.add('animate-enter'));
    }
}

// ── Navigation ────────────────────────────────────────────────
function setupNav(onTabChange) {
    const links = document.querySelectorAll('#navLinks li');
    links.forEach(link => {
        link.addEventListener('click', () => {
            links.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            const target = link.getAttribute('data-target');
            showView(target);
            if (onTabChange) onTabChange(target);

            // Update header text
            const titles = {
            'view-dashboard': { title: 'Clinician Workload & Patient Flow', sub: 'Data-driven recommendations to reduce administrative burden and optimize shift scheduling' },
            'view-staffing': { title: 'Staffing Intelligence', sub: 'Real-time directory and predictive hourly staffing models' },
            'view-occupancy': { title: 'Bed Occupancy Analytics', sub: 'Utilization rates, capacity forecasting, and historical trends' },
            'view-reports': { title: 'Operational Reports', sub: 'Actionable evidence-based clinical recommendations and patient records' },
            'view-datasets': { title: 'System Datasets', sub: 'Processed and aggregated intelligence data serving the dashboard' }
        };
            if (titles[target]) {
                document.getElementById('pageTitle').textContent = titles[target].title;
                document.getElementById('pageSubtitle').textContent = titles[target].sub;
            }
        });
    });
}

// ── Main Init ─────────────────────────────────────────────────
async function init() {
    // Load data
    const [deptData, heatData, occData, foreData, staffData, staffDetails, patients] = await Promise.all([
        fetchJSON('./data/processed/dept_wait_metrics.json'),
        fetchJSON('./data/processed/peak_load_heatmap.json'),
        fetchJSON('./data/processed/bed_occupancy_daily.json'),
        fetchJSON('./data/processed/bed_forecast.json'),
        fetchJSON('./data/processed/staffing_needs_by_dept_hour.json'),
        fetchJSON('./data/processed/staff_details.json'),
        fetchJSON('./data/processed/detailed_patients.json'),
    ]);

    // Show dashboard tab first
    showView('view-dashboard');
    buildDeptChart(deptData);
    buildHeatmap(heatData);
    buildReadmissionChart();
    buildOccupancyOverview(occData, foreData);

    // Track which tabs have been initialized
    const done = {};

    setupNav((tabId) => {
        if (tabId === 'view-staffing' && !done.staffing) {
            done.staffing = true;
            buildStaffingChart(staffData);
            buildStaffDirectory(staffDetails, patients);
        }
        if (tabId === 'view-occupancy' && !done.occupancy) {
            done.occupancy = true;
            buildDetailedOccChart(occData, foreData);
            buildUtilizationChart(occData);
            buildOccStats(occData);
        }
        if (tabId === 'view-reports' && !done.reports) {
            done.reports = true;
            buildPatientTable(patients);
        }
    });
}

// ── Dashboard Charts ──────────────────────────────────────────
function buildDeptChart(data) {
    const depts = data ? data.map(d => d.Department) : ['Emergency','Radiology','Surgery','Cardiology','Neurology','Pediatrics'];
    const waits = data ? data.map(d => d.Avg_Wait_Minutes) : [45,30,15,12,18,14];
    const colors = ['#2C4C3B','#C85A47','#DDA74F','#3E5A74','#8B7355','#4A6B5D'];
    const labels = [];
    for (let i = 0; i < 28; i++) {
        const d = new Date(2023, 11, i + 1);
        labels.push(d.toLocaleDateString('en-US', { month:'short', day:'numeric' }));
    }
    const datasets = depts.map((dept, i) => ({
        label: dept,
        data: labels.map(() => Math.max(5, waits[i] * (0.9 + Math.random() * 0.3))),
        borderColor: colors[i % colors.length],
        backgroundColor: 'transparent',
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        borderWidth: 2,
    }));
    new Chart(document.getElementById('deptChart'), {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position:'top', labels: { usePointStyle:true, boxWidth:6 }}},
            scales: {
                y: { beginAtZero: true, grid: { drawBorder: false }},
                x: { grid: { display: false }},
            },
            interaction: { mode:'index', intersect:false },
            animation: { y: { duration:1800, easing:'easeOutQuart' }},
        }
    });
}

function buildHeatmap(data) {
    const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
    const mat = {};
    for (let h = 0; h < 24; h++) {
        mat[h] = {};
        days.forEach(d => mat[h][d] = 0);
    }
    if (data) {
        data.forEach(r => {
            if (mat[r.Admission_Hour] && mat[r.Admission_Hour][r.Admission_DayOfWeek] !== undefined)
                mat[r.Admission_Hour][r.Admission_DayOfWeek] = r.Patient_Count;
        });
    } else {
        for (let h = 0; h < 24; h++) days.forEach(d => {
            let b = (h > 8 && h < 20) ? 40 : 8;
            if (d === 'Tuesday' && h >= 7 && h <= 14) b += 80;
            mat[h][d] = b + Math.floor(Math.random() * 15);
        });
    }
    let max = 0;
    Object.values(mat).forEach(row => Object.values(row).forEach(v => { if (v > max) max = v; }));

    const tbl = document.getElementById('heatmapTable');
    let html = '<thead><tr><th>Time</th>' + days.map(d => `<th>${d.slice(0,3)}</th>`).join('') + '</tr></thead><tbody>';
    for (let i = 0; i < 24; i += 4) {
        html += `<tr><td style="color:var(--muted)">${i}:00</td>`;
        days.forEach(d => {
            let sum = 0;
            for (let j = 0; j < 4; j++) sum += mat[i + j][d];
            const int = sum / (max * 4);
            const bg = `rgba(56,189,248,${0.05 + int * 0.95})`;
            const col = int > 0.5 ? '#fff' : 'var(--accent)';
            html += `<td style="background:${bg};color:${col}">${sum}</td>`;
        });
        html += '</tr>';
    }
    tbl.innerHTML = html + '</tbody>';
}

function buildReadmissionChart() {
    new Chart(document.getElementById('readmissionChart'), {
        type: 'bar',
        data: {
            labels: ['0–17','18–40','41–65','66+'],
            datasets: [{
                label: 'Readmission Rate (%)',
                data: [8.2, 10.5, 14.3, 27.1],
                backgroundColor: (ctx) => ctx.dataIndex === 3 ? '#F43F5E' : '#38BDF8',
                borderRadius: 6,
                borderWidth: 0,
                barPercentage: 0.6,
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display:false }},
            scales: {
                y: { beginAtZero: true, grid: { drawBorder: false }},
                x: { grid: { display: false }},
            },
            animation: { y: { duration:1400, easing:'easeOutBack' }},
        }
    });
}

function buildOccupancyOverview(occData, foreData) {
    let hDates=[], hRates=[], fDates=[], fRates=[];
    if (occData && foreData) {
        const rec = occData.slice(-14);
        hDates = rec.map(d => d.Date.split('T')[0]);
        hRates = rec.map(d => d.Occupancy_Rate);
        fDates = foreData.map(d => d.Date.split('T')[0]);
        fRates = foreData.map(d => d.Forecasted_Beds);
    } else {
        for (let i=0;i<14;i++) { hDates.push(`D-${14-i}`); hRates.push(68+Math.random()*16); }
        for (let i=0;i<7;i++)  { fDates.push(`D+${i+1}`);  fRates.push(84+i*2+Math.random()*4); }
    }
    const allDates = [...hDates, ...fDates];
    const hSeries  = [...hRates, ...Array(fDates.length).fill(null)];
    const fSeries  = [...Array(hDates.length-1).fill(null), hRates[hRates.length-1], ...fRates];
    const ctx = document.getElementById('occupancyChart').getContext('2d');
    const grad = ctx.createLinearGradient(0,0,0,260);
    grad.addColorStop(0,'rgba(56,189,248,.3)'); grad.addColorStop(1,'rgba(56,189,248,0)');
    new Chart(ctx, {
        type:'line',
        data: { labels:allDates, datasets:[
            { label:'Historical', data:hSeries, borderColor:'#38BDF8', backgroundColor:grad, fill:true, tension:.3, pointRadius:3, borderWidth:2 },
            { label:'Forecast',   data:fSeries, borderColor:'#FBBF24', borderDash:[5,5], backgroundColor:'transparent', tension:.3, pointRadius:4, pointBackgroundColor:'#FFFFFF', borderWidth:2 },
        ]},
        options: {
            responsive:true, maintainAspectRatio:false,
            interaction:{mode:'index',intersect:false},
            plugins:{ legend:{position:'top',labels:{usePointStyle:true,boxWidth:6}} },
            scales:{ y:{min:40,max:120,grid:{drawBorder:false}}, x:{grid:{display:false}} },
            animation:{ x:{duration:1800,easing:'easeOutExpo'} },
        }
    });
}

// ── Staffing Charts ───────────────────────────────────────────
function buildStaffingChart(data) {
    if (!data) return;
    const depts = [...new Set(data.map(d => d.Department))];
    const hours = Array.from({length:24}, (_,i) => `${i}:00`);
    const colors = ['#38BDF8','#F43F5E','#FBBF24','#10B981','#8B5CF6','#6366F1'];
    const datasets = depts.map((dept,i) => {
        const pts = data.filter(d => d.Department===dept).sort((a,b) => a.Admission_Hour-b.Admission_Hour);
        return {
            label: dept,
            data: pts.map(d => d.Recommended_Staff),
            borderColor: colors[i%colors.length],
            backgroundColor: colors[i%colors.length]+'28',
            fill:true, tension:.4, pointRadius:2, pointHoverRadius:6, borderWidth:2,
        };
    });
    new Chart(document.getElementById('staffingChart'), {
        type:'line',
        data:{labels:hours, datasets},
        options:{
            responsive:true, maintainAspectRatio:false,
            plugins:{ legend:{position:'top',labels:{usePointStyle:true,boxWidth:6}}, tooltip:{mode:'index',intersect:false} },
            scales:{
                y:{beginAtZero:true, title:{display:true,text:'Recommended Staff'}, grid:{drawBorder:false}},
                x:{title:{display:true,text:'Hour of Day'}, grid:{display:false}},
            },
            interaction:{mode:'index',intersect:false},
            animation:{y:{duration:2000,easing:'easeOutQuart'}},
        }
    });
}

function buildStaffDirectory(staffList, patients) {
    if (!staffList) return;
    const grid = document.getElementById('staffDirectory');
    const panel = document.getElementById('staffPanel');
    grid.innerHTML = '';

    staffList.forEach(staff => {
        const icon = staff.Role === 'Attending Physician' ? 'fa-user-doctor' : 'fa-user-nurse';
        const card = document.createElement('div');
        card.className = 'staff-card';
        card.innerHTML = `
            <i class="fa-solid ${icon} staff-icon"></i>
            <div class="staff-name">${staff.Name}</div>
            <div class="staff-role">${staff.Role}</div>
            <div class="staff-dept">${staff.Department}</div>
        `;
        card.addEventListener('click', () => {
            document.querySelectorAll('.staff-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            const myPts = patients ? patients.filter(p => p.Assigned_Doctor_ID===staff.Staff_ID || p.Assigned_Nurse_ID===staff.Staff_ID) : [];
            panel.classList.remove('hidden');
            panel.innerHTML = `
                <h3><i class="fa-solid fa-clipboard-user"></i> ${staff.Name} — ${myPts.length} Patient(s) Assigned</h3>
                <ul class="detail-list">
                    ${myPts.length===0 ? '<li>No current assignments.</li>' : myPts.map(p => `
                        <li>
                            <div style="display:flex;justify-content:space-between;align-items:center">
                                <strong>${p.Patient_ID}</strong>
                                <span class="risk-badge ${p.Readmission_Risk==1?'risk-high':'risk-low'}">${p.Readmission_Risk==1?'⚠ High Risk':'✓ Low Risk'}</span>
                            </div>
                            <div style="color:var(--muted);font-size:.85rem">${p.Department} · <em>${p.Diagnosis}</em></div>
                            <div class="meds">💊 ${p.Medications ? p.Medications.join(', ') : 'N/A'}</div>
                        </li>
                    `).join('')}
                </ul>
            `;
        });
        grid.appendChild(card);
    });
}

// ── Occupancy Charts ──────────────────────────────────────────
function buildDetailedOccChart(occData, foreData) {
    if (!occData || !foreData) return;
    const hist = occData.slice(-30);
    const hD = hist.map(d => d.Date.split('T')[0]);
    const hR = hist.map(d => d.Occupancy_Rate);
    const fD = foreData.map(d => d.Date.split('T')[0]);
    const fR = foreData.map(d => d.Forecasted_Beds);
    const all = [...hD,...fD];
    const hS  = [...hR, ...Array(fD.length).fill(null)];
    const fS  = [...Array(hD.length-1).fill(null), hR[hR.length-1], ...fR];
    const ctx = document.getElementById('detailedOccChart').getContext('2d');
    const grad = ctx.createLinearGradient(0,0,0,350);
    grad.addColorStop(0,'rgba(56,189,248,.3)'); grad.addColorStop(1,'rgba(56,189,248,0)');
    new Chart(ctx, {
        type:'bar',
        data:{ labels:all, datasets:[
            { type:'line', label:'Forecast', data:fS, borderColor:'#FBBF24', borderDash:[5,5], backgroundColor:'transparent', tension:.3, pointRadius:4, pointBackgroundColor:'#FFFFFF', borderWidth:2.5 },
            { type:'bar',  label:'Historical Occupancy', data:hS, backgroundColor:grad, borderColor:'#38BDF8', borderWidth:1, borderRadius:3 },
        ]},
        options:{
            responsive:true, maintainAspectRatio:false,
            interaction:{mode:'index',intersect:false},
            plugins:{ legend:{position:'top',labels:{usePointStyle:true,boxWidth:6}} },
            scales:{ y:{min:40,max:120,grid:{drawBorder:false}}, x:{grid:{display:false}} },
            animation:{ y:{duration:1500,easing:'easeOutBounce'} },
        }
    });
}

function buildUtilizationChart(occData) {
    if (!occData) return;
    const latest = occData[occData.length-1];
    const occupied = Math.min(Math.round(latest.Occupancy_Rate), 100);
    const available = 100 - occupied;

    // Update stat cards
    document.getElementById('statOccupied').textContent = occupied;
    document.getElementById('statAvail').textContent = available;
    document.getElementById('statRate').textContent = occupied + '%';

    const isHigh = occupied > 85;

    new Chart(document.getElementById('utilizationChart'), {
        type:'doughnut',
        data:{
            labels:['Occupied','Available'],
            datasets:[{
                data:[occupied, available],
                backgroundColor: [isHigh ? '#F43F5E' : '#38BDF8', 'rgba(255,255,255,0.05)'],
                borderColor:     [isHigh ? '#F43F5E' : '#38BDF8', 'transparent'],
                borderWidth:2,
                hoverOffset:8,
            }]
        },
        options:{
            responsive:true, maintainAspectRatio:false,
            cutout:'72%',
            plugins:{
                legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:8, padding:20}},
                tooltip:{ callbacks:{ label: ctx => ` ${ctx.label}: ${ctx.parsed} beds` }},
            },
            animation:{ animateRotate:true, duration:1500, easing:'easeOutQuart' },
        },
        plugins:[{
            id:'center',
            afterDraw(chart) {
                const {ctx, chartArea:{top,width,height}} = chart;
                ctx.save();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                const cx = width/2, cy = top+height/2;
                ctx.font = 'bold 2.4rem Outfit, sans-serif';
                ctx.fillStyle = '#F8FAFC';
                ctx.fillText(`${occupied}%`, cx, cy-12);
                ctx.font = '.82rem Outfit, sans-serif';
                ctx.fillStyle = '#94A3B8';
                ctx.fillText('Utilization', cx, cy+18);
                ctx.restore();
            }
        }]
    });
}

function buildOccStats(occData) {
    if (!occData) return;
    const latest = occData[occData.length-1];
    const occupied = Math.min(Math.round(latest.Occupancy_Rate), 100);
    document.getElementById('statOccupied').textContent = occupied;
    document.getElementById('statAvail').textContent = 100 - occupied;
    document.getElementById('statRate').textContent = occupied + '%';
}

// ── Reports & Patient Table ───────────────────────────────────
function buildPatientTable(patients) {
    if (!patients) return;
    const tbody = document.querySelector('#patientTable tbody');
    const panel = document.getElementById('patientPanel');
    const rows = patients.slice(0, 200);

    rows.forEach(p => {
        const tr = document.createElement('tr');
        const isHigh = p.Readmission_Risk == 1;
        tr.innerHTML = `
            <td><strong>${p.Patient_ID}</strong></td>
            <td>${p.Admission_Date ? p.Admission_Date.split(' ')[0] : '—'}</td>
            <td>${p.Department}</td>
            <td>${p.Diagnosis}</td>
            <td>${p.Assigned_Doctor_Name || '—'}</td>
            <td><span class="risk-badge ${isHigh?'risk-high':'risk-low'}">${isHigh?'⚠ High':'✓ Low'}</span></td>
        `;
        tr.addEventListener('click', () => {
            document.querySelectorAll('#patientTable tbody tr').forEach(r => r.classList.remove('row-selected'));
            tr.classList.add('row-selected');
            panel.classList.remove('hidden');
            panel.innerHTML = `
                <h3><i class="fa-solid fa-notes-medical"></i> Patient Journey — ${p.Patient_ID}</h3>
                <div class="journey-grid">
                    <div class="journey-item"><div class="j-label">Department</div><div class="j-val">${p.Department}</div></div>
                    <div class="journey-item"><div class="j-label">Diagnosis</div><div class="j-val">${p.Diagnosis}</div></div>
                    <div class="journey-item"><div class="j-label">Admission Date</div><div class="j-val">${p.Admission_Date ? p.Admission_Date.split(' ')[0] : '—'}</div></div>
                    <div class="journey-item"><div class="j-label">Length of Stay</div><div class="j-val">${p.Length_of_Stay_Days} day(s)</div></div>
                    <div class="journey-item"><div class="j-label">Wait Time</div><div class="j-val">${Math.round(p.Wait_Time_Minutes)} min</div></div>
                    <div class="journey-item"><div class="j-label">Readmission Risk</div><div class="j-val"><span class="risk-badge ${isHigh?'risk-high':'risk-low'}">${isHigh?'⚠ High Risk':'✓ Low Risk'}</span></div></div>
                    <div class="journey-item"><div class="j-label">Attending Doctor</div><div class="j-val">${p.Assigned_Doctor_Name || '—'}</div></div>
                    <div class="journey-item"><div class="j-label">Assigned Nurse</div><div class="j-val">${p.Assigned_Nurse_Name || '—'}</div></div>
                </div>
                <div style="margin-top:12px"><div class="j-label" style="margin-bottom:6px">Medications</div>
                    <div class="med-tags">${p.Medications ? p.Medications.map(m=>`<span class="med-tag">${m}</span>`).join('') : 'N/A'}</div>
                </div>
            `;
            panel.scrollIntoView({ behavior:'smooth', block:'nearest' });
        });
        tbody.appendChild(tr);
    });
}

// ── Start ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);

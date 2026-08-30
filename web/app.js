document.addEventListener("DOMContentLoaded", () => {
    initFunnelChart();
    initChannelChart();
    populateFunnelList();
    populateChannelTable();
    updateSalaryCard();
});

function switchTab(tabId) {
    document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
    document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
    
    document.getElementById(tabId).classList.remove("hidden");
    const btn = document.getElementById(`btn-${tabId}`);
    if (btn) btn.classList.add("active");
}

function initFunnelChart() {
    const ctx = document.getElementById("funnelChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["1. Applied", "2. Screening", "3. Tech Challenge", "4. Executive Interview", "5. Offer Accepted"],
            datasets: [
                {
                    label: "Candidate Volume",
                    data: [50000, 31920, 16180, 7120, 1914],
                    backgroundColor: [
                        "rgba(56, 189, 248, 0.85)",
                        "rgba(14, 165, 233, 0.85)",
                        "rgba(99, 102, 241, 0.85)",
                        "rgba(168, 85, 247, 0.85)",
                        "rgba(52, 211, 153, 0.95)"
                    ],
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: c => ` Volume: ${c.parsed.y.toLocaleString()} Candidates (${((c.parsed.y / 50000) * 100).toFixed(1)}%)`
                    }
                }
            },
            scales: {
                x: { ticks: { color: "#cbd5e1", font: { size: 11 } }, grid: { display: false } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(51, 65, 85, 0.25)" } }
            }
        }
    });
}

function initChannelChart() {
    const ctx = document.getElementById("channelChart").getContext("2d");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["LinkedIn Recruiter", "Employee Referral", "Inbound Careers", "Headhunting Agency", "Direct Sourcing"],
            datasets: [{
                data: [674, 492, 381, 230, 137],
                backgroundColor: [
                    "#0284c7",
                    "#10b981",
                    "#6366f1",
                    "#f59e0b",
                    "#ec4899"
                ],
                borderWidth: 0,
                cutout: "70%"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom", labels: { color: "#94a3b8", font: { size: 10 }, padding: 12 } }
            }
        }
    });
}

function populateFunnelList() {
    const stages = [
        { name: "1_Applied", count: "50,000", pct: "100.0%", days: "3.2d" },
        { name: "2_Screening", count: "31,920", pct: "63.8%", days: "9.8d" },
        { name: "3_Tech Challenge", count: "16,180", pct: "32.4%", days: "19.5d" },
        { name: "4_Executive Interview", count: "7,120", pct: "14.2%", days: "31.4d" },
        { name: "5_Offer Accepted", count: "1,914", pct: "3.83%", days: "44.2d" }
    ];

    const list = document.getElementById("funnel-stage-list");
    list.innerHTML = stages.map(s => `
        <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
            <div>
                <span class="font-bold text-slate-200">${s.name}</span>
                <div class="text-[10px] text-slate-400">Velocity: ${s.days}</div>
            </div>
            <div class="text-right font-mono">
                <div class="text-white font-bold">${s.count}</div>
                <div class="text-[10px] text-sky-400">${s.pct}</div>
            </div>
        </div>
    `).join("");
}

function populateChannelTable() {
    const channels = [
        { name: "Employee Referral", apps: "8,950", hires: "492", rate: "5.50%", cph: "$21,800", high: true },
        { name: "Direct Sourcing Outreach", apps: "4,010", hires: "137", rate: "3.42%", cph: "$8,190", high: true },
        { name: "LinkedIn Recruiter", apps: "19,050", hires: "674", rate: "3.54%", cph: "$12,710", high: true },
        { name: "Inbound Careers Portal", apps: "11,990", hires: "381", rate: "3.18%", cph: "$1,570", high: true },
        { name: "External Headhunting Agency", apps: "6,000", hires: "230", rate: "3.83%", cph: "$143,478", high: false }
    ];

    const tbody = document.getElementById("channel-table-body");
    tbody.innerHTML = channels.map(c => `
        <tr class="hover:bg-slate-900/40 transition-colors">
            <td class="py-2.5 font-sans font-semibold text-slate-200">${c.name}</td>
            <td class="py-2.5 text-center text-slate-400">${c.apps}</td>
            <td class="py-2.5 text-center text-white font-bold">${c.hires}</td>
            <td class="py-2.5 text-center text-sky-400">${c.rate}</td>
            <td class="py-2.5 text-right font-bold ${c.high ? 'text-emerald-400' : 'text-rose-400'}">${c.cph}</td>
        </tr>
    `).join("");
}

const salaryMatrix = {
    "Data & AI": {
        "Junior": { ask: 68500, budget: 72000 },
        "Mid-Level": { ask: 104200, budget: 108000 },
        "Senior": { ask: 151400, budget: 156000 },
        "Lead / Staff": { ask: 198200, budget: 205000 }
    },
    "Engineering": {
        "Junior": { ask: 65400, budget: 68000 },
        "Mid-Level": { ask: 98500, budget: 102000 },
        "Senior": { ask: 144200, budget: 148000 },
        "Lead / Staff": { ask: 189500, budget: 195000 }
    },
    "Product & Design": {
        "Junior": { ask: 54200, budget: 56000 },
        "Mid-Level": { ask: 84300, budget: 88000 },
        "Senior": { ask: 122500, budget: 126000 },
        "Lead / Staff": { ask: 161000, budget: 168000 }
    }
};

function updateSalaryCard() {
    const dept = document.getElementById("sel-dept").value;
    const seniority = document.getElementById("sel-seniority").value;

    const data = salaryMatrix[dept][seniority];
    const gap = data.ask - data.budget;

    document.getElementById("card-avg-ask").innerText = `$${data.ask.toLocaleString()} USD`;
    document.getElementById("card-budget-max").innerText = `$${data.budget.toLocaleString()}`;
    document.getElementById("card-ask-val").innerText = `$${data.ask.toLocaleString()}`;
    
    const gapElem = document.getElementById("card-gap-val");
    if (gap <= 0) {
        gapElem.innerText = `-$${Math.abs(gap).toLocaleString()}`;
        gapElem.className = "text-lg font-bold text-emerald-400 mt-1";
        document.getElementById("card-badge").innerText = "WITHIN BUDGET BAND";
        document.getElementById("card-badge").className = "px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold font-mono";
    } else {
        gapElem.innerText = `+$${gap.toLocaleString()}`;
        gapElem.className = "text-lg font-bold text-rose-400 mt-1";
        document.getElementById("card-badge").innerText = "BUDGET OVERRUN RISK";
        document.getElementById("card-badge").className = "px-3 py-1.5 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-bold font-mono";
    }
}

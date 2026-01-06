"""
Create team dashboard HTML with embedded JSON data
"""

import json

# Read the JSON data
with open(r"C:\Code\Promethian  Light\team_dashboard_data.json", 'r') as f:
    data = json.load(f)

# Create HTML with embedded data
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Burn Rate Dashboard - All 15 Members</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }

        .dashboard {
            max-width: 1600px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .header h1 {
            color: #1a202c;
            font-size: 32px;
            margin-bottom: 10px;
        }

        .header .subtitle {
            color: #718096;
            font-size: 16px;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .tab-button {
            background: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }

        .tab-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .tab-button.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .metric-card .label {
            color: #718096;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .metric-card .value {
            color: #1a202c;
            font-size: 32px;
            font-weight: bold;
        }

        .metric-card .subvalue {
            color: #4299e1;
            font-size: 14px;
            margin-top: 4px;
        }

        .chart-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .chart-card h2 {
            color: #1a202c;
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }

        .employee-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .employee-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .employee-card .name {
            color: #1a202c;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 4px;
        }

        .employee-card .position {
            color: #718096;
            font-size: 14px;
            margin-bottom: 12px;
        }

        .employee-card .stat {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }

        .employee-card .stat:last-child {
            border-bottom: none;
        }

        .employee-card .stat .label {
            color: #4a5568;
            font-size: 14px;
        }

        .employee-card .stat .value {
            color: #1a202c;
            font-size: 14px;
            font-weight: 600;
        }

        .utilization-bar {
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            margin-top: 8px;
            overflow: hidden;
        }

        .utilization-fill {
            height: 100%;
            background: linear-gradient(90deg, #48bb78 0%, #38a169 100%);
            transition: width 0.3s;
        }

        .utilization-fill.low {
            background: linear-gradient(90deg, #f56565 0%, #e53e3e 100%);
        }

        .utilization-fill.medium {
            background: linear-gradient(90deg, #ecc94b 0%, #d69e2e 100%);
        }

        .table-container {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: #f7fafc;
            padding: 12px;
            text-align: left;
            color: #4a5568;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e2e8f0;
            position: sticky;
            top: 0;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            color: #2d3748;
        }

        tr:hover {
            background: #f7fafc;
        }

        .project-list {
            font-size: 12px;
            color: #4a5568;
            margin-top: 8px;
        }

        .project-item {
            padding: 4px 0;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        // Embedded data
        const DASHBOARD_DATA = ''' + json.dumps(data, indent=2) + ''';

        const Dashboard = () => {
            const [activeTab, setActiveTab] = React.useState('overview');
            const [data, setData] = React.useState(DASHBOARD_DATA);
            const chartRef = React.useRef(null);

            React.useEffect(() => {
                if (!data || activeTab !== 'overview') return;

                const ctx = document.getElementById('teamChart');
                if (!ctx) return;

                if (chartRef.current) {
                    chartRef.current.destroy();
                }

                chartRef.current = new Chart(ctx.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: data.employees.map(e => {
                            const parts = e.name.split(' ');
                            return parts[0] + ' ' + parts[parts.length - 1];
                        }),
                        datasets: [{
                            label: 'Total Hours',
                            data: data.employees.map(e => e.totalHours),
                            backgroundColor: 'rgba(54, 162, 235, 0.8)',
                            borderWidth: 0
                        }, {
                            label: 'Billable Hours',
                            data: data.employees.map(e => e.billableHours),
                            backgroundColor: 'rgba(75, 192, 192, 0.8)',
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true, position: 'top' }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { callback: (value) => `${value}h` }
                            }
                        }
                    }
                });

                return () => {
                    if (chartRef.current) {
                        chartRef.current.destroy();
                    }
                };
            }, [activeTab, data]);

            const getUtilizationClass = (util) => {
                if (util < 40) return 'low';
                if (util < 70) return 'medium';
                return '';
            };

            return (
                <div className="dashboard">
                    <div className="header">
                        <h1>Team Burn Rate Dashboard - All 15 Members</h1>
                        <p className="subtitle">{data.summary.dateRange} • {data.summary.numEmployees} Team Members • {data.summary.numProjects} Projects</p>
                    </div>

                    <div className="tabs">
                        <button className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
                            Overview
                        </button>
                        <button className={`tab-button ${activeTab === 'team' ? 'active' : ''}`} onClick={() => setActiveTab('team')}>
                            Team Members
                        </button>
                        <button className={`tab-button ${activeTab === 'projects' ? 'active' : ''}`} onClick={() => setActiveTab('projects')}>
                            Projects
                        </button>
                        <button className={`tab-button ${activeTab === 'table' ? 'active' : ''}`} onClick={() => setActiveTab('table')}>
                            Detailed Table
                        </button>
                    </div>

                    {activeTab === 'overview' && (
                        <>
                            <div className="metrics-grid">
                                <div className="metric-card">
                                    <div className="label">Total Hours</div>
                                    <div className="value">{data.summary.totalHours.toLocaleString()}</div>
                                    <div className="subvalue">{data.summary.avgDailyHours.toFixed(0)} hrs/day avg</div>
                                </div>
                                <div className="metric-card">
                                    <div className="label">Billable Hours</div>
                                    <div className="value">{data.summary.billableHours.toLocaleString()}</div>
                                    <div className="subvalue">{data.summary.utilization.toFixed(1)}% team utilization</div>
                                </div>
                                <div className="metric-card">
                                    <div className="label">Total Revenue</div>
                                    <div className="value">${(data.summary.totalRevenue / 1000000).toFixed(2)}M</div>
                                    <div className="subvalue">${(data.summary.totalRevenue / data.summary.billableHours).toFixed(0)}/hr avg</div>
                                </div>
                                <div className="metric-card">
                                    <div className="label">Active Projects</div>
                                    <div className="value">{data.summary.numProjects}</div>
                                    <div className="subvalue">{data.summary.numEmployees} team members</div>
                                </div>
                            </div>

                            <div className="chart-card">
                                <h2>Team Hours Comparison</h2>
                                <div style={{height: '400px'}}>
                                    <canvas id="teamChart"></canvas>
                                </div>
                            </div>
                        </>
                    )}

                    {activeTab === 'team' && (
                        <div className="employee-grid">
                            {data.employees.map((emp, idx) => (
                                <div key={idx} className="employee-card">
                                    <div className="name">{emp.name}</div>
                                    <div className="position">{emp.position}</div>
                                    <div className="stat">
                                        <span className="label">Total Hours</span>
                                        <span className="value">{emp.totalHours.toLocaleString()}h</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Billable Hours</span>
                                        <span className="value">{emp.billableHours.toLocaleString()}h</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Utilization</span>
                                        <span className="value">{emp.utilization}%</span>
                                    </div>
                                    <div className="utilization-bar">
                                        <div className={`utilization-fill ${getUtilizationClass(emp.utilization)}`} style={{width: `${emp.utilization}%`}}></div>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Revenue</span>
                                        <span className="value">${(emp.revenue / 1000).toFixed(0)}k</span>
                                    </div>
                                    <div className="stat">
                                        <span className="label">Projects</span>
                                        <span className="value">{emp.numProjects}</span>
                                    </div>
                                    {emp.projects.length > 0 && (
                                        <div className="project-list">
                                            <strong>Top Projects:</strong>
                                            {emp.projects.slice(0, 3).map((proj, pidx) => (
                                                <div key={pidx} className="project-item">
                                                    • {proj.project}: {proj.hours}h
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === 'projects' && (
                        <div className="table-container">
                            <h2 style={{marginBottom: '20px'}}>Top Projects by Revenue</h2>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Project Code</th>
                                        <th>Description</th>
                                        <th>Total Hours</th>
                                        <th>Daily Hours</th>
                                        <th>Total Revenue</th>
                                        <th>Daily Revenue</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.projects.map((project, idx) => (
                                        <tr key={idx}>
                                            <td><strong>{project.project}</strong></td>
                                            <td>{project.description}</td>
                                            <td>{project.totalHours.toFixed(1)}h</td>
                                            <td>{project.dailyHours.toFixed(1)}h/day</td>
                                            <td>${project.totalRevenue.toLocaleString()}</td>
                                            <td><strong>${project.dailyRevenue.toLocaleString()}/day</strong></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {activeTab === 'table' && (
                        <div className="table-container">
                            <h2 style={{marginBottom: '20px'}}>Detailed Team Member Breakdown</h2>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Position</th>
                                        <th>Total Hours</th>
                                        <th>Billable Hours</th>
                                        <th>Utilization</th>
                                        <th>Revenue</th>
                                        <th>Projects</th>
                                        <th>Top 3 Projects</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.employees.map((emp, idx) => (
                                        <tr key={idx}>
                                            <td><strong>{emp.name}</strong></td>
                                            <td>{emp.position}</td>
                                            <td>{emp.totalHours.toLocaleString()}h</td>
                                            <td>{emp.billableHours.toLocaleString()}h</td>
                                            <td>
                                                <span style={{
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    background: emp.utilization >= 70 ? '#c6f6d5' : emp.utilization >= 40 ? '#feebc8' : '#fed7d7',
                                                    color: emp.utilization >= 70 ? '#22543d' : emp.utilization >= 40 ? '#c05621' : '#c53030',
                                                    fontWeight: '600'
                                                }}>
                                                    {emp.utilization}%
                                                </span>
                                            </td>
                                            <td>${(emp.revenue / 1000).toFixed(0)}k</td>
                                            <td>{emp.numProjects}</td>
                                            <td style={{fontSize: '12px'}}>
                                                {emp.projects.slice(0, 3).map((proj, pidx) => (
                                                    <div key={pidx}>• {proj.project} ({proj.hours}h)</div>
                                                ))}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            );
        };

        ReactDOM.render(<Dashboard />, document.getElementById('root'));
    </script>
</body>
</html>'''

# Write the HTML file
output_path = r"C:\Code\Promethian  Light\team_dashboard.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Dashboard created successfully: {output_path}")
print(f"File size: {len(html_content) / 1024:.1f} KB")

"""
Eleven Views CSV Intelligence Suite - Fixed Version
Addresses all issues identified in diagnostic report:
- Fixed CSV parsing regex
- Added error handling and boundaries
- Added loading states and fallback UI
- Added console logging for debugging
- CDN error detection
"""

from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# Fixed CSV Viewer HTML Template
CSV_VIEWER_HTML = """{% raw %}<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eleven Views - CSV Deal Room</title>
    
    <!-- React 18 -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js" 
            onerror="handleScriptError('React')"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"
            onerror="handleScriptError('ReactDOM')"></script>
    
    <!-- Babel Standalone for JSX - Load first and wait for it -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"
            onerror="handleScriptError('Babel')"
            onload="console.log('✅ Babel loaded'); window.babelLoaded = true;"></script>
    
    <!-- Recharts -->
    <script src="https://unpkg.com/recharts@2.5.0/dist/Recharts.js"
            onerror="handleScriptError('Recharts')"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-bg: #050505;
            --secondary-bg: #121212;
            --accent-gold: #d4af37;
            --accent-bronze: #b88a1a;
            --text-primary: #f5f1e5;
            --text-secondary: rgba(245, 241, 229, 0.65);
            --border-color: rgba(212, 175, 55, 0.18);
            --success: #0fb56d;
            --warning: #ffb347;
            --error: #f07a63;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: radial-gradient(circle at top, rgba(212, 175, 55, 0.12), transparent 45%), var(--primary-bg);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }

        .app-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1rem;
        }

        /* Header Styles */
        .header {
            background: linear-gradient(135deg, rgba(37, 29, 11, 0.85) 0%, rgba(18, 18, 18, 0.95) 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-bronze) 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.5rem;
            color: #080808;
            box-shadow: 0 4px 18px rgba(212, 175, 55, 0.35);
        }

        .brand-info h1 {
            font-size: 1.6rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-gold), var(--accent-bronze));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .brand-info p {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        /* Loading and Error States */
        .loading-state, .error-state {
            text-align: center;
            padding: 3rem 2rem;
            background: var(--secondary-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin: 2rem 0;
        }

        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--accent-gold);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-icon {
            font-size: 3rem;
            color: var(--error);
            margin-bottom: 1rem;
        }

        /* Button Styles */
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-gold) 0%, #FFA500 100%);
            color: var(--primary-bg);
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
        }

        .btn-secondary {
            background: var(--secondary-bg);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }

        .btn-secondary:hover {
            background: #252A47;
            border-color: var(--accent-bronze);
        }

        /* Upload Section */
        .upload-section {
            background: var(--secondary-bg);
            padding: 2rem;
            border-radius: 12px;
            border: 2px dashed var(--border-color);
            text-align: center;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }

        .upload-section:hover {
            border-color: var(--accent-gold);
            background: #1F2440;
        }

        .upload-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: var(--accent-gold);
        }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid var(--border-color);
        }

        .tab {
            padding: 1rem 2rem;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            position: relative;
            transition: all 0.3s ease;
        }

        .tab:hover {
            color: var(--text-primary);
        }

        .tab.active {
            color: var(--accent-gold);
        }

        .tab.active::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-gold), var(--accent-bronze));
        }

        /* Table Styles */
        .table-container {
            background: var(--secondary-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }

        .table-controls {
            padding: 1rem 1.5rem;
            background: #1F2440;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }

        .search-input {
            flex: 1;
            min-width: 200px;
            padding: 0.75rem 1rem;
            background: var(--primary-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 1rem;
        }

        .search-input:focus {
            outline: none;
            border-color: rgba(212, 175, 55, 0.35);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background: #1F2440;
            font-weight: 600;
            color: var(--accent-gold);
            cursor: pointer;
            user-select: none;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        th:hover {
            background: #252A47;
        }

        tr:hover {
            background: rgba(74, 158, 255, 0.05);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: var(--secondary-bg);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: var(--accent-gold);
            box-shadow: 0 4px 20px rgba(255, 215, 0, 0.2);
        }

        .stat-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-gold), var(--accent-bronze));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Charts */
        .chart-container {
            background: var(--secondary-bg);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }

        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }

        /* Debug Panel */
        .debug-panel {
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            max-width: 300px;
            font-size: 0.85rem;
            display: none;
        }

        .debug-panel.show {
            display: block;
        }

        .debug-item {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
        }

        .debug-item:last-child {
            border-bottom: none;
        }

        .debug-status {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }

        .debug-status.ok {
            background: var(--success);
        }

        .debug-status.error {
            background: var(--error);
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
            }

            .tabs {
                flex-direction: column;
            }

            .tab {
                border-bottom: 1px solid var(--border-color);
            }

            .stat-card {
                text-align: center;
            }

            table {
                font-size: 0.9rem;
            }

            th, td {
                padding: 0.75rem 0.5rem;
            }
        }
    </style>

    <!-- Error Tracking Script -->
    <script>
        // Global error tracking
        window.scriptErrors = [];
        window.jsErrors = [];
        
        function handleScriptError(scriptName) {
            window.scriptErrors.push(scriptName);
            console.error(`Failed to load ${scriptName}`);
        }

        window.addEventListener('error', function(e) {
            window.jsErrors.push({
                message: e.message,
                source: e.filename,
                line: e.lineno,
                col: e.colno
            });
            console.error('JavaScript Error:', e);
        });

        // Log when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            console.log('✅ DOM Ready');
            console.log('React available:', typeof React !== 'undefined');
            console.log('ReactDOM available:', typeof ReactDOM !== 'undefined');
            console.log('Babel available:', typeof Babel !== 'undefined');
            console.log('Recharts available:', typeof Recharts !== 'undefined');
        });
    </script>
</head>
<body>
    <!-- Fallback Loading UI -->
    <div id="root">
        <div class="app-container">
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <h2>Loading Eleven Views CSV Intelligence...</h2>
                <p style="margin-top: 1rem; color: var(--text-secondary);">
                    Initializing components and loading dependencies...
                </p>
            </div>
        </div>
    </div>

    <!-- Debug Panel -->
    <div id="debug-panel" class="debug-panel">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Debug Info</div>
        <div id="debug-content"></div>
    </div>

    <!-- React Application -->
    <!-- Keep Babel for JSX processing, but ensure it's ready -->
    <script type="text/babel" data-presets="react">
        // Error Boundary Component
        class ErrorBoundary extends React.Component {
            constructor(props) {
                super(props);
                this.state = { hasError: false, error: null, errorInfo: null };
            }

            static getDerivedStateFromError(error) {
                return { hasError: true };
            }

            componentDidCatch(error, errorInfo) {
                console.error('React Error Boundary:', error, errorInfo);
                this.setState({ error, errorInfo });
            }

            render() {
                if (this.state.hasError) {
                    return (
                        <div className="app-container">
                            <div className="error-state">
                                <div className="error-icon">⚠️</div>
                                <h2>Something went wrong</h2>
                                <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>
                                    {this.state.error && this.state.error.toString()}
                                </p>
                                <button 
                                    className="btn btn-primary" 
                                    onClick={() => window.location.reload()}
                                    style={{ marginTop: '1.5rem' }}
                                >
                                    🔄 Reload Page
                                </button>
                            </div>
                        </div>
                    );
                }

                return this.props.children;
            }
        }

        // Main CSV Report Viewer Component
        const CSVReportViewer = () => {
            const [data, setData] = React.useState(null);
            const [activeTab, setActiveTab] = React.useState('data');
            const [searchTerm, setSearchTerm] = React.useState('');
            const [sortConfig, setSortConfig] = React.useState({ key: null, direction: 'asc' });
            const [showDebug, setShowDebug] = React.useState(false);

            // FIXED: CSV parsing with correct regex
            const parseCSV = (csvText) => {
                try {
                    console.log('📄 Parsing CSV...');
                    
                    // FIXED: Single backslash for proper regex
                    const lines = csvText.trim().split(/\r?\n/);
                    
                    if (lines.length === 0) {
                        throw new Error('CSV file is empty');
                    }

                    const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
                    console.log('📊 Headers:', headers);

                    const rows = [];
                    for (let i = 1; i < lines.length; i++) {
                        if (lines[i].trim()) {
                            const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
                            const row = {};
                            headers.forEach((header, index) => {
                                row[header] = values[index] || '';
                            });
                            rows.push(row);
                        }
                    }

                    console.log(`✅ Parsed ${rows.length} rows`);
                    return { headers, rows };
                } catch (error) {
                    console.error('❌ CSV Parsing Error:', error);
                    throw error;
                }
            };

            const handleFileUpload = (event) => {
                const file = event.target.files[0];
                if (!file) return;

                console.log('📁 File selected:', file.name);

                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const csvData = parseCSV(e.target.result);
                        setData(csvData);
                        setActiveTab('data');
                        console.log('✅ Data loaded successfully');
                    } catch (error) {
                        alert(`Error parsing CSV: ${error.message}`);
                    }
                };
                reader.onerror = () => {
                    alert('Error reading file');
                };
                reader.readAsText(file);
            };

            const filteredAndSortedData = React.useMemo(() => {
                if (!data) return [];

                let filtered = data.rows.filter(row =>
                    Object.values(row).some(val =>
                        String(val).toLowerCase().includes(searchTerm.toLowerCase())
                    )
                );

                if (sortConfig.key) {
                    filtered.sort((a, b) => {
                        const aVal = a[sortConfig.key];
                        const bVal = b[sortConfig.key];
                        
                        const aNum = parseFloat(aVal);
                        const bNum = parseFloat(bVal);
                        
                        if (!isNaN(aNum) && !isNaN(bNum)) {
                            return sortConfig.direction === 'asc' ? aNum - bNum : bNum - aNum;
                        }
                        
                        return sortConfig.direction === 'asc'
                            ? String(aVal).localeCompare(String(bVal))
                            : String(bVal).localeCompare(String(aVal));
                    });
                }

                return filtered;
            }, [data, searchTerm, sortConfig]);

            const handleSort = (key) => {
                setSortConfig(prev => ({
                    key,
                    direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
                }));
            };

            const calculateStats = () => {
                if (!data) return null;

                const stats = {
                    totalRows: data.rows.length,
                    totalColumns: data.headers.length,
                    numericColumns: 0,
                    textColumns: 0
                };

                data.headers.forEach(header => {
                    const values = data.rows.map(row => row[header]);
                    const numericValues = values.filter(v => !isNaN(parseFloat(v)));
                    if (numericValues.length > values.length * 0.5) {
                        stats.numericColumns++;
                    } else {
                        stats.textColumns++;
                    }
                });

                return stats;
            };

            const getNumericColumns = () => {
                if (!data) return [];
                
                return data.headers.filter(header => {
                    const values = data.rows.map(row => row[header]);
                    const numericValues = values.filter(v => !isNaN(parseFloat(v)) && v !== '');
                    return numericValues.length > values.length * 0.5;
                });
            };

            const renderUploadSection = () => (
                <div className="upload-section">
                    <div className="upload-icon">📊</div>
                    <h2 style={{ marginBottom: '1rem' }}>Upload CSV Report</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                        Upload your CSV file to analyze data with advanced visualizations
                    </p>
                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                        id="csv-upload"
                    />
                    <label htmlFor="csv-upload" className="btn btn-primary">
                        📁 Choose CSV File
                    </label>
                </div>
            );

            const renderDataTab = () => {
                if (!data) return renderUploadSection();

                return (
                    <div className="table-container">
                        <div className="table-controls">
                            <input
                                type="text"
                                placeholder="🔍 Search data..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="search-input"
                            />
                            <button className="btn btn-secondary" onClick={() => setData(null)}>
                                🔄 Upload New File
                            </button>
                        </div>
                        <div style={{ overflowX: 'auto', maxHeight: '600px' }}>
                            <table>
                                <thead>
                                    <tr>
                                        {data.headers.map(header => (
                                            <th key={header} onClick={() => handleSort(header)}>
                                                {header}
                                                {sortConfig.key === header && (
                                                    <span style={{ marginLeft: '0.5rem' }}>
                                                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                                                    </span>
                                                )}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredAndSortedData.map((row, idx) => (
                                        <tr key={idx}>
                                            {data.headers.map(header => (
                                                <td key={header}>{row[header]}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div style={{ padding: '1rem 1.5rem', background: '#1F2440', textAlign: 'center', color: 'var(--text-secondary)' }}>
                            Showing {filteredAndSortedData.length} of {data.rows.length} rows
                        </div>
                    </div>
                );
            };

            const renderAnalyticsTab = () => {
                if (!data) return renderUploadSection();

                const stats = calculateStats();
                const numericColumns = getNumericColumns();

                return (
                    <div>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-label">Total Rows</div>
                                <div className="stat-value">{stats.totalRows}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Total Columns</div>
                                <div className="stat-value">{stats.totalColumns}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Numeric Columns</div>
                                <div className="stat-value">{stats.numericColumns}</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-label">Text Columns</div>
                                <div className="stat-value">{stats.textColumns}</div>
                            </div>
                        </div>

                        {numericColumns.length > 0 && (
                            <div className="chart-container">
                                <div className="chart-title">📊 Numeric Data Distribution</div>
                                <div style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                                    Showing first numeric column: {numericColumns[0]}
                                </div>
                                {typeof Recharts !== 'undefined' ? (
                                    <Recharts.ResponsiveContainer width="100%" height={300}>
                                        <Recharts.BarChart data={data.rows.slice(0, 20)}>
                                            <Recharts.CartesianGrid strokeDasharray="3 3" stroke="rgba(212,175,55,0.2)" />
                                            <Recharts.XAxis dataKey={data.headers[0]} stroke="rgba(245,241,229,0.6)" />
                                            <Recharts.YAxis stroke="rgba(245,241,229,0.6)" />
                                            <Recharts.Tooltip 
                                                contentStyle={{ background: '#161616', border: '1px solid rgba(212,175,55,0.25)' }}
                                            />
                                            <Recharts.Bar dataKey={numericColumns[0]} fill="#d4af37" />
                                        </Recharts.BarChart>
                                    </Recharts.ResponsiveContainer>
                                ) : (
                                    <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                        Chart library not available. Please check console for errors.
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            };

            return (
                <ErrorBoundary>
                    <div className="app-container">
                        <header className="header">
                            <div className="header-content">
                                <div className="logo-section">
                                    <div className="logo">EV</div>
                                    <div className="brand-info">
                                        <h1>Eleven Views</h1>
                                        <p>Sports Partnerships Intelligence Studio</p>
                                    </div>
                                </div>
                                <button 
                                    className="btn btn-secondary"
                                    onClick={() => setShowDebug(!showDebug)}
                                >
                                    🐛 Debug
                                </button>
                            </div>
                        </header>

                        {data && (
                            <div className="tabs">
                                <button
                                    className={`tab ${activeTab === 'data' ? 'active' : ''}`}
                                    onClick={() => setActiveTab('data')}
                                >
                                    📊 Data View
                                </button>
                                <button
                                    className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
                                    onClick={() => setActiveTab('analytics')}
                                >
                                    📈 Analytics
                                </button>
                            </div>
                        )}

                        {activeTab === 'data' && renderDataTab()}
                        {activeTab === 'analytics' && renderAnalyticsTab()}

                        {/* Debug Info */}
                        {showDebug && (
                            <div style={{ marginTop: '2rem', padding: '1rem', background: 'var(--secondary-bg)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                <h3>Debug Information</h3>
                                <div style={{ marginTop: '1rem', fontSize: '0.9rem', fontFamily: 'monospace' }}>
                                    <div>✅ React: {typeof React !== 'undefined' ? 'Loaded' : '❌ Failed'}</div>
                                    <div>✅ ReactDOM: {typeof ReactDOM !== 'undefined' ? 'Loaded' : '❌ Failed'}</div>
                                    <div>✅ Babel: {typeof Babel !== 'undefined' ? 'Loaded' : '❌ Failed'}</div>
                                    <div>✅ Recharts: {typeof Recharts !== 'undefined' ? 'Loaded' : '❌ Failed'}</div>
                                    <div style={{ marginTop: '1rem' }}>
                                        Data Loaded: {data ? '✅ Yes' : '❌ No'}
                                    </div>
                                    {data && (
                                        <>
                                            <div>Rows: {data.rows.length}</div>
                                            <div>Columns: {data.headers.length}</div>
                                        </>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </ErrorBoundary>
            );
        };

        // Mount React App with error handling
        function mountReactApp() {
            try {
                console.log('🚀 Attempting to mount React application...');
                console.log('React available:', typeof React !== 'undefined');
                console.log('ReactDOM available:', typeof ReactDOM !== 'undefined');
                console.log('Babel available:', typeof Babel !== 'undefined');
                console.log('Babel loaded flag:', window.babelLoaded);
                
                if (typeof React === 'undefined') {
                    throw new Error('React library not loaded. Check network connection or browser console.');
                }
                if (typeof ReactDOM === 'undefined') {
                    throw new Error('ReactDOM library not loaded. Check network connection or browser console.');
                }
                if (typeof Babel === 'undefined' && !window.babelLoaded) {
                    console.warn('⚠️ Babel not loaded yet, but continuing...');
                }

                const root = document.getElementById('root');
                if (!root) {
                    throw new Error('Root element not found');
                }

                // Wait a bit more for Babel to be ready if needed
                if (typeof Babel !== 'undefined' && Babel.transform) {
                    console.log('✅ Babel is ready to transform JSX');
                }

                // Use React.createElement to avoid Babel JSX processing issues
                // This is more reliable than waiting for Babel to process JSX
                if (ReactDOM.createRoot) {
                    const reactRoot = ReactDOM.createRoot(root);
                    reactRoot.render(React.createElement(CSVReportViewer));
                    console.log('✅ React application mounted successfully (React 18)');
                } else {
                    ReactDOM.render(React.createElement(CSVReportViewer), root);
                    console.log('✅ React application mounted successfully (React 17)');
                }
            } catch (error) {
                console.error('❌ Failed to mount React application:', error);
                console.error('Error stack:', error.stack);
                const root = document.getElementById('root');
                if (root) {
                    root.innerHTML = `
                        <div class="app-container">
                            <div class="error-state">
                                <div class="error-icon">⚠️</div>
                                <h2>Failed to Initialize</h2>
                                <p style="margin-top: 1rem; color: var(--text-secondary);">
                                    ${error.message}
                                </p>
                                <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                                    Error: ${error.toString()}
                                </p>
                                <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                                    Please check the browser console (F12) for more details.
                                </p>
                                <button 
                                    class="btn btn-primary" 
                                    onclick="window.location.reload()"
                                    style="margin-top: 1.5rem;"
                                >
                                    🔄 Reload Page
                                </button>
                            </div>
                        </div>
                    `;
                }
            }
        }
        
        // Wait for Babel to be ready
        function waitForBabel(callback, maxAttempts = 50) {
            let attempts = 0;
            const checkBabel = setInterval(function() {
                attempts++;
                if (typeof Babel !== 'undefined' && Babel.transform) {
                    clearInterval(checkBabel);
                    console.log('✅ Babel is ready after', attempts * 100, 'ms');
                    callback();
                } else if (attempts >= maxAttempts) {
                    clearInterval(checkBabel);
                    console.warn('⚠️ Babel not loaded after 5 seconds, attempting mount anyway...');
                    callback();
                }
            }, 100);
        }
        
        // Wait for all scripts to load
        function initApp() {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('📄 DOM Content Loaded');
                    waitForBabel(function() {
                        setTimeout(mountReactApp, 200);
                    });
                });
            } else {
                console.log('📄 DOM already loaded');
                waitForBabel(function() {
                    setTimeout(mountReactApp, 200);
                });
            }
        }
        
        // Also try mounting after window load
        window.addEventListener('load', function() {
            console.log('🌐 Window loaded');
            setTimeout(function() {
                const root = document.getElementById('root');
                if (root && root.querySelector('.loading-state')) {
                    console.log('⏳ Still showing loading state, attempting mount...');
                    waitForBabel(mountReactApp, 20);
                }
            }, 2000);
        });
        
        // Start initialization
        initApp();
    </script>
</body>
</html>{% endraw %}
"""

def create_csv_viewer_route(app):
    """Add CSV viewer route to Flask app"""
    
    @app.route('/csv-viewer')
    @app.route('/reports')
    def csv_viewer():
        """Serve the CSV viewer page"""
        return render_template_string(CSV_VIEWER_HTML)
    
    return app

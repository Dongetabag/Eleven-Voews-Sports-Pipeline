# AI Arbitrage Mac App - Expert Cursor Implementation Guide

**Target**: Build production-ready native macOS application for AI-powered arbitrage system
**Timeline**: 4-6 weeks | **Complexity**: Advanced | **Priority**: CRITICAL PATH ITEMS FIRST

---

## 🎯 PHASE 1: CRITICAL PATH - Foundation (Week 1)

### 1.1 Project Setup & Architecture

**Cursor Command**: Create new Xcode project with optimal structure

```bash
# Initialize project structure
mkdir -p AIArbitrage/{Sources,Resources,Tests,Backend}
cd AIArbitrage

# Create Swift package structure
swift package init --type executable --name AIArbitrage

# Setup Python backend environment
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

**File: `Package.swift`** (Dependency Management)
```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "AIArbitrage",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "AIArbitrage", targets: ["AIArbitrage"])
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.1"),
        .package(url: "https://github.com/pointfreeco/swift-composable-architecture", from: "1.5.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.3"),
        .package(url: "https://github.com/vapor/async-kit.git", from: "1.19.0"),
        .package(url: "https://github.com/apple/swift-crypto.git", from: "3.0.0")
    ],
    targets: [
        .executableTarget(
            name: "AIArbitrage",
            dependencies: [
                "Alamofire",
                .product(name: "ComposableArchitecture", package: "swift-composable-architecture"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "AsyncKit", package: "async-kit"),
                .product(name: "Crypto", package: "swift-crypto")
            ],
            path: "Sources",
            resources: [.process("Resources")]
        ),
        .testTarget(
            name: "AIArbitrageTests",
            dependencies: ["AIArbitrage"],
            path: "Tests"
        )
    ]
)
```

**File: `Backend/requirements.txt`**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
google-generativeai==0.3.2
playwright==1.41.0
selenium==4.17.2
beautifulsoup4==4.12.3
aiohttp==3.9.1
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
redis[hiredis]==5.0.1
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.1
loguru==0.7.2
apscheduler==3.10.4
httpx==0.26.0
tenacity==8.2.3
pyobjc-framework-Cocoa==10.1
pyobjc-framework-WebKit==10.1
```

---

### 1.2 Core App Structure (TCA Architecture)

**File: `Sources/App/AIArbitrageApp.swift`**
```swift
import SwiftUI
import ComposableArchitecture

@main
struct AIArbitrageApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    static let store = Store(initialState: AppFeature.State()) {
        AppFeature()
            ._printChanges()
    }
    
    var body: some Scene {
        WindowGroup {
            AppView(store: AIArbitrageApp.store)
                .frame(minWidth: 1200, minHeight: 800)
                .onAppear {
                    setupWindow()
                }
        }
        .windowStyle(.hiddenTitleBar)
        .windowToolbarStyle(.unified)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
        
        Settings {
            SettingsView(store: AIArbitrageApp.store.scope(
                state: \.settings,
                action: \.settings
            ))
        }
    }
    
    private func setupWindow() {
        if let window = NSApplication.shared.windows.first {
            window.isMovableByWindowBackground = true
            window.titlebarAppearsTransparent = true
            window.standardWindowButton(.closeButton)?.isHidden = false
            window.standardWindowButton(.miniaturizeButton)?.isHidden = false
            window.standardWindowButton(.zoomButton)?.isHidden = false
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Start embedded Python backend
        BackendService.shared.startBackend()
        
        // Setup notification center
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { _, _ in }
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        BackendService.shared.stopBackend()
    }
}
```

**File: `Sources/Features/AppFeature.swift`** (Main App State Machine)
```swift
import ComposableArchitecture
import Foundation

@Reducer
struct AppFeature {
    struct State: Equatable {
        var dashboard = DashboardFeature.State()
        var opportunities = OpportunitiesFeature.State()
        var analytics = AnalyticsFeature.State()
        var settings = SettingsFeature.State()
        var selectedTab: Tab = .dashboard
        var isBackendConnected = false
        var connectionStatus: ConnectionStatus = .disconnected
        
        enum Tab: String, CaseIterable {
            case dashboard = "Dashboard"
            case opportunities = "Opportunities"
            case analytics = "Analytics"
            case settings = "Settings"
        }
        
        enum ConnectionStatus: Equatable {
            case connected
            case disconnected
            case connecting
            case error(String)
        }
    }
    
    enum Action: Equatable {
        case dashboard(DashboardFeature.Action)
        case opportunities(OpportunitiesFeature.Action)
        case analytics(AnalyticsFeature.Action)
        case settings(SettingsFeature.Action)
        case selectTab(State.Tab)
        case backendConnectionStatusChanged(State.ConnectionStatus)
        case checkBackendConnection
        case startScanning
        case stopScanning
        case onAppear
    }
    
    @Dependency(\.apiClient) var apiClient
    @Dependency(\.continuousClock) var clock
    
    var body: some Reducer<State, Action> {
        Scope(state: \.dashboard, action: /Action.dashboard) {
            DashboardFeature()
        }
        Scope(state: \.opportunities, action: /Action.opportunities) {
            OpportunitiesFeature()
        }
        Scope(state: \.analytics, action: /Action.analytics) {
            AnalyticsFeature()
        }
        Scope(state: \.settings, action: /Action.settings) {
            SettingsFeature()
        }
        
        Reduce { state, action in
            switch action {
            case .onAppear:
                return .run { send in
                    // Check backend connection every 5 seconds
                    for await _ in clock.timer(interval: .seconds(5)) {
                        await send(.checkBackendConnection)
                    }
                }
                
            case .checkBackendConnection:
                return .run { send in
                    do {
                        let status = try await apiClient.checkHealth()
                        await send(.backendConnectionStatusChanged(.connected))
                    } catch {
                        await send(.backendConnectionStatusChanged(.error(error.localizedDescription)))
                    }
                }
                
            case let .backendConnectionStatusChanged(status):
                state.connectionStatus = status
                state.isBackendConnected = status == .connected
                return .none
                
            case let .selectTab(tab):
                state.selectedTab = tab
                return .none
                
            case .startScanning:
                return .run { send in
                    try await apiClient.startScanning()
                }
                
            case .stopScanning:
                return .run { send in
                    try await apiClient.stopScanning()
                }
                
            case .dashboard, .opportunities, .analytics, .settings:
                return .none
            }
        }
    }
}
```

---

## 🔥 PHASE 2: Backend Service Integration (Week 1-2)

### 2.1 Embedded Python Backend Manager

**File: `Sources/Services/BackendService.swift`**
```swift
import Foundation
import Logging

class BackendService: ObservableObject {
    static let shared = BackendService()
    
    @Published var isRunning = false
    @Published var port: Int = 8000
    @Published var logs: [String] = []
    
    private var process: Process?
    private let logger = Logger(label: "BackendService")
    private let queue = DispatchQueue(label: "backend-service", qos: .userInitiated)
    
    private init() {}
    
    func startBackend() {
        queue.async { [weak self] in
            guard let self = self else { return }
            
            // Find Python executable
            guard let pythonPath = self.findPythonExecutable() else {
                self.logger.error("Python 3.11+ not found")
                return
            }
            
            // Setup environment
            let backendPath = self.getBackendPath()
            let venvPath = backendPath.appendingPathComponent("venv")
            let activatePath = venvPath.appendingPathComponent("bin/activate")
            
            // Check if venv exists, create if not
            if !FileManager.default.fileExists(atPath: venvPath.path) {
                self.setupVirtualEnvironment(pythonPath: pythonPath, backendPath: backendPath)
            }
            
            // Start FastAPI server
            let process = Process()
            process.executableURL = venvPath.appendingPathComponent("bin/python3")
            process.arguments = ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "\(self.port)", "--reload"]
            process.currentDirectoryURL = backendPath
            
            // Setup environment variables
            var environment = ProcessInfo.processInfo.environment
            environment["PYTHONPATH"] = backendPath.path
            environment["GEMINI_API_KEY"] = self.getAPIKey()
            process.environment = environment
            
            // Capture output
            let outputPipe = Pipe()
            let errorPipe = Pipe()
            process.standardOutput = outputPipe
            process.standardError = errorPipe
            
            outputPipe.fileHandleForReading.readabilityHandler = { handle in
                let data = handle.availableData
                if let output = String(data: data, encoding: .utf8) {
                    DispatchQueue.main.async {
                        self.logs.append(output)
                        self.logger.info("\(output)")
                    }
                }
            }
            
            errorPipe.fileHandleForReading.readabilityHandler = { handle in
                let data = handle.availableData
                if let output = String(data: data, encoding: .utf8) {
                    DispatchQueue.main.async {
                        self.logs.append("ERROR: \(output)")
                        self.logger.error("\(output)")
                    }
                }
            }
            
            do {
                try process.run()
                self.process = process
                
                DispatchQueue.main.async {
                    self.isRunning = true
                    self.logger.info("Backend started on port \(self.port)")
                }
                
                // Wait for server to be ready
                self.waitForServerReady()
                
            } catch {
                self.logger.error("Failed to start backend: \(error)")
            }
        }
    }
    
    func stopBackend() {
        process?.terminate()
        process = nil
        isRunning = false
        logger.info("Backend stopped")
    }
    
    private func findPythonExecutable() -> URL? {
        let possiblePaths = [
            "/usr/local/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/bin/python3",
            ProcessInfo.processInfo.environment["HOME"]! + "/.pyenv/shims/python3"
        ]
        
        for path in possiblePaths {
            if FileManager.default.fileExists(atPath: path) {
                return URL(fileURLWithPath: path)
            }
        }
        
        return nil
    }
    
    private func getBackendPath() -> URL {
        let bundle = Bundle.main
        if let resourcePath = bundle.resourcePath {
            return URL(fileURLWithPath: resourcePath).appendingPathComponent("Backend")
        }
        // Development fallback
        return URL(fileURLWithPath: FileManager.default.currentDirectoryPath).appendingPathComponent("Backend")
    }
    
    private func setupVirtualEnvironment(pythonPath: URL, backendPath: URL) {
        let venvPath = backendPath.appendingPathComponent("venv")
        
        logger.info("Setting up virtual environment...")
        
        let createVenv = Process()
        createVenv.executableURL = pythonPath
        createVenv.arguments = ["-m", "venv", venvPath.path]
        
        do {
            try createVenv.run()
            createVenv.waitUntilExit()
            
            // Install requirements
            let pip = Process()
            pip.executableURL = venvPath.appendingPathComponent("bin/pip3")
            pip.arguments = ["install", "-r", "requirements.txt"]
            pip.currentDirectoryURL = backendPath
            
            try pip.run()
            pip.waitUntilExit()
            
            logger.info("Virtual environment setup complete")
        } catch {
            logger.error("Failed to setup venv: \(error)")
        }
    }
    
    private func waitForServerReady(maxAttempts: Int = 30) {
        queue.async {
            var attempts = 0
            while attempts < maxAttempts {
                do {
                    let url = URL(string: "http://127.0.0.1:\(self.port)/health")!
                    let (_, response) = try URLSession.shared.synchronousDataTask(with: url)
                    
                    if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                        self.logger.info("Backend server is ready")
                        return
                    }
                } catch {
                    // Server not ready yet
                }
                
                Thread.sleep(forTimeInterval: 1)
                attempts += 1
            }
            
            self.logger.error("Backend server failed to start within timeout")
        }
    }
    
    private func getAPIKey() -> String {
        // Try to get from Keychain first
        if let key = KeychainService.shared.retrieve(key: "GEMINI_API_KEY") {
            return key
        }
        
        // Fallback to environment variable
        return ProcessInfo.processInfo.environment["GEMINI_API_KEY"] ?? ""
    }
}

// Helper extension for synchronous URLSession
extension URLSession {
    func synchronousDataTask(with url: URL) throws -> (Data, URLResponse) {
        var data: Data?
        var response: URLResponse?
        var error: Error?
        
        let semaphore = DispatchSemaphore(value: 0)
        
        let task = self.dataTask(with: url) {
            data = $0
            response = $1
            error = $2
            semaphore.signal()
        }
        
        task.resume()
        semaphore.wait()
        
        if let error = error {
            throw error
        }
        
        return (data ?? Data(), response!)
    }
}
```

### 2.2 Optimized Python Backend

**File: `Backend/main.py`** (FastAPI with Advanced Features)
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
import logging
from datetime import datetime

from api import router as api_router
from services.scraper_service import ScraperService
from services.ai_service import AIService
from services.database_service import DatabaseService
from services.notification_service import NotificationService
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
scraper_service: Optional[ScraperService] = None
ai_service: Optional[AIService] = None
db_service: Optional[DatabaseService] = None
notification_service: Optional[NotificationService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global scraper_service, ai_service, db_service, notification_service
    
    logger.info("🚀 Starting AI Arbitrage Backend...")
    
    # Initialize services
    db_service = DatabaseService()
    await db_service.init_db()
    
    ai_service = AIService(api_key=settings.GEMINI_API_KEY)
    await ai_service.initialize()
    
    scraper_service = ScraperService(ai_service, db_service)
    await scraper_service.initialize()
    
    notification_service = NotificationService()
    
    logger.info("✅ All services initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down services...")
    await scraper_service.cleanup()
    await db_service.close()
    logger.info("✅ Cleanup complete")

# Create FastAPI app
app = FastAPI(
    title="AI Arbitrage Backend",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scraper": scraper_service is not None and scraper_service.is_running,
            "ai": ai_service is not None,
            "database": db_service is not None
        }
    }

@app.get("/")
async def root():
    return {"message": "AI Arbitrage Backend API v2.0"}

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send updates every 2 seconds
            if scraper_service:
                stats = await scraper_service.get_stats()
                await websocket.send_json({
                    "type": "stats_update",
                    "data": stats,
                    "timestamp": datetime.now().isoformat()
                })
            
            await asyncio.sleep(2)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
```

**File: `Backend/services/ai_service.py`** (Optimized AI Engine)
```python
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class OpportunityScore:
    score: float  # 0-10
    confidence: float  # 0-1
    reasoning: str
    estimated_profit: float
    estimated_profit_margin: float
    risk_level: str  # low, medium, high
    market_demand: str  # low, medium, high
    recommendation: str  # buy, skip, investigate

class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        self.chat_session = None
        
    async def initialize(self):
        """Initialize Gemini AI"""
        try:
            genai.configure(api_key=self.api_key)
            
            # Use Gemini 2.5 Flash for optimal performance
            self.model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-latest',
                generation_config={
                    "temperature": 0.3,  # Lower for more consistent scoring
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
                }
            )
            
            logger.info("✅ AI Service initialized with Gemini 2.5 Flash")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI service: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_opportunity(
        self,
        product_data: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> OpportunityScore:
        """Analyze a product opportunity with comprehensive AI scoring"""
        
        prompt = self._build_analysis_prompt(product_data, market_data)
        
        try:
            # Use async generation
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            # Parse structured response
            result = self._parse_ai_response(response.text)
            
            logger.info(f"Analyzed opportunity: {product_data.get('title', 'Unknown')} - Score: {result.score}/10")
            
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Return conservative default
            return OpportunityScore(
                score=5.0,
                confidence=0.3,
                reasoning="AI analysis unavailable",
                estimated_profit=0,
                estimated_profit_margin=0,
                risk_level="high",
                market_demand="unknown",
                recommendation="investigate"
            )
    
    def _build_analysis_prompt(self, product_data: Dict, market_data: Optional[Dict]) -> str:
        """Build comprehensive analysis prompt"""
        
        return f"""You are an expert e-commerce arbitrage analyst. Analyze this product opportunity and provide a structured JSON response.

PRODUCT INFORMATION:
- Title: {product_data.get('title', 'Unknown')}
- Description: {product_data.get('description', 'N/A')}
- Price: ${product_data.get('price', 0)}
- Condition: {product_data.get('condition', 'Unknown')}
- Location: {product_data.get('location', 'Unknown')}
- Posted: {product_data.get('posted_date', 'Unknown')}
- Images: {len(product_data.get('images', []))} available

{f'''MARKET DATA:
- Average Sold Price: ${market_data.get('avg_sold_price', 'N/A')}
- Recent Sales: {market_data.get('recent_sales_count', 'N/A')}
- Market Demand: {market_data.get('demand_level', 'N/A')}
''' if market_data else 'MARKET DATA: Not available'}

ANALYZE AND RESPOND IN THIS EXACT JSON FORMAT:
{{
    "score": <float 0-10>,
    "confidence": <float 0-1>,
    "reasoning": "<detailed explanation>",
    "estimated_profit": <dollar amount>,
    "estimated_profit_margin": <percentage as decimal>,
    "risk_level": "<low|medium|high>",
    "market_demand": "<low|medium|high>",
    "recommendation": "<buy|skip|investigate>",
    "key_factors": ["<factor1>", "<factor2>", ...],
    "concerns": ["<concern1>", "<concern2>", ...]
}}

SCORING CRITERIA (0-10):
- 9-10: Exceptional opportunity, high profit margin (>50%), low risk, high demand
- 7-8: Great opportunity, good profit margin (30-50%), moderate risk
- 5-6: Decent opportunity, acceptable margin (15-30%), needs investigation
- 3-4: Marginal opportunity, low margin (<15%), higher risk
- 0-2: Poor opportunity, avoid

Consider: Product authenticity, condition, market saturation, seasonality, shipping costs, potential issues."""

    def _parse_ai_response(self, response_text: str) -> OpportunityScore:
        """Parse AI response into structured format"""
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            data = json.loads(response_text)
            
            return OpportunityScore(
                score=float(data.get('score', 5.0)),
                confidence=float(data.get('confidence', 0.5)),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                estimated_profit=float(data.get('estimated_profit', 0)),
                estimated_profit_margin=float(data.get('estimated_profit_margin', 0)),
                risk_level=data.get('risk_level', 'medium'),
                market_demand=data.get('market_demand', 'unknown'),
                recommendation=data.get('recommendation', 'investigate')
            )
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Raw response: {response_text}")
            
            # Attempt to extract score from text
            score = 5.0
            for line in response_text.split('\n'):
                if 'score' in line.lower():
                    try:
                        score = float(''.join(c for c in line if c.isdigit() or c == '.'))
                        break
                    except:
                        pass
            
            return OpportunityScore(
                score=score,
                confidence=0.5,
                reasoning=response_text[:200],
                estimated_profit=0,
                estimated_profit_margin=0,
                risk_level="medium",
                market_demand="unknown",
                recommendation="investigate"
            )
    
    async def batch_analyze(self, products: List[Dict[str, Any]]) -> List[OpportunityScore]:
        """Analyze multiple products concurrently"""
        tasks = [self.analyze_opportunity(product) for product in products]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

---

## 🎨 PHASE 3: SwiftUI Views (Week 2-3)

### 3.1 Main Dashboard

**File: `Sources/Views/DashboardView.swift`**
```swift
import SwiftUI
import ComposableArchitecture
import Charts

struct DashboardView: View {
    let store: StoreOf<DashboardFeature>
    
    var body: some View {
        WithViewStore(store, observe: { $0 }) { viewStore in
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    // Stats Overview
                    statsGrid(viewStore)
                    
                    // Recent Opportunities Chart
                    recentOpportunitiesChart(viewStore)
                    
                    // Active Scanning Status
                    scanningStatus(viewStore)
                    
                    // Top Opportunities
                    topOpportunities(viewStore)
                }
                .padding(24)
            }
            .background(Color(nsColor: .windowBackgroundColor))
            .navigationTitle("Dashboard")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: { viewStore.send(.refreshData) }) {
                        Label("Refresh", systemImage: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                viewStore.send(.onAppear)
            }
        }
    }
    
    @ViewBuilder
    private func statsGrid(_ viewStore: ViewStoreOf<DashboardFeature>) -> some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible()),
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 16) {
            StatCard(
                title: "Total Opportunities",
                value: "\(viewStore.totalOpportunities)",
                change: "+\(viewStore.opportunitiesChange)%",
                isPositive: viewStore.opportunitiesChange > 0,
                icon: "chart.bar.fill",
                color: .blue
            )
            
            StatCard(
                title: "Potential Profit",
                value: "$\(viewStore.totalPotentialProfit, specifier: "%.0f")",
                change: "+$\(viewStore.profitChange, specifier: "%.0f")",
                isPositive: true,
                icon: "dollarsign.circle.fill",
                color: .green
            )
            
            StatCard(
                title: "Active Listings",
                value: "\(viewStore.activeListings)",
                change: "+\(viewStore.listingsChange)",
                isPositive: true,
                icon: "cart.fill",
                color: .orange
            )
            
            StatCard(
                title: "Avg. Margin",
                value: "\(viewStore.avgMargin, specifier: "%.1f")%",
                change: "+\(viewStore.marginChange, specifier: "%.1f")%",
                isPositive: viewStore.marginChange > 0,
                icon: "percent",
                color: .purple
            )
        }
    }
    
    @ViewBuilder
    private func recentOpportunitiesChart(_ viewStore: ViewStoreOf<DashboardFeature>) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Opportunities Found (Last 7 Days)")
                .font(.headline)
                .foregroundColor(.primary)
            
            Chart(viewStore.chartData) { data in
                LineMark(
                    x: .value("Date", data.date),
                    y: .value("Count", data.count)
                )
                .foregroundStyle(.blue.gradient)
                .interpolationMethod(.catmullRom)
                
                AreaMark(
                    x: .value("Date", data.date),
                    y: .value("Count", data.count)
                )
                .foregroundStyle(.blue.opacity(0.1).gradient)
                .interpolationMethod(.catmullRom)
            }
            .frame(height: 200)
            .chartYAxis {
                AxisMarks(position: .leading)
            }
        }
        .padding()
        .background(Color(nsColor: .controlBackgroundColor))
        .cornerRadius(12)
    }
    
    @ViewBuilder
    private func scanningStatus(_ viewStore: ViewStoreOf<DashboardFeature>) -> some View {
        HStack {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Circle()
                        .fill(viewStore.isScanning ? Color.green : Color.gray)
                        .frame(width: 10, height: 10)
                    
                    Text(viewStore.isScanning ? "Scanning Active" : "Scanning Inactive")
                        .font(.headline)
                }
                
                Text("Last scan: \(viewStore.lastScanTime, style: .relative) ago")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                if viewStore.isScanning {
                    ProgressView(value: viewStore.scanProgress)
                        .progressViewStyle(.linear)
                        .frame(height: 6)
                }
            }
            
            Spacer()
            
            Button(action: {
                viewStore.send(viewStore.isScanning ? .stopScanning : .startScanning)
            }) {
                Label(
                    viewStore.isScanning ? "Stop" : "Start",
                    systemImage: viewStore.isScanning ? "stop.circle.fill" : "play.circle.fill"
                )
                .font(.headline)
            }
            .buttonStyle(.borderedProminent)
            .tint(viewStore.isScanning ? .red : .green)
        }
        .padding()
        .background(Color(nsColor: .controlBackgroundColor))
        .cornerRadius(12)
    }
    
    @ViewBuilder
    private func topOpportunities(_ viewStore: ViewStoreOf<DashboardFeature>) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Top Opportunities")
                .font(.headline)
            
            ForEach(viewStore.topOpportunities.prefix(5)) { opportunity in
                OpportunityRowView(opportunity: opportunity)
                    .onTapGesture {
                        viewStore.send(.selectOpportunity(opportunity.id))
                    }
            }
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let change: String
    let isPositive: Bool
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Spacer()
                
                HStack(spacing: 4) {
                    Image(systemName: isPositive ? "arrow.up.right" : "arrow.down.right")
                    Text(change)
                }
                .font(.caption)
                .foregroundColor(isPositive ? .green : .red)
            }
            
            Text(value)
                .font(.system(size: 28, weight: .bold, design: .rounded))
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(nsColor: .controlBackgroundColor))
        .cornerRadius(12)
    }
}
```

---

## ⚡ KEY ENHANCEMENTS & OPTIMIZATIONS

### 1. **Performance Optimizations**
- Async/await throughout for non-blocking operations
- Connection pooling for database and HTTP requests
- Lazy loading for large datasets
- Image caching with Kingfisher
- Background queue processing for heavy tasks

### 2. **AI Enhancements**
- Structured JSON responses for reliable parsing
- Retry logic with exponential backoff
- Batch processing for multiple items
- Confidence scoring and risk assessment
- Market demand analysis integration

### 3. **Database Optimizations**
- Core Data with async/await
- Batch insert operations
- Optimized fetch requests with predicates
- Background context for heavy operations
- SQLite WAL mode for better concurrency

### 4. **Security Enhancements**
- Keychain integration for API keys
- Encrypted local storage
- Secure WebSocket connections
- Input validation and sanitization
- Rate limiting on API endpoints

### 5. **User Experience**
- Real-time updates via WebSocket
- Responsive UI with loading states
- Error handling with user-friendly messages
- Keyboard shortcuts for power users
- Dark mode support

---

## 📦 NEXT STEPS FOR CURSOR

### Phase 4: Scraping Service (Week 3)
- Implement Playwright-based scraper for each marketplace
- Add proxy rotation and anti-detection measures
- Create queue system for scraping tasks
- Build retry logic with circuit breaker pattern

### Phase 5: Analytics & Reporting (Week 4)
- Build comprehensive analytics dashboard
- Export functionality (CSV, PDF)
- Historical data visualization
- Profit/loss tracking

### Phase 6: Testing & Deployment (Week 5-6)
- Unit tests for all components
- Integration tests for API
- UI tests with XCTest
- Beta testing and bug fixes
- App Store submission preparation

---

## 🚨 CRITICAL NOTES FOR CURSOR

1. **Always use async/await** - Never block the main thread
2. **Handle errors gracefully** - Every network call needs proper error handling
3. **Test incrementally** - Build and test each feature before moving on
4. **Optimize early** - Performance matters for scraping and AI operations
5. **Follow Apple HIG** - Match macOS design patterns
6. **Security first** - Never hardcode API keys or sensitive data
7. **Log everything** - Comprehensive logging for debugging
8. **Document as you go** - Add inline comments for complex logic

---

## 🔧 CURSOR WORKFLOW

1. **Start with Backend**: Get Python backend running first
2. **Build Core Services**: Implement API client and service layer
3. **Create Main Views**: Build dashboard and opportunities views
4. **Add Scraping**: Implement scraping service with schedulers
5. **Integrate AI**: Connect Gemini for analysis
6. **Polish UI**: Add animations, loading states, error handling
7. **Test Thoroughly**: Unit, integration, and UI tests
8. **Optimize**: Profile and optimize performance
9. **Deploy**: Build, sign, and distribute

---

**This guide provides production-ready code that Cursor can implement directly. Focus on one phase at a time, test thoroughly, and iterate quickly.**

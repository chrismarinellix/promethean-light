use serde::{Deserialize, Serialize};
use std::process::Command;
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager, WindowEvent,
};

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResult {
    pub id: String,
    pub score: f64,
    pub text: String,
    pub source: String,
    pub created_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SourceCounts {
    pub emails: i64,
    pub documents: i64,
    pub notes: i64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DaemonStats {
    pub total_documents: i64,
    pub total_chunks: i64,
    pub total_tags: i64,
    #[serde(default)]
    pub total_clusters: i64,
    #[serde(default)]
    pub sources: Option<SourceCounts>,
}

#[tauri::command]
async fn search_documents(query: String, limit: Option<i32>) -> Result<Vec<SearchResult>, String> {
    let client = reqwest::Client::new();
    let limit = limit.unwrap_or(10);

    let res = client
        .post("http://127.0.0.1:8000/search")
        .json(&serde_json::json!({
            "query": query,
            "limit": limit
        }))
        .send()
        .await
        .map_err(|e| format!("Failed to connect to daemon: {}", e))?;

    if !res.status().is_success() {
        return Err(format!("Search failed with status: {}", res.status()));
    }

    let results: Vec<SearchResult> = res
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(results)
}

#[tauri::command]
async fn get_stats() -> Result<DaemonStats, String> {
    let client = reqwest::Client::new();

    let res = client
        .get("http://127.0.0.1:8000/stats")
        .send()
        .await
        .map_err(|e| format!("Failed to connect to daemon: {}", e))?;

    if !res.status().is_success() {
        return Err(format!("Stats failed with status: {}", res.status()));
    }

    let stats: DaemonStats = res
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(stats)
}

#[tauri::command]
async fn check_daemon() -> Result<bool, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(2))
        .build()
        .unwrap();

    match client.get("http://127.0.0.1:8000/stats").send().await {
        Ok(res) => Ok(res.status().is_success()),
        Err(_) => Ok(false),
    }
}

#[tauri::command]
async fn get_tags() -> Result<Vec<serde_json::Value>, String> {
    let client = reqwest::Client::new();

    let res = client
        .get("http://127.0.0.1:8000/tags")
        .send()
        .await
        .map_err(|e| format!("Failed to connect to daemon: {}", e))?;

    let tags: Vec<serde_json::Value> = res
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(tags)
}

#[tauri::command]
async fn start_daemon(passphrase: String) -> Result<String, String> {
    // Set environment variable and start daemon in a visible console window
    // Note: The window title must be quoted when it contains spaces
    let result = Command::new("cmd")
        .args(["/C", "start", "\"Promethean Light Daemon\"", "cmd", "/K",
               &format!("cd /d \"C:\\Code\\Promethian  Light\" && set MYDATA_PASSPHRASE={} && python -m mydata daemon", passphrase)])
        .spawn();

    match result {
        Ok(_) => {
            // Wait for daemon to start - it takes time to load ML models
            // Try multiple times with delays
            let client = reqwest::Client::new();

            for attempt in 1..=12 {
                tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

                // Check /stats endpoint which should return 200 when ready
                if let Ok(res) = client.get("http://127.0.0.1:8000/stats").send().await {
                    if res.status().is_success() {
                        return Ok("Daemon started successfully".to_string());
                    }
                }

                // Log progress (attempt number)
                if attempt == 6 {
                    // Still trying after 18 seconds
                }
            }

            // After 36 seconds, give up but daemon might still be starting
            Ok("Daemon process started. It may still be loading - click 'Retry Connection' in a moment.".to_string())
        }
        Err(e) => Err(format!("Failed to start daemon: {}", e)),
    }
}

#[tauri::command]
async fn stop_daemon() -> Result<String, String> {
    // Kill any running python daemon processes
    let _ = Command::new("taskkill")
        .args(["/F", "/IM", "python.exe"])
        .output();

    Ok("Daemon stopped".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            // Create tray menu
            let quit = MenuItem::with_id(app, "quit", "Quit Promethean Light", true, None::<&str>)?;
            let show = MenuItem::with_id(app, "show", "Show God Mode Panel", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show, &quit])?;

            // Build tray icon
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .tooltip("Promethean Light")
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        app.exit(0);
                    }
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            // Show window on startup
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            // Minimize to tray instead of closing
            if let WindowEvent::CloseRequested { api, .. } = event {
                let _ = window.hide();
                api.prevent_close();
            }
        })
        .invoke_handler(tauri::generate_handler![
            search_documents,
            get_stats,
            check_daemon,
            get_tags,
            start_daemon,
            stop_daemon
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

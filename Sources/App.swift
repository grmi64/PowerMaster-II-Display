import Cocoa
import WebKit
import Darwin

final class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, WKScriptMessageHandler {
    var window: NSWindow!
    var web: WKWebView!
    var process: Process?
    var output = Data()
    var lockFD: Int32 = -1
    var shuttingDown = false
    var fullFrame: NSRect?
    var compact = false
    func applicationDidFinishLaunching(_ notification: Notification) {
        // A second launch activates the first app and never opens the USB port.
        let identifier = Bundle.main.bundleIdentifier ?? "com.grmi64.PowerMasterIIDisplay"
        if let existing = NSRunningApplication.runningApplications(withBundleIdentifier: identifier).first(where: { $0.processIdentifier != ProcessInfo.processInfo.processIdentifier }) {
            existing.activate(options: [.activateAllWindows, .activateIgnoringOtherApps])
            NSApp.terminate(nil)
            return
        }
        let lockDirectory = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent(identifier)
        try? FileManager.default.createDirectory(at: lockDirectory, withIntermediateDirectories: true)
        lockFD = Darwin.open(lockDirectory.appendingPathComponent("instance.lock").path, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR)
        guard lockFD >= 0, flock(lockFD, LOCK_EX | LOCK_NB) == 0 else { NSApp.terminate(nil); return }
        let menu = NSMenu()
        let appMenu = NSMenu()
        let about = appMenu.addItem(withTitle: "About PowerMaster II Display…", action: #selector(showAbout(_:)), keyEquivalent: "")
        about.target = self
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Quit PowerMaster II Display", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        let item = NSMenuItem(); item.submenu = appMenu; menu.addItem(item)
        NSApp.mainMenu = menu
        window = NSWindow(contentRect: NSRect(x: 0,y: 0,width: 940,height: 850), styleMask: [.titled,.closable,.miniaturizable,.resizable], backing: .buffered, defer: false)
        window.title = "PowerMaster II Display"
        window.minSize = NSSize(width: 650,height: 650)
        window.center(); window.delegate = self
        window.setFrameAutosaveName("PowerMasterMainWindow")
        ensureWindowVisible()
        NotificationCenter.default.addObserver(self, selector: #selector(recoverForScreenChange(_:)), name: NSApplication.didChangeScreenParametersNotification, object: nil)
        let config = WKWebViewConfiguration()
        config.userContentController.add(self, name: "displayWindow")
        let webData = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent(identifier)
        try? FileManager.default.createDirectory(at: webData, withIntermediateDirectories: true)
        web = WKWebView(frame: window.contentView!.bounds, configuration: config)
        web.autoresizingMask = [.width,.height]; window.contentView!.addSubview(web)
        window.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true)
        launchReader()
    }
    @objc func showAbout(_ sender: Any?) {
        let version = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "Unknown"
        let build = Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String ?? "Unknown"
        NSApp.orderFrontStandardAboutPanel(options: [
            .applicationName: "PowerMaster II Display", .applicationVersion: version, .version: "Build " + build,
            .credits: NSAttributedString(string: "Created by NY6C\nIndependent PowerMaster II meter display."),
            .init(rawValue: "Copyright"): "© 2026 NY6C"
        ])
        NSApp.activate(ignoringOtherApps: true)
    }
    func launchReader() {
        guard let resources = Bundle.main.resourceURL else { return }
        let task = Process(); task.executableURL = resources.appendingPathComponent("meter-reader/meter-reader")
        var args = ["--no-browser","--http-port","51879"]
        if CommandLine.arguments.contains("--demo") { args.append("--demo") }
        task.arguments = args
        task.environment = ProcessInfo.processInfo.environment.merging(["PYTHONDONTWRITEBYTECODE":"1","PYTHONUNBUFFERED":"1"]) { _,new in new }
        let pipe = Pipe(); task.standardOutput = pipe
        task.standardError = FileHandle.standardError
        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty else { return }
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.output.append(data)
                if let text = String(data:self.output,encoding:.utf8), let line = text.components(separatedBy:"\n").first, let range = line.range(of:"http://127.0.0.1:"), let url = URL(string:String(line[range.lowerBound...])) {
                    self.web.load(URLRequest(url:url))
                    pipe.fileHandleForReading.readabilityHandler = nil
                }
            }
        }
        task.terminationHandler = { [weak self] p in
            if p.terminationStatus != 0 {
                DispatchQueue.main.async { guard let self = self, !self.shuttingDown else { return }; self.showError("The meter reader stopped. Exit any older meter reader before opening this app. If the problem persists, check the app diagnostics.") }
            }
        }
        do { try task.run(); process = task }
        catch { showError("Could not start Python reader: \(error.localizedDescription)") }
    }
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "displayWindow", let options = message.body as? [String:Any],
              let small = options["compact"] as? Bool, let onTop = options["alwaysOnTop"] as? Bool else { return }
        window.level = onTop ? .floating : .normal
        window.title = "PowerMaster II Display" + (small ? " · Compact" : "") + (onTop ? " · On top" : "")
        if small != compact {
            if small {
                if window.frame.height >= 650 {
                    fullFrame = window.frame
                    UserDefaults.standard.set(NSStringFromRect(window.frame), forKey: "PowerMasterFullFrame")
                } else if let stored = UserDefaults.standard.string(forKey: "PowerMasterFullFrame") {
                    fullFrame = NSRectFromString(stored)
                }
                window.minSize = NSSize(width: 600, height: 340)
                window.setContentSize(NSSize(width: 700, height: 350))
            } else {
                window.minSize = NSSize(width: 650, height: 650)
                if let frame = fullFrame { window.setFrame(frame, display: true) }
                else { window.setContentSize(NSSize(width: 940, height: 850)) }
            }
            compact = small
            ensureWindowVisible()
        }
    }
    func ensureWindowVisible() {
        guard let window = window, !window.styleMask.contains(.fullScreen) else { return }
        let old = window.frame
        let frame = WindowPlacement.recover(old, screens: NSScreen.screens.map { $0.visibleFrame })
        if frame != old {
            window.minSize = NSSize(width:min(window.minSize.width,frame.width),height:min(window.minSize.height,frame.height))
            window.setFrame(frame, display:true)
        }
    }
    @objc func recoverForScreenChange(_ notification: Notification) { ensureWindowVisible() }
    func applicationDidBecomeActive(_ notification: Notification) { ensureWindowVisible() }
    func showError(_ message:String) {
        let alert=NSAlert();alert.messageText="PowerMaster II Display";alert.informativeText=message
        ensureWindowVisible()
        if let window = window, window.isVisible { alert.beginSheetModal(for:window) }
        else { alert.runModal() }
    }
    func applicationShouldHandleReopen(_ sender:NSApplication,hasVisibleWindows flag:Bool)->Bool { ensureWindowVisible();window?.makeKeyAndOrderFront(nil);return true }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender:NSApplication)->Bool { true }
    func applicationWillTerminate(_ notification:Notification) { shuttingDown = true; if let p=process,p.isRunning {p.terminationHandler = nil;p.terminate();p.waitUntilExit()} }
}
@main
struct InstrumentApplication {
    static func main() {
        let app=NSApplication.shared
        let delegate=AppDelegate()
        app.delegate=delegate
        app.setActivationPolicy(.regular)
        app.run()
    }
}

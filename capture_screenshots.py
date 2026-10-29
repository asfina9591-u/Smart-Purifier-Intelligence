import os
import time
from playwright.sync_api import sync_playwright

def run():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 920}, device_scale_factor=2)
        page = context.new_page()
        
        print("Connecting to Streamlit at http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=60000)
        
        page.wait_for_selector('[data-testid="stTab"]', timeout=30000)
        time.sleep(3)
        
        tabs = page.locator('[data-testid="stTab"]')
        
        # 1. Live Monitor
        print("Capturing 1/6: Live Monitor (default view)...")
        tabs.nth(0).click()
        time.sleep(2)
        page.screenshot(path=os.path.join(out_dir, "01_live_monitor.png"), full_page=True)
        
        # 2. Live Monitor - Safety Fail-Safe Triggered
        print("Capturing 2/6: Safety Check Triggered...")
        fault_toggle = page.get_by_text("Simulate sensor fault")
        if fault_toggle.count() > 0:
            fault_toggle.click()
            time.sleep(1.5)
            page.screenshot(path=os.path.join(out_dir, "02_safety_check_triggered.png"), full_page=True)
            fault_toggle.click()
            time.sleep(1)
            
        # 3. Why This Prediction? (SHAP Feature Importance)
        print("Capturing 3/6: Why This Prediction? (SHAP)...")
        tabs.nth(1).click()
        time.sleep(2)
        page.screenshot(path=os.path.join(out_dir, "03_why_this_prediction.png"), full_page=True)
        
        # 4. What-if Simulator (use=15 L baseline)
        print("Capturing 4/6: What-if Simulator (use=15 L)...")
        tabs.nth(2).click()
        time.sleep(2)
        page.screenshot(path=os.path.join(out_dir, "04_what_if_15L.png"), full_page=True)
        
        # 5. What-if Simulator (use=30 L high usage)
        print("Capturing 5/6: What-if Simulator (use=30 L)...")
        use_input = page.locator('input[aria-label*="Daily water use"]')
        if use_input.count() > 0:
            use_input.focus()
            for _ in range(15):
                page.keyboard.press("ArrowRight")
                time.sleep(0.04)
            time.sleep(2)
        page.screenshot(path=os.path.join(out_dir, "05_what_if_30L.png"), full_page=True)
        
        # 6. Model Validation
        print("Capturing 6/6: Model Validation Metrics...")
        tabs.nth(3).click()
        time.sleep(2)
        page.screenshot(path=os.path.join(out_dir, "06_model_validation.png"), full_page=True)
        
        browser.close()
        print("SUCCESS: All 6 screenshots successfully saved to", out_dir)

if __name__ == "__main__":
    run()

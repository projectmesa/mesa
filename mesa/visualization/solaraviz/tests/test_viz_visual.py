
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageChops
import io
import base64

def setup_webdriver():
    """Initialize webdriver for taking screenshots"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def take_component_screenshot(driver, component):
    """Take a screenshot of a specific component"""
    component.screenshot(os.path.join("tests", "screenshots", "current.png"))

def compare_screenshots(baseline_path, current_path, threshold=0.1):
    """Compare two screenshots and return difference percentage"""
    with Image.open(baseline_path) as baseline_img:
        with Image.open(current_path) as current_img:
            diff = ImageChops.difference(baseline_img, current_img)
            diff_pixels = sum(diff.convert("L").point(bool).getdata())
            total_pixels = baseline_img.size[0] * baseline_img.size[1]
            return diff_pixels / total_pixels

@pytest.fixture(scope="session")
def screenshot_dir():
    """Create directories for screenshots if they don't exist"""
    dirs = ["tests/screenshots", "tests/screenshots/baseline"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    return dirs[0]

def test_grid_visualization_appearance(example_model, screenshot_dir):
    """Test the visual appearance of the grid visualization"""
    driver = setup_webdriver()
    try:
        # Initialize the component
        model = example_model
        grid = SolaraGrid(model=model)
        
        # Take screenshot
        current_path = os.path.join(screenshot_dir, "grid_current.png")
        baseline_path = os.path.join(screenshot_dir, "baseline", "grid_baseline.png")
        
        take_component_screenshot(driver, grid)
        
        # If baseline doesn't exist, create it
        if not os.path.exists(baseline_path):
            os.rename(current_path, baseline_path)
            pytest.skip("Baseline image created")
        
        # Compare with baseline
        diff_ratio = compare_screenshots(baseline_path, current_path)
        assert diff_ratio <= 0.1, f"Visual difference of {diff_ratio:.2%} exceeds threshold"
    
    finally:
        driver.quit()

def test_chart_visualization_appearance(example_model, screenshot_dir):
    """Test the visual appearance of the chart visualization"""
    driver = setup_webdriver()
    try:
        # Initialize the component
        model = example_model
        chart = SolaraChart(model=model)
        
        # Take screenshot
        current_path = os.path.join(screenshot_dir, "chart_current.png")
        baseline_path = os.path.join(screenshot_dir, "baseline", "chart_baseline.png")
        
        take_component_screenshot(driver, chart)
        
        # If baseline doesn't exist, create it
        if not os.path.exists(baseline_path):
            os.rename(current_path, baseline_path)
            pytest.skip("Baseline image created")
        
        # Compare with baseline
        diff_ratio = compare_screenshots(baseline_path, current_path)
        assert diff_ratio <= 0.1, f"Visual difference of {diff_ratio:.2%} exceeds threshold"
    
    finally:
        driver.quit()

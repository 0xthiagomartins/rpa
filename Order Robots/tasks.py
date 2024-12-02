from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.Tables import Tables
from RPA.FileSystem import FileSystem

# libraries
file_system = FileSystem()
archive = Archive()
pdf = PDF()

@task
def order_all_robots():
    file_system.create_directory(path="output/receipts")
    browser.configure(slowmo=1000)
    open_robot_order_page()
    orders: list[dict] = load_orders()
    for order in orders:
        close_popup()
        fill_and_submit_order(order)
        collect_results(order["Order number"])
        order_another_robot()
    zip_results()

def close_popup():
    """Close the popup"""
    page = browser.page()
    page.locator(".btn-dark", has_text="OK").click()

def open_robot_order_page():
    """Open the robot order page"""
    page = browser.page()
    page.goto("https://robotsparebinindustries.com/#/robot-order")

def download_orders():
    """Download orders from CSV file"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def read_orders() -> list[dict]:
    """Read orders from CSV file"""
    table = Tables().read_table_from_csv("orders.csv", header=True, delimiters=",")
    return table

def load_orders() -> list[dict]:
    """Load orders from web CSV file to in-memory list"""
    download_orders()
    return read_orders()

def click_order_button():
    """Click the order button"""
    page = browser.page()
    page.locator("#order").click()
    if page.locator(".alert-danger").is_visible():
        click_order_button()
        
def fill_and_submit_order(order):
    """Fill and submit an order"""
    page = browser.page()
    # fill
    page.locator("#head").select_option(order["Head"])
    page.locator(f"#id-body-{order['Body']}").click()
    page.locator("xpath=//div[3]/input").fill(order["Legs"])
    page.locator("#address").fill(order["Address"])
    # submit
    click_order_button()

def save_receipt_as_pdf(id: int|str):
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(sales_results_html, f"output/receipt-{id}.pdf")

def embed_screenshot_to_pdf(id: int|str):
    """Embed Robot Screenshot to PDF"""
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path=f"output/robot-{id}.png")
    pdf.add_files_to_pdf(
        files=[
            f"output/receipt-{id}.pdf", 
            f"output/robot-{id}.png"
        ], 
        target_document=f"output/receipts/receipt-{id}.pdf"
    )

def collect_results(id: int|str):
    """Save Receipt and Robot Screenshot to PDF"""
    save_receipt_as_pdf(id)
    embed_screenshot_to_pdf(id)

def order_another_robot():
    """Click the 'Order another robot' button"""
    page = browser.page()
    page.locator("#order-another").click()

def zip_results():
    """Zip the results"""
    archive.archive_folder_with_zip(folder="output/receipts", archive_name="output/receipts.zip")

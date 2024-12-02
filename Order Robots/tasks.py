from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from RPA.PDF import PDF
from RPA.Archive import Archive
from time import sleep


lib = Archive()
pdf = PDF()

@task
def order_all_robots():
    browser.configure(slowmo=1000)
    open_robot_order_page()
    orders: list[dict] = load_orders()
    for order in orders:
        fill_and_submit_order(order)
        collect_results(order["Order number"])
        order_another_robot()
    zip_results()
    
def open_robot_order_page():
    """Open the robot order page"""
    page = browser.page()
    page.goto("https://robotsparebinindustries.com/#/robot-order")
    page.locator(".btn-dark", has_text="OK").click()

def load_orders() -> list[dict]:
    """Load orders from CSV file"""

    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", target_file="orders.csv", overwrite=True)
    sleep(10)
    excel = Files()
    excel.open_workbook("orders.csv")
    worksheet = excel.read_worksheet_as_table("orders", header=True)
    excel.close_workbook()
    return worksheet

def fill_and_submit_order(order):
    """Fill and submit an order"""
    page = browser.page()
    # fill
    page.locator("#head").select_option(order["Head"])
    page.locator(f"#id-body-{order['Body']}").click()
    page.locator("xpath=//div[3]/input").fill(order["Legs"])
    page.locator("#address").fill(order["Address"])
    # submit
    page.locator("#order").click()

def save_receipt_as_pdf(id: int|str):
    """Export the data to a pdf file"""

    page = browser.page()
    
    sales_results_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(sales_results_html, f"output/receipt-{id}.pdf")

def embed_screenshot_to_pdf(id: int|str):
    """Embed Robot Screenshot to PDF"""

    page = browser.page()
    page.locator("#robot-preview-image").wait_for().screenshot(path=f"output/robot-{id}.png")
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
    lib.archive_folder_with_zip(folder="output/receipts", archive_name="output/receipts.zip")

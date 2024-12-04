
from robocorp.tasks import task
from robocorp import workitems
import requests

@task
def consume_traffic_data():
    """
    Inhuman Insurance, Inc. Artificial Intelligence System automation.
    Consumes traffic data work items.
    """
    for item in workitems.inputs:
        traffic_data = item.payload["traffic_data"]
        valid = validate_traffic_data(traffic_data)
        if valid:
            status, return_json = post_traffic_data_to_sales_system(traffic_data)
            if status == 200:
                item.done()
            else: 
                item.fail(
                    exception_type="APPLICATION",
                    code="TRAFFIC_DATA_POST_FAILED",
                    message=return_json["message"],
                )
        else:
            item.fail(
                exception_type="BUSINESS",
                code="INVALID_TRAFFIC_DATA",
                message=f"some error message with: {traffic_data}",
            )

def validate_traffic_data(traffic_data) -> bool:
    return len(traffic_data["country"]) == 3
    
def post_traffic_data_to_sales_system(traffic_data) -> tuple[int, dict]:
    url = "https://robocorp.com/inhuman-insurance-inc/sales-system-api"
    response = requests.post(url, json=traffic_data)
    return response.status_code, response.json()

from datetime import datetime
from playerstars_domain.utils.datetime_helper import aware_utc
from playerstars_domain.wirecard import (
    ApiResponseInfo,
    NextInvoiceDate)


def process_api_response_for_errors(response_json):
    response = ApiResponseInfo.from_json(response_json['content'])
    errors = [f'{x.code} - {x.description}' for x in response.errors]
    alerts = [f'{x.code} - {x.description}' for x in response.alerts]

    all_errors = ' / '.join(errors)
    all_alerts = ' / '.join(alerts)
    return f'Errors occurred: {all_errors} | Alerts: {all_alerts}'


def mount_next_invoice_as_datetime(next_invoice: NextInvoiceDate):
    next_date = datetime(
        next_invoice.year, next_invoice.month, next_invoice.day, 0, 0, 0)
    return aware_utc(next_date)

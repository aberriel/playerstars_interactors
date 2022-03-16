from datetime import datetime
from playerstars_domain import NextInvoiceDate
from playerstars_interactors.wirecard.wirecard_utils import (
    mount_next_invoice_as_datetime,
    process_api_response_for_errors)

import pytz


def test_process_api_response_for_errors():
    response_json = {
        'content': {
            "alerts": [
                {
                    "code": "MA76",
                    "description": "Alerta ocorrido"
                }
            ],
            "errors": [
                {
                    "code": "CUS-008",
                    "description": "Erro ocorrido"
                }
            ],
            "message": "Cliente criado com sucesso"
        }
    }
    response_string = process_api_response_for_errors(response_json)
    assert response_string == 'Errors occurred: CUS-008 - Erro ocorrido | ' \
        'Alerts: MA76 - Alerta ocorrido'


def test_mount_next_invoice_as_datetime():
    next_invoice = NextInvoiceDate(2020, 1, 10)
    next_invoice_datetime = mount_next_invoice_as_datetime(next_invoice)
    assert next_invoice_datetime == \
        datetime(2020, 1, 10, 0, 0, 0, tzinfo=pytz.utc)

import zeep

PIN_CODE = "302LS8gaiI7SIii4bOdT"
TERMINAL = "98826118"


def main():
    data = {
        "LoginAccount": PIN_CODE,
        "Amount": "1000",
        "OrderId": "0",
        "CallBackUrl": ""
    }
    client = zeep.Client("https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?WSDL")
    res = client.service.SalePaymentRequest(data)
    print(res)
    pass


if __name__ == '__main__':
    main()

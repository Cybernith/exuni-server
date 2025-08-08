from sms_ir import SmsIr


SMS_IR_API_KEY = 'pdeR38lAboNkpR9AJrWgwWn2vgtbxjfccHRMt3SOeB1lD2Nq74ZnBFG3pSEF9VSe'
SMS_IR_LINE_NUMBER = '30007732903879'

class Sms:

    @staticmethod
    def send(phone, message):
        sms_ir = SmsIr(SMS_IR_API_KEY)
        response = sms_ir.send_sms(
            number=phone,
            message=message,
            linenumber=SMS_IR_LINE_NUMBER
        )
        return response

    @staticmethod
    def bulk_send(numbers, message):
        sms_ir = SmsIr(SMS_IR_API_KEY)
        response = sms_ir.send_bulk_sms(
            numbers=numbers,
            message=message,
            linenumber=SMS_IR_LINE_NUMBER
        )

        return response

    @staticmethod
    def send_like_to_like(numbers, messages):
        sms_ir = SmsIr(SMS_IR_API_KEY)
        response = sms_ir.send_like_to_like(
            numbers=numbers,
            messages=messages,
            linenumber=SMS_IR_LINE_NUMBER,
            send_date_time=None
        )

        return response


if __name__ == '__main__':
    text = ""
    print(text)

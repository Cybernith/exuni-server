from sms_ir import SmsIr

from server.settings import SMS_IR_API_KEY, SMS_IR_LINE_NUMBER


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
    def bulk_send(phones, message):
        sms_ir = SmsIr(SMS_IR_API_KEY)
        response = sms_ir.send_bulk_sms(
            number=phones,
            message=message,
            linenumber=SMS_IR_LINE_NUMBER
        )

        return response


if __name__ == '__main__':
    text = ""
    print(text)

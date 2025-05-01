from sms_ir import SmsIr

class Sms:

    @staticmethod
    def send(phone, message):
        sms_ir = SmsIr("HGJzMQfePOpaAuZZQ7qIN9yzxDpyfLFaamqkT78kshXxPevZ")
        response = sms_ir.send_sms(
            number=phone,
            message=message,
            linenumber=30002108001289
        )

        return response

    @staticmethod
    def bulk_send(phones, message):
        sms_ir = SmsIr("HGJzMQfePOpaAuZZQ7qIN9yzxDpyfLFaamqkT78kshXxPevZ")
        response = sms_ir.send_bulk_sms(
            number=phones,
            message=message,
            linenumber=30002108001289
        )

        return response


if __name__ == '__main__':
    text = ""
    print(text)

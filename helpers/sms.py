from sms_ir import SmsIr

class Sms:

    @staticmethod
    def send(phone, message):
        sms_ir = SmsIr("HGJzMQfePOpaAuZZQ7qIN9yzxDpyfLFaamqkT78kshXxPevZ")
        response = sms_ir.send_sms(
            number=phone,
            message=message,
            linenumber=3000264543
        )

        return response


if __name__ == '__main__':
    text = ""
    print(text)

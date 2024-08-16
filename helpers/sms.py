from sms_ir import SmsIr

class Sms:

    @staticmethod
    def send(phone, message):
        sms_ir = SmsIr("m8ctbveeWwbcHyqsa8FEleAmZdGrynRoaumdTsc8pbimmH1r0dOfZL4wUay1ogP9")
        response = sms_ir.send_sms(
            number=phone,
            message=message,
            linenumber=3000264543
        )

        return response


if __name__ == '__main__':
    text = ""
    print(
        Sms.send('09307468674', text)
    )

from django.core.management.base import BaseCommand

from wares.models import Unit

units = [
    {
        "code": 1611,
        "title": "لنگه"
    },
    {
        "code": 1612,
        "title": "عدل"
    },
    {
        "code": 1613,
        "title": "جعبه"
    },
    {
        "code": 1618,
        "title": "توپ"
    },
    {
        "code": 1619,
        "title": "ست"
    },
    {
        "code": 1620,
        "title": "دست"
    },
    {
        "code": 1624,
        "title": "کارتن"
    },
    {
        "code": 1627,
        "title": "عدد"
    },
    {
        "code": 1628,
        "title": "بسته"
    },
    {
        "code": 1629,
        "title": "پاکت"
    },
    {
        "code": 1631,
        "title": "دستگاه"
    },
    {
        "code": 1640,
        "title": "تخته"
    },
    {
        "code": 1641,
        "title": "رول"
    },
    {
        "code": 1642,
        "title": "طاقه"
    },
    {
        "code": 1643,
        "title": "جفت"
    },
    {
        "code": 1645,
        "title": "مترمربع"
    },
    {
        "code": 1649,
        "title": "پالت"
    },
    {
        "code": 1661,
        "title": "دوجین"
    },
    {
        "code": 1668,
        "title": "رینگ(حلقه)"
    },
    {
        "code": 1673,
        "title": "قراص"
    },
    {
        "code": 1694,
        "title": "قراصه(bundle)"
    },
    {
        "code": 1637,
        "title": "لیتر"
    },
    {
        "code": 1650,
        "title": "ساشه"
    },
    {
        "code": 1683,
        "title": "کپسول"
    },
    {
        "code": 1656,
        "title": "بندیل"
    },
    {
        "code": 1630,
        "title": "رول(حلقه)"
    },
    {
        "code": 163,
        "title": "قالب"
    },
    {
        "code": 1660,
        "title": "شانه"
    },
    {
        "code": 1647,
        "title": "مترمکعب"
    },
    {
        "code": 1689,
        "title": "ثوب"
    },
    {
        "code": 1690,
        "title": "نیم دوجین"
    },
    {
        "code": 1635,
        "title": "قرقره"
    },
    {
        "code": 164,
        "title": "کیلوگرم"
    },
    {
        "code": 1638,
        "title": "بطری"
    },
    {
        "code": 161,
        "title": "برگ"
    },
    {
        "code": 1625,
        "title": "سطل"
    },
    {
        "code": 1654,
        "title": "ورق"
    },
    {
        "code": 1646,
        "title": "شاخه"
    },
    {
        "code": 1644,
        "title": "قوطی"
    },
    {
        "code": 1617,
        "title": "جلد"
    },
    {
        "code": 162,
        "title": "تیوب"
    },
    {
        "code": 165,
        "title": "متر"
    },
    {
        "code": 1610,
        "title": "کلاف"
    },
    {
        "code": 1615,
        "title": "کیسه"
    },
    {
        "code": 1680,
        "title": "طغرا"
    },
    {
        "code": 1639,
        "title": "بشکه"
    },
    {
        "code": 1614,
        "title": "گالن"
    },
    {
        "code": 1687,
        "title": "فاقد بسته بندی"
    },
    {
        "code": 1693,
        "title": "کارتن(mastercase)"
    },
    {
        "code": 166,
        "title": "صفحه"
    },
    {
        "code": 1666,
        "title": "مخزن"
    },
    {
        "code": 1626,
        "title": "تانکر"
    },
    {
        "code": 1648,
        "title": "دبه"
    },
    {
        "code": 1684,
        "title": "سبد"
    },
    {
        "code": 169,
        "title": "تن"
    },
    {
        "code": 1651,
        "title": "بانکه"
    },
    {
        "code": 1633,
        "title": "سیلندر"
    },
    {
        "code": 1679,
        "title": "فوت مربع"
    },
    {
        "code": 168,
        "title": "حلب"
    },
    {
        "code": 1665,
        "title": "شیت"
    },
    {
        "code": 1659,
        "title": "چلیک"
    },
    {
        "code": 1636,
        "title": "جام"
    },
    {
        "code": 1622,
        "title": "گرم"
    },
    {
        "code": 1616,
        "title": "نخ"
    },
    {
        "code": 1652,
        "title": "شعله"
    },
    {
        "code": 1678,
        "title": "قیراط"
    },
    {
        "code": 16100,
        "title": "میلی لیتر"
    },
    {
        "code": 16101,
        "title": "میلی متر"
    },
    {
        "code": 16102,
        "title": "میلی گرم"
    },
    {
        "code": 16103,
        "title": "ساعت"
    },
    {
        "code": 16104,
        "title": "روز"
    },
    {
        "code": 16105,
        "title": "تن کیلومتر"
    },
    {
        "code": 1669,
        "title": "کیلووات ساعت"
    },
    {
        "code": 1676,
        "title": "نفر"
    },
    {
        "code": 16110,
        "title": "ثانیه"
    },
    {
        "code": 16111,
        "title": "دقیقه"
    },
    {
        "code": 16112,
        "title": "ماه"
    },
    {
        "code": 16113,
        "title": "سال"
    },
    {
        "code": 16114,
        "title": "قطعه"
    },
    {
        "code": 16115,
        "title": "سانتی متر"
    },
    {
        "code": 16116,
        "title": "سانتی متر مربع"
    },
    {
        "code": 1632,
        "title": "فروند"
    },
    {
        "code": 1653,
        "title": "واحد"
    },
    {
        "code": 16108,
        "title": "لیوان"
    },
    {
        "code": 16117,
        "title": "نوبت"
    },
    {
        "code": 16118,
        "title": "مگاوات ساعت"
    },
    {
        "code": 16119,
        "title": "گیگابایت بر ثانیه"
    },
    {
        "code": 1681,
        "title": "ویال"
    },
    {
        "code": 1667,
        "title": "حلقه (دیسک)"
    },
    {
        "code": 16120,
        "title": "نسخه (جلد)"
    }
]


class Command(BaseCommand):
    help = 'insert units to data base'

    def handle(self, *args, **options):
        for unit in units:
            Unit.objects.create(
                name=unit['title'],
                code=unit['code'],
            )
            print(unit['code'], ' >>>> inserted to database')



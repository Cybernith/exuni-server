from django.core.management import BaseCommand
import csv
import re

from django.db.models import Q


from products.models import Product, ProductGallery, Category, Brand
import time
import requests
from requests.exceptions import RequestException
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'insert removed product'

    @staticmethod
    def save_product_picture_from_url(product_id, image_url):
        print('image >', image_url)
        for attempt in range(3):  # حداکثر ۳ تلاش
            try:
                response = requests.get(image_url, timeout=120)
                if response.status_code == 200:
                    product = Product.objects.get(id=product_id)
                    file_name = image_url.split('/')[-1]
                    product.picture.save(file_name, ContentFile(response.content), save=True)
                    return product.picture  # موفقیت‌آمیز
                else:
                    print(f"❌ دریافت تصویر موفق نبود: {image_url} با کد {response.status_code}")
                    break
            except RequestException as e:
                print(f"❌ خطا در دانلود تصویر {image_url}: {e}")
                if attempt < 2:
                    print("⏳ ۳ ثانیه صبر و تلاش مجدد...")
                    time.sleep(3)
                else:
                    print("❌ پس از ۳ تلاش، دانلود تصویر انجام نشد.")
        return None

    @staticmethod
    def add_product_picture_gallery_from_url(product_id, image_urls):
        for image_url in image_urls:
            print('gallery >', image_url)
            for attempt in range(3):  # ۳ بار تلاش مجدد
                try:
                    response = requests.get(image_url, timeout=120)
                    if response.status_code == 200:
                        product = Product.objects.get(id=product_id)
                        gallery = ProductGallery.objects.create(product=product)
                        file_name = image_url.split('/')[-1]
                        gallery.picture.save(file_name, ContentFile(response.content), save=True)
                        break  # موفق شدیم، بیرون بزن از حلقه تلاش‌ها
                    else:
                        print(f"❌ دانلود عکس موفق نبود: {image_url} با کد {response.status_code}")
                        break
                except RequestException as e:
                    print(f"❌ خطا در دانلود {image_url}: {e}")
                    if attempt < 2:
                        print("⏳ 3 ثانیه صبر می‌کنم و دوباره تلاش می‌کنم...")
                        time.sleep(3)
                    else:
                        print("❌ پس از ۳ تلاش، این عکس رد شد.")


    def handle(self, *args, **options):
        new_products_ids = []

        with open('skus.csv', 'r', encoding='utf-8') as s:
            reader = csv.reader(s)
            skus = list(reader)

        with open('products.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row if exists
            index = 1
            counter = 1
            for row in reader:
                product_type = row[47]
                if not product_type:
                    product_type = 'variation'
                product_id = row[3].strip()
                if not Product.objects.filter(product_id=product_id).exists() and product_type != 'variation':
                    sku = skus[index][12] or None
                    name = row[0] or None
                    summary = row[4] or None
                    explanation = row[5] or None
                    status = Product.PROCESSING
                    brand = Brand.objects.filter(name__icontains=row[46]).first() or None if row[46] else None
                    categories = []
                    if row[49].split('>'):
                        cats = row[49].split('>')
                        cats = [cat.strip() for cat in cats]
                        categories = Category.objects.filter(name__in=cats)

                    try:
                        if int(row[18]) > 0:
                            inventory = int(row[18])
                        else:
                            inventory = 0
                    except:
                        inventory = 0

                    try:
                        if int(row[20]) > 0:
                            price = int(row[20])
                        else:
                            price = 0
                    except:
                        price = 0

                    try:
                        if int(row[19]) > 0:
                            regular_price = int(row[19])
                        else:
                            regular_price = 0
                    except:
                        regular_price = 0

                    if not price or price == 0:
                        price = regular_price

                    product = Product.objects.create(
                        name=name,
                        sixteen_digit_code=sku,
                        product_id=product_id,
                        product_type=product_type,
                        summary_explanation=summary,
                        explanation=explanation,
                        status=status,
                        brand=brand,
                        first_inventory=inventory,
                        price=price,
                        regular_price=regular_price,
                    )
                    product.category.set(categories)
                    new_products_ids.append(product_id)
                    print(counter, ' >', product.id, ' created', inventory)
                    counter += 1
                index += 1

        with open('products.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row if exists
            var_index = 1
            var_counter = 1
            for row in reader:
                product_id = row[3].strip()
                product_type = row[47]
                if not product_type:
                    product_type = 'variation'
                if not Product.objects.filter(product_id=product_id).exists() and product_type == 'variation':
                    sku = skus[var_index][12]
                    name = row[0] or 'without name'
                    summary = row[4] or None
                    explanation = row[5] or None
                    status = Product.PROCESSING
                    brand = Brand.objects.filter(name__icontains=row[46]).first() or None if row[46] else None
                    categories = []
                    if row[49].split('>'):
                        cats = row[49].split('>')
                        cats = [cat.strip() for cat in cats]
                        categories = Category.objects.filter(name__in=cats)


                    try:
                        if int(row[18]) > 0:
                            inventory = int(row[18])
                        else:
                            inventory = 0
                    except:
                        inventory = 0

                    try:
                        if int(row[20]) > 0:
                            price = int(row[20])
                        else:
                            price = 0
                    except:
                        price = 0

                    try:
                        if int(row[19]) > 0:
                            regular_price = int(row[19])
                        else:
                            regular_price = 0
                    except:
                        regular_price = 0

                    if not price or price == 0:
                        price = regular_price

                    variation_of_sku = skus[var_index][13].strip() or 'sadasdasd'
                    variation_of_name = row[14].strip() or 'asdasdsadasd'
                    variation_of = Product.objects.filter(product_id=row[2].strip()).first()
                    if not variation_of:
                        variation_of = Product.objects.filter(
                            product_type=Product.VARIABLE
                        ).filter(Q(sixteen_digit_code=variation_of_sku) or Q(name__icontains=variation_of_name)).first()

                    product = Product.objects.create(
                        variation_of=variation_of,
                        name=name,
                        sixteen_digit_code=sku,
                        product_id=product_id,
                        product_type=product_type,
                        summary_explanation=summary,
                        explanation=explanation,
                        status=status,
                        brand=brand,
                        first_inventory=inventory,
                        price=price,
                        regular_price=regular_price,
                    )
                    product.category.set(categories)
                    new_products_ids.append(product_id)
                    print(var_counter, ' >', product.id, 'variation created', inventory)
                    var_counter += 1
                var_index += 1


        with open('pics.csv', 'r', encoding='utf-8') as s:
            pic_reader = csv.reader(s)
            header = next(pic_reader)  # Skip header row if exists
            for row in pic_reader:
                product_id = row[0].strip()
                if product_id in new_products_ids:
                    product = Product.objects.filter(product_id=product_id).first()
                    image_paths = re.findall(r'https?://[^\s!|]*?(/wp-content/[^\s!|]+?\.(?:jpe?g|png|webp|gif|bmp))',
                                             row[2], re.IGNORECASE)
                    base_url = "http://developersoroosh.ir"
                    full_urls = [base_url + path for path in image_paths]

                    if full_urls:
                        if len(full_urls) > 1:
                            pic = self.save_product_picture_from_url(product.id, full_urls[0])
                            product.picture = pic
                            product.save()
                            self.add_product_picture_gallery_from_url(product.id, full_urls[:1])
                        else:
                            if len(full_urls) == 1:
                                pic = self.save_product_picture_from_url(product.id, full_urls[0])
                                product.picture = pic
                                product.save()


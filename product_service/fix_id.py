import random
from django.db import transaction
from django.utils.text import slugify
from catalog.infrastructure.models import ProductModel, CategoryModel, BrandModel, ProductTypeModel, VariantModel

def generate_1000_real_products_docker():
    print("-> Đang kiểm tra và tự động khởi tạo danh mục/thương hiệu nền...")
    
    with transaction.atomic():
        # 1. TỰ ĐỘNG TẠO DANH MỤC (Nếu chưa có)
        cats = {}
        for c_name in ["Electronics", "Fashion", "Sports"]:
            obj, _ = CategoryModel.objects.get_or_create(
                name=c_name, 
                defaults={"slug": slugify(c_name)}
            )
            cats[c_name.lower()] = obj

        # 2. TỰ ĐỘNG TẠO THƯƠNG HIỆU (Nếu chưa có)
        brands = {}
        brand_countries = {"Apple": "USA", "Samsung": "Korea", "Nike": "USA", "Adidas": "Germany", "Sony": "Japan"}
        for b_name, country in brand_countries.items():
            obj, _ = BrandModel.objects.get_or_create(
                name=b_name, 
                defaults={"country": country}
            )
            brands[b_name.lower()] = obj

        # 3. TỰ ĐỘNG TẠO LOẠI SẢN PHẨM (Nếu chưa có)
        types = {}
        type_names = ["Smartphone", "Laptop", "Sneakers", "T-Shirt", "Headphones", "Tablet", "Smartwatch", "Earbuds", "TV"]
        for t_name in type_names:
            obj, _ = ProductTypeModel.objects.get_or_create(
                name=t_name, 
                defaults={"description": f"Mô tả cho loại {t_name}"}
            )
            # Tạo key dạng chữ thường xóa dấu gạch để khớp logic bên dưới (t-shirt -> tshirt)
            key = t_name.lower().replace("-", "")
            types[key] = obj

        # 4. XÓA SẠCH DỮ LIỆU CŨ TRONG DOCKER ĐỂ ĐỒNG BỘ TỪ P0001
        print("💥 Đang làm sạch các sản phẩm lỗi trước đó trong Docker...")
        VariantModel.objects.all().delete()
        ProductModel.objects.all().delete()

        # Bộ blueprints chứa dữ liệu thật và ảnh thật của bạn
        blueprints = [
            {"brand": brands["apple"], "cat": cats["electronics"], "type": types["smartphone"], "base_name": "iPhone 15 Pro", "img": "https://admin.hoanghamobile.com/Uploads/2023/09/14/vn-iphone-15-pro-natural-titanium-pdp-image-position-1a-natural-titanium-color.jpg", "price_min": 999, "price_max": 1499},
            {"brand": brands["apple"], "cat": cats["electronics"], "type": types["laptop"], "base_name": "MacBook Pro 14 M3", "img": "https://cdn.tgdd.vn/Products/Images/44/275442/macbook-pro-14-inch-m1-pro-2021-10-core-cpu-bac-1-750x500.jpg","price_min": 1599, "price_max": 2499},
            {"brand": brands["apple"], "cat": cats["electronics"], "type": types["tablet"], "base_name": "iPad Air M2", "img": "https://product.hstatic.net/200000949372/product/ipad-air-11-inch-m2_51631e6716b444d985e5dd6efe545d71.png", "price_min": 599, "price_max": 899},
            {"brand": brands["apple"], "cat": cats["electronics"], "type": types["earbuds"], "base_name": "AirPods Pro Gen 2", "img": "https://cdn.tgdd.vn/Products/Images/54/315014/tai-nghe-bluetooth-airpods-pro-2nd-gen-usb-c-charge-apple-1-750x500.jpg", "price_min": 249, "price_max": 279},
            {"brand": brands["samsung"], "cat": cats["electronics"], "type": types["smartphone"], "base_name": "Samsung Galaxy S24 Ultra", "img": "https://images.samsung.com/is/image/samsung/assets/vn/smartphones/galaxy-s24-ultra/buy/01_S24Ultra-Group-KV_PC_0527_final.jpg?imbypass=true", "price_min": 799, "price_max": 1299},
            {"brand": brands["samsung"], "cat": cats["electronics"], "type": types["smartwatch"], "base_name": "Samsung Galaxy Watch 6", "img": "https://cdn.tgdd.vn/Products/Images/7077/310861/samsung-galaxy-watch6-classic-lte-43mm-den-1-750x500.jpg", "price_min": 299, "price_max": 399},
            {"brand": brands["samsung"], "cat": cats["electronics"], "type": types["tv"], "base_name": "Samsung Crystal UHD 4K 55", "img": "https://cdnv2.tgdd.vn/mwg-static/dmx/Products/Images/1942/337090/smart-tivi-crystal-uhd-samsung-4k-55-inch-ua55u8550f-1-638811844944632698-700x467.jpg", "price_min": 499, "price_max": 899},
            {"brand": brands["sony"], "cat": cats["electronics"], "type": types["headphones"], "base_name": "Sony WH-1000XM5 Premium", "img": "https://www.sony.com.vn/image/6145c1d32e6ac8e63a46c912dc33c5bb?fmt=pjpeg&bgcolor=FFFFFF&bgc=FFFFFF&wid=2515&hei=1320", "price_min": 349, "price_max": 399},
            {"brand": brands["sony"], "cat": cats["electronics"], "type": types["earbuds"], "base_name": "Sony WF-1000XM5 Wireless", "img": "https://cdn2.cellphones.com.vn/insecure/rs:fill:0:358/q:90/plain/https://cellphones.com.vn/media/catalog/product/t/a/tai-nghe-khong-day-sony-wf-1000xm5_1.png", "price_min": 199, "price_max": 249},
            {"brand": brands["nike"], "cat": cats["sports"], "type": types["sneakers"], "base_name": "Nike Air Max 270 Black", "img": "https://images-na.ssl-images-amazon.com/images/I/81d0FiKm6NL.jpg", "price_min": 120, "price_max": 180},
            {"brand": brands["nike"], "cat": cats["sports"], "type": types["tshirt"], "base_name": "Nike Dri-FIT Athletic", "img": "https://supersports.com.vn/cdn/shop/files/IF2997-486-1.jpg?v=1773040886", "price_min": 25, "price_max": 45},
            {"brand": brands["adidas"], "cat": cats["sports"], "type": types["sneakers"], "base_name": "Adidas Ultraboost Light", "img": "https://assets.adidas.com/images/w_600,f_auto,q_auto/e45d363186da4d328080e9abc2839a55_9366/Giay_Ultraboost_Light_Be_ID3318.jpg", "price_min": 140, "price_max": 200},
            {"brand": brands["adidas"], "cat": cats["sports"], "type": types["tshirt"], "base_name": "Adidas Essentials Tee", "img": "https://cdn.vuahanghieu.com/unsafe/0x900/left/top/smart/filters:quality(90)/https://admin.vuahanghieu.com/upload/product/2023/02/ao-phong-adidas-essentials-tee-gn4069-mau-den-size-xs-63e1f63f15085-07022023135703.jpg", "price_min": 25, "price_max": 40},
            {"brand": brands["nike"], "cat": cats["fashion"], "type": types["tshirt"], "base_name": "Nike Sportswear Club Tee", "img": "https://static.nike.com/a/images/t_web_pdp_936_v2/f_auto,u_9ddf04c7-2a9a-4d76-add1-d15af8f0263d,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/6e51c5f5-ef2f-4f86-9ab0-db0fc16a3d35/AS+W+NSW+CLUB+SS+VRB+15+TEE.png", "price_min": 20, "price_max": 35},
            {"brand": brands["nike"], "cat": cats["fashion"], "type": types["sneakers"], "base_name": "Nike Court Vision", "img": "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco,c_scale,w_300,u_9ddf04c7-2a9a-4d76-add1-d15af8f0263d,c_scale,fl_relative,w_1.0,h_1.0,fl_layer_apply/a4b9a6fb-fbc5-485b-ae0b-f1263d3df85a/NIKE+COURT+VISION+MID+NN.png", "price_min": 70, "price_max": 120},
            {"brand": brands["adidas"], "cat": cats["fashion"], "type": types["tshirt"], "base_name": "Adidas Originals Trefoil Tee", "img": "https://www.jordan1.vn/wp-content/uploads/2023/09/429dffb6ad_1024x1024-removebg-preview_1db681684c81460e8cd6d318249edce3_927715c079ca4f2d9b36473e4b402d24.png", "price_min": 25, "price_max": 40},
            {"brand": brands["adidas"], "cat": cats["fashion"], "type": types["sneakers"], "base_name": "Adidas Stan Smith", "img": "https://assets.adidas.com/images/w_600,f_auto,q_auto/68ae7ea7849b43eca70aac1e00f5146d_9366/Stan_Smith_Shoes_White_FX5502_01_standard.jpg", "price_min": 80, "price_max": 130},
        ]

        colors = ["Space Gray", "Silver", "Midnight Black", "Titanium", "Obsidian", "Aurora", "Alpine White"]
        versions = ["V1", "V2", "Pro Edition", "Plus", "Generation 2026", "Special Pack", "Standard"]

        product_instances = []
        print("-> Đang sinh cấu trúc 1000 sản phẩm thật vào bộ nhớ RAM...")
        
        for i in range(1000):
            p_id = f"P{i+1:04d}"  # Tạo chuẩn từ P0001 đến P1000
            
            bp = random.choice(blueprints)
            color = random.choice(colors)
            ver = random.choice(versions)
            
            full_name = f"{bp['base_name']} {color} - {ver}"
            clean_sku = f"{bp['brand'].name.upper()}-{p_id}-{random.randint(10,99)}"

            product = ProductModel(
                id=p_id,
                name=full_name,
                sku=clean_sku,
                description=f"Sản phẩm {full_name} phân phối chính hãng bởi {bp['brand'].name}.",
                price=round(random.uniform(bp['price_min'], bp['price_max']), 2),
                stock=random.randint(20, 500),
                image=bp['img'],
                category=bp['cat'],
                brand=bp['brand'],
                product_type=bp['type'],
                is_active=True,
                attributes={"color": color, "version": ver, "is_mock": True}
            )
            product_instances.append(product)

        print("-> Đang thực hiện ghi bulk_create vào CSDL Docker...")
        ProductModel.objects.bulk_create(product_instances)

    print("=== THÀNH CÔNG: Đã tự động tạo danh mục nền và nạp 1000 sản phẩm thật từ P0001 -> P1000 ===")

generate_1000_real_products_docker()
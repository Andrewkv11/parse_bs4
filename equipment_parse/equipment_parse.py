import json
import random
import time
import requests
from bs4 import BeautifulSoup

base_url = "https://alpatech.ru"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "User-agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1"
}

# response = requests.get(url=base_url, headers=headers).text
# soup = BeautifulSoup(response, "lxml")
# category_list = soup.find("div", id="dropdown_138").find_all("a", class_="ty-menu__item-link a-first-lvl")
# category_dict = {}
# for category in category_list:
#     category_url = category["href"]
#     category_name = category.text.strip()
#     category_dict[category_name] = category_url
#
# with open("category_urls.json", "w") as file:
#     json.dump(category_dict, file, indent=4, ensure_ascii=False)
#
with open("category_urls.json") as file:
    category_dict = json.load(file)

for category in category_dict:
    response_category = requests.get(category_dict[category]).text
    soup_category = BeautifulSoup(response_category, "lxml")
    subcategory_list = soup_category.find("ul", class_="subcategories clearfix").find_all("a")
    products_dict = {}
    print(f"Идет запись категории - {category}.....")
    for subcategory in subcategory_list:
        subcategory_name = subcategory.text.strip()
        subcategory_url = subcategory["href"]
        products_dict[subcategory_name] = []
        print(f"     - Идет запись подкатегории {subcategory_name}......")
        try:
            while True:
                response_subcategory = requests.get(subcategory_url, headers=headers).text
                soup_subcategory = BeautifulSoup(response_subcategory, "lxml")
                pagination = soup_subcategory.find("div", class_="ty-pagination")
                products = soup_subcategory.find_all("div", class_="ty-product-list__content")
                for product in products:
                    one_product_dict = {}
                    product_name = product.find("a").text
                    product_url = product.find("a").get("href")
                    product_price = product.find("span", class_="ty-price")
                    if product_price:
                        product_price = int(product_price.text.split(".")[0].replace("\xa0", ""))
                    else:
                        product_price = "Цену уточняйте"
                    product_availability = product.find("span", class_="ty-qty-in-stock ty-control-group__item")
                    if product_availability:
                        product_availability = "В наличии"
                    else:
                        product_availability = "Запрашивайте"
                    one_product_dict["Наименование"] = product_name
                    one_product_dict["Цена"] = product_price
                    one_product_dict["Наличие"] = product_availability
                    one_product_dict["Ссылка"] = product_url
                    products_dict[subcategory_name].append(one_product_dict)
                    print(f"                   -----{product_name} записан")
                time.sleep(random.randint(1, 3))
                if not pagination:
                    break
                else:
                    next_page = pagination.find("a",
                                                class_="ty-pagination__item ty-pagination__btn ty-pagination__next cm-history cm-ajax ty-pagination__right-arrow")
                    if next_page:
                        subcategory_url = next_page.get("href")
                    else:
                        break
            print(f"     - Подкатегория {subcategory_name} записана")
        except:
            print("Не удалось обработать страницу")

    print(f"Категория {category} записана")
    with open(f"data/{category}.json", "w") as file:
        json.dump(products_dict, file, indent=4, ensure_ascii=False)

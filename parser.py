from seleniumbase import SB
import time

# Классы, которые использует озон на данный момент для отображения отзывов, придется менять при смене классов, либо автоматизировать поиск
REVIEW_CLASSES = {
    "review_block": ".v5r_30",
    "author": ".yp0_30",
    "date": ".q3r_30",
    "rating_stars": ".a5d10-a svg path",
    "text": ".r4q_30",
}
def parse_ozon_reviews(url):
    reviews_data =[]
    # Хром нужен обязательно, без него не работает undetectable фича.
    # Должен стоять на пк, выполняющем парсинг, либо скачивать приложение если есть GUI на пк, либо если на сервере линукс без GUI, то через chromium-browser+xvfb, можно было бы через playwright, но было сказано выполнять с помощью seleniumbase
    with SB(
        browser="chrome", 
        headless=True,
        undetectable=True,
    ) as sb:

        sb.open(url)
        sb.sleep(0.5)

        page = 1

        while True:
            print(f"\n=== Парсим страницу {page} ===")

            sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sb.sleep(0.5)

            if not sb.is_element_present(REVIEW_CLASSES["review_block"]):
                sb.save_screenshot('screen.png')
                print("Отзывы не найдены или доступ ограничен")
                break

            reviews = sb.find_elements(REVIEW_CLASSES["review_block"])

            for review in reviews:
                author = ""
                date = ""
                rating = 0
                text = ""

                try:
                    author = review.find_element("css selector", REVIEW_CLASSES["author"]).text
                except Exception as e:
                    # print(e)
                    pass

                try:
                    date = review.find_element("css selector", REVIEW_CLASSES["date"]).text
                except Exception as e:
                    # print(e)
                    pass

                try:
                    stars = review.find_elements("css selector", REVIEW_CLASSES["rating_stars"])
                    rating = len(stars)  # количество звезд
                except Exception as e:
                    # print(e)
                    pass

                try:
                    text = review.find_element("css selector", REVIEW_CLASSES["text"]).text
                except Exception as e:
                    # print(e)
                    pass

                reviews_data.append({
                    "author": author,
                    "date": date,
                    "rating": rating,
                    "text": text,
                })
                

            page+=1
            if sb.is_element_present("a:contains('Дальше')"): # Поиск кнопки для перехода на сдедующую страницу(sb.click_link('Дальше') не работает из-за невидимого блока поверх)

                link = sb.find_element("a:contains('Дальше')")
                sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                sb.sleep(0.5)
                sb.execute_script("arguments[0].click();", link)
            else: 
                break # нет следующей страницы - отзывы закончились
    return reviews_data

if __name__ == "__main__":
    product_id = input("Введите ID товара")
    url = f"https://www.ozon.ru/product/{product_id}/reviews/"
    res = parse_ozon_reviews(url)
    print(res)


import requests

class BaseAPIClient:
    # Базовый класс для работы с внешними API

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

        self.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }


    def _get(self, endpoint: str = "", params: dict = None) -> dict | None:
        # """Защищенный метод для выполнения GET-запросов с обработкой ошибок."""

        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()  # Проверка на ошибки HTTP (404, 500 и т.д.)
            return response.json()
        except requests.RequestException as e:
            print(f"[Ошибка API] Не удалось получить данные с {url}: {e}")
            return None


class CurrencyService(BaseAPIClient):
    # Сервис курс валют

    def __init__(self):
        # Передаем URL в родительский класс
        super().__init__(base_url="https://cbr-xml-daily.ru")

    def get_rates(self) -> str:
        data = self._get("/daily_json.js")
        if not data:
            return "⚠️ Не удалось загрузить курсы валют. Попробуйте позже."

        valute = data.get("Valute", {})
        usd = valute.get("USD", {}).get("Value", "—")
        eur = valute.get("EUR", {}).get("Value", "—")
        cny = valute.get("CNY", {}).get("Value", "—")

        return (
            "💰 <b>Актуальный курс ЦБ РФ:</b>\n\n"
            f"🇺🇸 Доллар (USD): <b>{usd} ₽</b>\n"
            f"🇪🇺 Евро (EUR): <b>{eur} ₽</b>\n"
            f"🇨🇳 Юань (CNY): <b>{cny} ₽</b>"
        )
class WeatherService(BaseAPIClient):
    """Сервис для получения реальной погоды через wttr.in (без API-ключа)."""

    def __init__(self):
        super().__init__(base_url="https://wttr.in")

    def get_weather(self, city: str) -> str:
        # Параметр format=j1 заставляет сервис вернуть подробный JSON
        data = self._get(f"/{city}", params={"format": "j1", "lang": "ru"})
        if not data or "current_condition" not in data:
            return f"❌ Не удалось получить погоду для города <b>{city}</b>. Проверьте название."

        current = data["current_condition"][0]
        temp = current.get("temp_C", "—")
        feels_like = current.get("FeelsLikeC", "—")
        wind_kmh = int(current.get("windspeedKmph", 0))
        wind_ms = round(wind_kmh / 3.6, 1)  # Переводим км/ч в привычные м/с

        # Достаем описание погоды на русском языке
        lang_ru = current.get("lang_ru", [])
        desc = lang_ru[0].get("value", "") if lang_ru else ""

        return (
            f"🌤 <b>Погода в городе {city.capitalize()}:</b>\n\n"
            f"☁️ На улице: <b>{desc}</b>\n"
            f"🌡 Температура: <b>{temp}°C</b> (ощущается как {feels_like}°C)\n"
            f"💨 Ветер: <b>{wind_ms} м/с</b>"
        )


class NewsService(BaseAPIClient):
    """Сервис для получения свежих новостей в формате JSON."""

    def __init__(self):
        # Бесплатный шлюз, который превращает RSS РИА Новостей в чистый JSON
        super().__init__(base_url="https://rss2json.com")

    def get_news(self, limit: int = 5) -> str:
        params = {
            "rss_url": "https://ria.ru"
        }
        data = self._get("/api.json", params=params)

        if not data or data.get("status") != "ok":
            return "⚠️ Не удалось загрузить новости. Попробуйте позже."

        items = data.get("items", [])[:limit]
        if not items:
            return "⚠️ Свежих новостей пока нет."

        news_list = ["📰 <b>Главные новости:</b>\n"]
        for i, item in enumerate(items, start=1):
            title = item.get("title", "Без заголовка").strip()
            link = item.get("link", "")
            news_list.append(f"{i}. <a href='{link}'>{title}</a>")

        return "\n\n".join(news_list)




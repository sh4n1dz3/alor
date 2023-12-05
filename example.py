import os
from AlorPy import AlorPy
import json
from tqdm import tqdm

username = os.environ["USERNAME"]
refresh_token = os.environ["REFRESH_TOKEN"]

ap_provider = AlorPy(username, refresh_token, demo=True)
ap_provider.OnError = lambda error: print(error)  # Будем выводить ошибки торговли

seconds_from = ap_provider.get_time()
print(seconds_from)

exchange = "MOEX"
symbol = "LKOH-12.23"

if "-" in symbol:
    portfolio = "7500025"
else:
    portfolio = "D00025"

# TQBR, RFUD
securities_info = ap_provider.get_securities_exchange(exchange, market="FORTS")
print(f"Найдено инструментов {len(securities_info)}")
print(json.dumps(securities_info[0], indent=4))
for security_info in tqdm(securities_info):
    if security_info["board"] == "RFUD" and security_info["tradingStatus"] == 17 and "12.23" in security_info["symbol"]:
        print(json.dumps(security_info, indent=4))

risk = ap_provider.get_risk(exchange, portfolio)  # Получаем информацию о тикере
risk_category_id = risk["riskCategoryId"]
client_type = risk["clientType"]
print(f"Категория клиента {portfolio} ({exchange}): {risk_category_id} ({client_type})")

symbol_info = ap_provider.get_symbol(exchange, symbol)  # Получаем информацию о тикере
print(json.dumps(symbol_info, indent=4))
trading_status = symbol_info["tradingStatus"]

if trading_status == 18:
    raise ValueError(f"Торговый статус {exchange}.{symbol}: нет торгов / торги закрыты")

min_step = symbol_info['minstep']  # Минимальный шаг цены
print(f'Миниальный шаг {exchange}.{symbol}: {min_step}')

symbol_risk_rates = ap_provider.get_risk_rates(exchange, symbol, risk_category_id)
print(json.dumps(symbol_risk_rates, indent=4))
is_short_sell_possible = symbol_risk_rates["list"][0]["isShortSellPossible"]
is_short_sell_possible_ = "Да" if is_short_sell_possible else "Нет"
asset_type = symbol_risk_rates["list"][0]["assetType"]
print(f"Возможен шорт {exchange}.{symbol}: {is_short_sell_possible_}")

order_book = ap_provider.get_order_book(exchange, symbol, 1)
print(print(json.dumps(order_book, indent=4)))

qty = 1
p = 0.01

if is_short_sell_possible or asset_type == "futures":
    quotes = ap_provider.get_quotes(f'{exchange}:{symbol}')[0]  # Последнюю котировку получаем через запрос
    print(print(json.dumps(quotes, indent=4)))
    bid = quotes["bid"]
    ask = quotes["ask"]
    print(f'Лучший спрос / лучшее предложение {exchange}.{symbol}: {bid} / {ask}')
    last_price = quotes['last_price']  # Последняя цена сделкинимальный шаг цены
    print(f'Последняя цена сделки {exchange}.{symbol}: {last_price}')

    # Новая лимитная заявка
    side = "buy"
    side_ = "покупку" if side == "buy" else "продажу"
    limit_price = last_price * (1 - p) if side == "buy" else last_price * (1 + p)   # Лимитная цена на 1% ниже последней цены сделки
    # Округляем цену кратно минимальному шагу цены
    limit_price = round(limit_price // min_step * min_step, 2)
    print(f'Заявка {exchange}.{symbol} на {side_} {qty} шт. по лимитной цене {limit_price}')
    response = ap_provider.create_limit_order(portfolio, exchange, symbol, side, qty, 69600)
    order_id = response['orderNumber']  # Номер заявки
    print(f'Номер заявки: {order_id}')

    side = "sell"
    side_ = "покупку" if side == "buy" else "продажу"
    limit_price = last_price * (1 - p) if side == "buy" else last_price * (1 + p)   # Лимитная цена на 1% ниже последней цены сделки
    # Округляем цену кратно минимальному шагу цены
    limit_price = round(limit_price // min_step * min_step, 2)
    print(f'Заявка {exchange}.{symbol} на {side_} {qty} шт. по лимитной цене {limit_price}')
    response = ap_provider.create_limit_order(portfolio, exchange, symbol, side, qty, 69700)
    order_id = response['orderNumber']  # Номер заявки
    print(f'Номер заявки: {order_id}')
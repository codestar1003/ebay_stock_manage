import json
# from django.conf import settings

def profit_formula(sell_price:float, purchase_price:int, prima:float, shipping:float, setting_attr:json):

    # with open(file=str(settings.BASE_DIR / 'utils/settings_attrs.txt'),  mode='r', encoding='utf-8') as f:
    #     setting_attr = f.read()

    # setting_attr = json.loads(setting_attr)

    purchase_price = purchase_price + prima

    fvf = 0
    oversea = 0
    payoneer = 0
    fedex = 0
    rate = setting_attr['rate']

    if setting_attr['fvf'] != 0:
        fvf = setting_attr['fvf'] / 100

    if setting_attr['oversea'] != 0:
        oversea = setting_attr['oversea'] / 100

    if setting_attr['payoneer'] != 0:
        payoneer = setting_attr['payoneer'] / 100

    if setting_attr['fedex'] != 0:
        fedex = setting_attr['fedex'] / 100

    profit = (sell_price - sell_price * fvf - sell_price * oversea) * (rate - rate * payoneer) - purchase_price - shipping - shipping * fedex

    return profit

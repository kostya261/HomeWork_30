from decimal import Decimal

import stripe

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def convert_rub_to_dollars(amount):
    """ Конвертирует рубли в центы USD. """
    from forex_python.converter import CurrencyRates

    try:
        c = CurrencyRates()
        # Получаем курс RUB → USD
        rate = c.get_rate('RUB', 'USD')

        # Преобразуем Decimal в float
        if isinstance(amount, Decimal):
            rub = float(amount)
        else:
            rub = amount

        # Конвертируем: рубли → доллары → центы
        usd = rub * rate
        cents = int(usd * 100)

        print(f"[Конвертация] {rub} RUB → {usd:.2f} USD → {cents} центов")

        # Проверяем минимальную сумму Stripe (50 центов)
        if cents < 50:
            print(f"[Внимание] Сумма {cents} центов меньше минимальной!")

        return cents

    except Exception as e:
        print(f"[Ошибка конвертации] {e}, используем фиксированную сумму")
        # На всяк случай
        rub = float(amount) if isinstance(amount, Decimal) else amount
        return int((rub / 90) * 100)


def create_stripe_product(name, description=None):
    """ Создает продукт в Stripe. """
    product_data = {"name": name}
    if description:
        product_data["description"] = description

    product = stripe.Product.create(**product_data)
    return product.id


def create_stripe_price(amount_cents, product_id, currency='usd'):
    """ Создает цену в Stripe. """
    price = stripe.Price.create(
        unit_amount=amount_cents,
        currency=currency.lower(),
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id, success_url=None, cancel_url=None):
    """ Создает сессию оплаты в Stripe. """
    if not success_url:
        success_url = 'http://127.0.0.1:8000/payment/success/'
    if not cancel_url:
        cancel_url = 'http://127.0.0.1:8000/payment/cancel/'

    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
    )

    return {
        'session_id': session.id,
        'url': session.url,
        'payment_status': session.payment_status
    }


def get_stripe_session_status(session_id):
    """ Получает статус сессии оплаты из Stripe. """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status
    except stripe.error.StripeError as e:
        return str(e)

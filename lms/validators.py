import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_allowed_domains(value):
    """
    Валидатор для проверки ссылок на разрешенные домены.
    Разрешен только youtube.com.
    """
    if not value:
        return

    # Регулярное выражение для извлечения домена из URL
    domain_pattern = r'https?://(?:www\.)?([^/]+)'
    match = re.search(domain_pattern, value)

    if not match:
        raise ValidationError(
            _('Неверный формат ссылки.'),
            code='invalid_url'
        )

    domain = match.group(1).lower()

    # Разрешенные домены
    ALLOWED_DOMAINS = ['youtube.com', 'youtu.be']

    # Проверяем, является ли домен разрешенным или его поддоменом
    is_allowed = any(
        domain == allowed_domain or domain.endswith(f'.{allowed_domain}')
        for allowed_domain in ALLOWED_DOMAINS
    )

    if not is_allowed:
        raise ValidationError(
            _('Ссылки разрешены только на youtube.com.'),
            code='domain_not_allowed'
        )


def validate_text_for_links(text):
    """
    Проверяет текст на наличие запрещенных ссылок.
    Если в тексте есть ссылки не на youtube - выбрасывает ошибку.
    """
    if not text or not isinstance(text, str):
        return

    # Ищем все ссылки в тексте
    url_pattern = r'https?://[^\s<>"\']+'
    urls = re.findall(url_pattern, text)

    for url in urls:
        # Проверяем каждую ссылку через наш валидатор
        try:
            validate_allowed_domains(url)
        except ValidationError:
            # Обрезаем длинные URL для читаемости
            display_url = url[:50] + ('...' if len(url) > 50 else '')
            raise ValidationError(
                _('В тексте найдена запрещенная ссылка: %(url)s. Разрешены только ссылки на YouTube.'),
                params={'url': display_url},
                code='forbidden_link_in_text'
            )
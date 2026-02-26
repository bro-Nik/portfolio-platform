from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Получить реальный IP клиента с учетом прокси."""
    # Заголовки в порядке приоритета
    ip_headers = ['X-Real-IP', 'CF-Connecting-IP', 'True-Client-IP', 'X-Forwarded-For']
    
    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For может содержать цепочку: "client, proxy1, proxy2"
            # Берем первый IP (оригинальный клиент)
            return ip.split(',')[0].strip()
    
    return request.client.host if request.client else '127.0.0.1'

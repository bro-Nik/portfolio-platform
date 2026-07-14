from fastapi import Request


def get_client_ip(request: Request) -> str:
    ip_headers = ['X-Real-IP', 'CF-Connecting-IP', 'True-Client-IP', 'X-Forwarded-For']

    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            return ip.split(',')[0].strip()

    return request.client.host if request.client else '127.0.0.1'

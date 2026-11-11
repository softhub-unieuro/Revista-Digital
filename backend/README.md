# Backend

Django 5.2/DRF com PostgreSQL, usuário próprio e Celery. Instalação reproduzível em uv.lock.
Os primeiros endpoints funcionais são health checks e autenticação por sessão/CSRF.
O cadastro editorial e os arquivos continuam no backlog do Sprint 1.

A partir da raiz: uv sync --project backend --locked, make up e make check.
Use createsuperuser pelo contêiner para criar o acesso inicial. Não há senha padrão.
Ver o README da raiz para os endereços e comandos completos.

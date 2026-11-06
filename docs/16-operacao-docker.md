# Instalação e operação Docker

Entrega técnica de 04/11/2026. O responsável informou que ainda não há servidor nem
domínio e escolheu receber o pacote Docker. Este guia prepara a implantação futura;
não indica que já exista um site público ou renovação de certificado configurada.

## Conteúdo e requisitos

O ZIP contém código, assets do frontend fornecido, lockfiles, imagens reproduzíveis
por Dockerfiles, Compose, migrações, testes e manuais. Não contém imagens Docker já
compiladas, senhas, certificados, banco nem publicações. A primeira compilação precisa
de internet para baixar imagens e dependências. Confira o SHA-256 no arquivo lateral
e o commit em ENTREGA.json.

Instale Docker com Compose v2 e Python 3.11+ para os utilitários. Use um host Linux
com disco persistente e espaço para originais, versões históricas, derivados e backups.
Dimensione os recursos com a carga real antes de contratar: os limites de API (512 MiB)
e worker (768 MiB, um processamento por vez) são limites dos contêineres, não uma
promessa de capacidade total do servidor. PostgreSQL e Redis também consomem recursos.

## Configurar e iniciar

Entre na pasta extraída `unieuro-revista`. Obtenha um certificado válido para o domínio
escolhido, incluindo a cadeia completa, e instale `fullchain.pem` e `privkey.pem` em
`deploy/certs`. Proteja a chave privada e permita sua leitura pelo contêiner Nginx.
Nunca envie esses arquivos ao Git. Não há emissão ou renovação automática neste pacote.

Com um domínio real, substitua o exemplo abaixo:

```bash
python3 scripts/init_production_env.py --origin https://revista.exemplo.edu.br --http-bind 0.0.0.0:80 --https-bind 0.0.0.0:443
chmod 600 .env.production
docker compose --env-file .env.production -f compose.production.yaml config --quiet
docker compose --env-file .env.production -f compose.production.yaml up --build -d --wait --wait-timeout 180
```

O gerador cria segredos aleatórios e recusa sobrescrever uma configuração existente.
Guarde `.env.production` separadamente e com acesso restrito. Não publique a saída de
`docker compose config` sem `--quiet`: ela contém segredos interpolados. Configure DNS,
firewall e certificados no host antes de expor as portas. Banco e Redis não publicam portas.
O nome padrão do projeto é `revista-producao`; se usar `-p`, repita o mesmo nome em
**todos** os comandos operacionais e de backup.

No Colima, acrescente `--context colima` após `docker` e use um diretório de certificados
compartilhado com a VM, como `deploy/certs` dentro do projeto. `/tmp` do macOS não foi
compartilhado no ambiente usado nos testes. Não altere o contexto global do Docker.
Para um teste local, mantenha os bindings padrão de loopback e use um certificado local
explicitamente confiado pelo cliente de teste; não desative a verificação TLS.

Crie o primeiro administrador interativamente, sem senha padrão:

```bash
docker compose --env-file .env.production -f compose.production.yaml exec api /app/.venv/bin/python manage.py createsuperuser
```

Abra `/admin/login` na origem HTTPS e entre com esse e-mail. O comando cria o acesso
administrador inicial; usuários adicionais são gerenciados pelo painel da revista.
O UserAdmin do Django é somente leitura. Para recuperar acesso com controle do servidor:

```bash
docker compose --env-file .env.production -f compose.production.yaml exec api /app/.venv/bin/python manage.py changepassword EMAIL_DO_ADMIN
```

O terminal solicita a nova senha. Não coloque senhas em argumentos, documentação ou Git.

## Verificações e atualização

```bash
docker compose --env-file .env.production -f compose.production.yaml ps
docker compose --env-file .env.production -f compose.production.yaml logs --tail=100 api worker web
curl --fail https://revista.exemplo.edu.br/health/ready
```

`/health/live` confirma processo e `/health/ready` verifica banco/Redis. O worker tem
healthcheck Celery e retoma uploads pendentes ao iniciar. Logs da API registram
request_id, método, caminho, status e duração; não registram corpo, cookies ou query.
Auditoria editorial guarda responsável, registro e nomes de campos alterados.
Healthchecks não enviam alertas: destino, responsável e monitor externo ainda devem ser definidos.

Antes de atualizar, faça backup consistente e guarde código/imagens e configuração da
versão anterior. Defina `APP_VERSION` para identificar a nova imagem, então repita
`up --build -d --wait`. O serviço `migrate` aplica migrações e coleta arquivos estáticos
antes de iniciar API/worker. Faça login, publique um rascunho de teste autorizado e
confira leitor, busca, avaliação, download e arquivamento no domínio final.

Para parar sem remover dados:

```bash
docker compose --env-file .env.production -f compose.production.yaml down
```

**Não use `down -v` em ambientes com dados:** isso exclui volumes. PDFs ficam em volume
privado e cada requisição passa por autorização antes do Nginx interno. Ler um PDF
necessariamente transfere seu conteúdo ao navegador; desativar download não é DRM.

## Backup coerente

Reserve uma janela curta de manutenção: o script para web/API/worker, exporta PostgreSQL
e arquivos privados e reinicia os serviços previamente ativos, inclusive se houver erro.
A pasta de destino deve ser nova. Execute na pasta do projeto:

```bash
python3 scripts/production_backup.py backup --env-file .env.production --project revista-producao --directory backups/2026-11-04
python3 scripts/production_backup.py verify --env-file .env.production --project revista-producao --directory backups/2026-11-04
```

Use `--context colima` no utilitário se necessário. O manifesto contém tamanho,
SHA-256 e IDs das imagens. O backup contém dados pessoais e hashes de senhas: pasta
700/arquivos 600 não substituem criptografia e controle de acesso fora do host. Copie-o
para o destino externo aprovado e guarde também código e configuração privada original
em local seguro. A configuração não é incluída no backup; sem seus segredos/senha do banco,
a recuperação exige ajustes. Redis/cache não é restaurado; sessões ativas persistidas
no banco dependem da mesma chave Django e os trabalhos pendentes são retomados pelo worker.

Agendamento, cópia externa, retenção (proposta: 7 diários e 4 semanais), responsáveis,
RPO de 24 h e RTO de 4 h precisam ser acordados e medidos no host final. Nenhum desses
alvos é um serviço contratado ou um agendamento já instalado neste pacote.

## Restaurar em um destino vazio

Use outro projeto/volumes e portas livres. Copie a configuração original para
`.env.restore`, mantendo os segredos, e ajuste `PRODUCTION_ENV_FILE` para o caminho
absoluto desse arquivo, `PUBLIC_ORIGIN`, `DJANGO_CSRF_TRUSTED_ORIGINS`, bindings e
certificados do destino. Proteja o arquivo com modo 600. Não gere outra senha do banco
sem planejar a recuperação. Exemplo de nome de projeto isolado:

```bash
docker compose --env-file .env.restore -f compose.production.yaml -p revista-recuperacao up --build -d --wait db redis
python3 scripts/production_backup.py restore --env-file .env.restore --project revista-recuperacao --directory backups/2026-11-04
docker compose --env-file .env.restore -f compose.production.yaml -p revista-recuperacao up -d --wait --wait-timeout 180
```

O script verifica checksums/caminhos do tar e recusa sobrescrever tabelas, arquivos ou
uma aplicação em execução. Se falhar no meio, preserve o backup e recomece com outro
destino vazio; não tente mesclar restauração parcial com dados existentes.
Confirme usuários, créditos, publicações, versões históricas e os hashes dos PDFs.
Só depois direcione tráfego ao ambiente recuperado. O exercício automatizado de QA
faz essa conferência com PDFs textuais/digitalizados e uma versão antiga substituída.

Rollback de código não desfaz migrações ou conteúdo. Se a versão anterior for compatível
com o esquema, inicie-a e repita o smoke test. Se não for, restaure o backup em ambiente
isolado e valide antes de trocar tráfego. Nenhum comando automático sobrescreve produção.

## Retenção de arquivos

```bash
docker compose --env-file .env.production -f compose.production.yaml exec api /app/.venv/bin/python manage.py cleanup_storage --days 30
```

Sem `--apply`, apenas conta candidatos. Após revisar a política e o backup, acrescente
`--apply` para remover arquivos/documentos sem vínculo e derivados órfãos expirados.
Documentos de publicações e de seu histórico são preservados; arquivar não apaga arquivos.
Versões antigas continuam consumindo disco. Ajuste capacidade e política editorial antes
de aceitar remoção de histórico. Não há expurgo de versões publicadas nesta entrega.

## Referências

[Docker Compose em produção](https://docs.docker.com/compose/how-tos/production/),
[autenticação Django](https://docs.djangoproject.com/en/5.2/topics/auth/default/) e
[proxy Nginx](https://nginx.org/en/docs/http/ngx_http_proxy_module.html).

# Homologação, produção e entrega

Atualização de 04/11/2026: o responsável escolheu pacote Docker, pois ainda não há
servidor/domínio. Compose de produção, HTTPS local, smoke test e restauração isolada
estão implementados. [Guia executável](16-operacao-docker.md),
[manual editorial](17-manual-editorial.md) e [evidências/limites](15-sprint3-entrega.md).
Ainda não existe implantação pública. Os itens abaixo são o checklist para o host final.

## Antes da homologação

- Definir responsável técnico, responsável editorial, hospedagem, domínio e acessos.
- Dimensionar banco, disco, memória do worker e limite de uploads após a prova de PDFs.
- Manter ambientes separados para desenvolvimento, homologação e produção.
- Usar contas e dados de teste; PDFs de demonstração autorizados.
- Configurar frontend e /api no mesmo domínio; rota interna de arquivos inacessível diretamente.
- Documentar custos e capacidade escolhidos antes de contratar qualquer serviço.

## Artefatos de implantação previstos

Dockerfiles de frontend/API/worker, composição de desenvolvimento e produção, proxy
Nginx, variáveis de ambiente exemplificadas, comandos de migração, backup/restore,
health checks, rotina de deploy e estratégia de rollback.

Segredos reais ficam no ambiente/gerenciador apropriado, nunca no repositório. Arquivos
enviados e banco usam volumes persistentes. Recriar um contêiner não pode apagar revistas.

## Checklist de produção

- [ ] Artefato testado e identificado por commit/tag; dependências fixadas.
- [ ] DNS e HTTPS funcionando e renovação de certificado verificada.
- [ ] DEBUG desativado; hosts, origem confiável, sessão, CSRF e cookies revisados.
- [ ] Limites de bytes e timeouts coerentes entre proxy, API e worker.
- [ ] Migrações testadas; backup anterior guardado e procedimento de recuperação verificado.
- [ ] Arquivos privados e Range funcionando por autorização interna.
- [ ] Primeiro administrador criado por procedimento seguro, sem credencial padrão.
- [ ] Filas, armazenamento e readiness funcionando; logs sem segredos.
- [ ] SPA abre rotas diretamente e permite recarregar detalhe/admin sem 404 do proxy.
- [ ] Mocks e credenciais demonstrativas ausentes do caminho de produção.
- [ ] Smoke test real de publicação, busca, leitor, avaliação e download aprovado.
- [ ] Monitoramento e responsável por incidentes definidos.

## Backup e restauração

Proposta inicial: backup diário de PostgreSQL e arquivos, com retenção de 7 diários e
4 semanais, guardados fora do host principal e protegidos por acesso. Confirmar retenção
e custo antes da produção. Alvos iniciais: perda máxima de 24 h (RPO) e recuperação em
até 4 h (RTO), a demonstrar no exercício de restauração.

Cada backup deve ter manifesto/checksum e forma de recuperar a relação entre banco e
versões de arquivos. Testar a restauração em outro ambiente, abrir revistas e validar
as permissões. Backup existente sem restauração comprovada não atende ao aceite.

## Monitoramento

Monitorar liveness, readiness, falhas HTTP, fila acumulada, job falho, disco, tempo de
processamento e último backup concluído. Logs estruturados com request_id/job_id.
Alertas precisam de destino e responsável; não assumir que registrar log já notifica alguém.

## Rollback

Guardar a versão anterior e o artefato homologado. Antes de migração destrutiva, preferir
migrações compatíveis em etapas e comprovar a recuperação. Reverter aplicação não
reverte automaticamente esquema ou dados. Definir ação por falha e validar em homologação.

## Entrega ao professor e à equipe

Entregar URL final, versão, escopo validado, manual editorial, guia técnico, rotina de
backup/restauração, contatos/responsáveis e lista de limitações conhecidas. Credenciais
e acessos são transferidos por canal apropriado, com o responsável controlando a conta.

Treinamento: entrar, enviar revista, corrigir erros, escolher capa/tema, salvar rascunho,
publicar, editar, arquivar/restaurar e acompanhar avaliações. Fazer uma publicação real
durante a demonstração.

## Aceite final

- [ ] Jornada T01–T30 aplicável concluída com evidências no ambiente final.
- [ ] PDF real de 300 páginas navega até o fim no desktop e no celular.
- [ ] Arquivo de 301 páginas rejeitado e usuário informado.
- [ ] Visual aprovado e navegação acessível.
- [ ] Não há falha bloqueadora/crítica aberta.
- [ ] Backup restaurado, operação demonstrada e documentação testada por outra pessoa.
- [ ] Tag v1.0.0, data e responsáveis registrados.
- [ ] Janela de estabilização e atendimento acordada e pendências registradas.

Datas, responsáveis e URL final serão preenchidos quando definidos; não são entregas
já realizadas por este plano.

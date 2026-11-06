# Matriz de rastreabilidade

Todo requisito obrigatório precisa de implementação e evidência de teste.

| ID | Requisito | Tarefas | Testes |
|---|---|---|---|
| R01 | Portal público e catálogo | DOM-02, INT-01 | T08, T12 |
| R02 | Busca consistente e filtros | DOM-02, INT-01, INT-03 | T09, T10 |
| R03 | Temas, contagens e acervo completo | DOM-01, DOM-02, INT-01 | T08, T11 |
| R04 | Dados e links institucionais | DOM-03, INT-03, VIS-02 | T22, T24 |
| R05 | Login e sessão reais | AUTH-01 | T03 |
| R06 | Papéis e propriedade dos dados | AUTH-02, AUTH-03 | T04, T05, T07 |
| R07 | Ciclo de publicação persistente | DOM-01, INT-02 | T06, T23, T27 |
| R08 | Categorias e configurações | DOM-01, DOM-03, INT-03 | T08, T22 |
| R09 | Upload de 1 a 300 páginas | PDF-01, PDF-02, INT-02 | T13, T14, T15 |
| R10 | Capas e arquivos persistentes | PDF-03 | T16, T23, T28 |
| R11 | Leitura/download e Range autorizado | PDF-04 | T07, T17 |
| R12 | PDF real e uso limitado de recursos | FUND-04, READ-01, QA-03 | T18, T26 |
| R13 | Navegação completa no celular | READ-02 | T18 |
| R14 | Animação de virar páginas | READ-03 | T19 |
| R15 | Zoom e controles acessíveis | READ-04 | T20, T25 |
| R16 | Avaliação persistente e médias | DOM-03, INT-04 | T21, T23 |
| R17 | Gestão de usuários e indicadores | AUTH-03, DOM-03, INT-03 | T04, T05, T22 |
| R18 | Visual conforme referência | VIS-01, VIS-02, VIS-03 | T24 |
| R19 | Responsividade e navegadores | VIS-03, QA-04 | T18, T24, T25 |
| R20 | Ambiente e CI reprodutíveis | FUND-01, FUND-02, FUND-03 | T01, T02 |
| R21 | Teste integrado e sem mocks | QA-01, QA-02 | T06–T23, T27 |
| R22 | Homologação e produção | OPS-01, OPS-03, REL-01 | T29 |
| R23 | Backup, recuperação e operação | OPS-02 | T28 |
| R24 | Manuais, treinamento e aceite | REL-02, REL-03 | T30 |

## Evidência S03 — 04/11/2026

AUTH-02/03, DOM-01/02/03, PDF-03/04, INT-03/04 e QA-01: testes reais em
`backend/tests/test_editorial_admin.py`, `test_catalog_documents.py`,
`test_authentication.py` e jornada visual com persistência. OPS-01: imagens/Compose
de produção, Nginx TLS e `scripts/smoke_production.py`. Backup/restore parcial de
OPS-02: `production_backup.py`, `verify_restored_backup.py` e job production do CI.

[Relatório e capturas](15-sprint3-entrega.md), [operação](16-operacao-docker.md),
[manual](17-manual-editorial.md). QA de capacidade/dispositivos e aceites REL continuam
abertos; presença do manual não comprova treinamento/transferência de operação.

## Consolidação de homologação

[T27 — concorrência, T14 — limite real de bytes, T18 — páginas mistas, T26 — medidas parciais](18-homologacao-leitor.md).
Implementação: `catalog/concurrency.py`, migração 0006, formulários de publicação e
recuperação do leitor. Provas: `test_editorial_concurrency.py`, `capacity_probe.py`,
`qa_gateway.py` e etapa HTTPS de `smoke_production.py`. O histórico de provas S02/S03
permanece disponível; a rodada atual não encerra os critérios de hardware/aceite humano.

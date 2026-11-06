# Riscos, decisões e dependências

## Decisões de partida

| ID | Decisão | Situação |
|---|---|---|
| D01 | Monorepo independente com frontend existente e backend novo | Adotada para iniciar |
| D02 | React/Vite + Django/DRF + PostgreSQL | Adotada; versões fixadas e verificadas em F01 |
| D03 | Mesmo domínio e autenticação por sessão/CSRF | Adotada; hospedagem deve preservar esse desenho |
| D04 | PDF entre 1 e 300 páginas; 200 MiB configuráveis | Adotada como proposta inicial a medir |
| D05 | Arquivos privados com volume persistente e entrega interna autorizada | Adotada para MVP; S3 por adaptador se infraestrutura exigir |
| D06 | PDF.js; biblioteca de animação substituível por adaptador | Prova de desempenho em FUND-04 |
| D07 | Três perfis porque já aparecem na interface | Incluídos na versão 1.0 |
| D08 | Avaliação anônima por navegador e publicação | Adotada; não verifica identidade de pessoas |
| D09 | Traços vermelhos da imagem ou dourados do chat | Resolvida: preservar dourado do frontend final fornecido |
| D10 | Domínio, hospedagem e capacidade | Pendente antes de OPS-01; sem contratação neste plano |
| D11 | Logo, capas, textos institucionais e ISSN final | Logo/capas recebidos no pacote final; textos e ISSN ainda precisam de confirmação |

## Riscos e tratamento

| Risco | Impacto | Tratamento | Responsável por resolver |
|---|---|---|---|
| Misturar educação física com revistas | Modelo e escopo errados | Base exclusiva Revista-Digital e manifesto | Desenvolvimento |
| Animação exigir 300 páginas renderizadas | Travamento no celular | Prova em F01; cache limitado e alternativa CSS | Desenvolvimento |
| PDF escaneado enorme apesar de 300 páginas | Lentidão ou memória excessiva | Limites separados de bytes/pixels/tempo e medição | Desenvolvimento |
| Falha/repetição de job | Duplicação ou estado incorreto | Estado no banco, idempotência e retry testado | Desenvolvimento |
| Novo PDF quebrar edição já pública | Indisponibilidade | Versão candidata separada e troca transacional | Desenvolvimento |
| Arquivo de rascunho exposto por URL | Acesso indevido | Armazenamento privado e autorização em cada acesso | Desenvolvimento |
| Dados simulados parecerem persistentes | Falso aceite | E2E com reload/reinício e proibição de mocks em produção | Qualidade |
| Falta de materiais oficiais | Baixa fidelidade | Solicitar/consolidar materiais em VIS-01 | Responsável editorial |
| Escolha visual divergente | Retrabalho | Registrar decisão de paleta antes da fase visual | Responsável editorial |
| Ambiente final sem Range ou worker | Leitor/upload inadequados | Definir requisitos de infraestrutura cedo e validar em homologação | Operação |
| Backup sem arquivos ou sem teste | Perda de revistas | Backup conjunto e restauração em ambiente limpo | Operação |
| Prazo sem disponibilidade da equipe | Estimativa irreal | Esforço relativo, reserva e reestimativa em F01/F04 | Responsável do projeto |

Pendências de materiais/infraestrutura não impedem avançar em ambiente local e testes
com fixtures. Registrar a resolução de cada decisão com data e evidência; não inventar
conteúdo institucional ou credenciais para encerrar tarefas.

## Mudança de escopo

Nova necessidade recebe descrição, benefício, impacto em dados/API/telas/testes e efeito
na estimativa. Pedido explícito do responsável atualiza o plano. Funcionalidades futuras
do PDF orientativo não entram automaticamente na versão 1.0.

## Dependência identificada na preparação

A instalação da base apontou dois pacotes classificados como high pelo npm audit.
FUND-01 deve corrigir vite e source-map-js, fixar versões compatíveis e repetir os checks.
O build passou, mas isso não encerra os achados de dependências.

## Decisão de implementação da Sprint 2

Motion 14.9.0 sobre o par atual, em adaptador independente, preservou texto/links e o
orçamento de canvases. A comparação executável com StPageFlip e as medições completas
seguem abertas; justificativa e evidência em [entrega da Sprint 2](14-sprint2-pdf-real.md).

## Decisões S03 — 04/11/2026

- Entregar pacote Docker sem contratar hospedagem; usuário ainda não tem host/domínio.
- Reutilizar React existente e Django/DRF; não migrar backend para Node só pela disponibilidade de bibliotecas.
- Preservar PDFs históricos para leitores abertos; crescimento do disco precisa de acompanhamento.
- Backup coerente usa parada breve; agendamento externo/alertas dependem do ambiente final.
- Último administrador protegido inclusive contra atualização simultânea; UserAdmin do Django somente leitura.
- Gravação editorial é transacional, mas não implementa conflito otimista de formulários antigos (última gravação vence).
- Não declarar aceite de celular físico, heap, carga simultânea, comparação visual humana ou lançamento público sem esses testes.

## Consolidação S03 — 04/11/2026

O risco de formulário antigo sobrescrever uma edição foi tratado com versão crescente,
If-Match obrigatório e validação transacional. A decisão anterior de última gravação
vencer foi substituída por rejeição 412 e revisão explícita do formulário. Veja
[contrato](05-api.md) e [evidências](18-homologacao-leitor.md). Os riscos de memória
total/dispositivo/carga e infraestrutura permanecem abertos.

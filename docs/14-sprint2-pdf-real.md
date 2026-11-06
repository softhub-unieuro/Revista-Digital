# Entrega de desenvolvimento: catálogo e leitor real

Implementação em 03/11/2026 sobre o frontend final fornecido. Esta entrega resolve as
dependências de cadastro/upload necessárias ao leitor. Não declara concluídos todos
os cadastros da Sprint 1 nem a homologação/produção da Sprint 3.

## Comportamento entregue

- Home, catálogo, detalhe, busca, temas e acervo usam publicações do PostgreSQL.
  Nenhum desses caminhos importa `src/data.js`. Base vazia mostra estado vazio.
  A interface percorre a paginação da API para formar seu índice de metadados;
  paginação visual de catálogos muito grandes continua para a consolidação.
- O wizard original envia PDF real, acompanha o job e bloqueia avanço até ready.
  Título, edição, data e categorias são obrigatórios; descrição é opcional.
  Criação usa chave UUID estável para repetição após falha de rede sem duplicar edição.
- Colaborador prepara seus rascunhos; editor/admin publicam, arquivam e restauram.
  O PDF substituto só entra na publicação após processamento e salvamento explícito.
- Categorias podem ser criadas, editadas e desativadas por editor/admin. Desativar
  retira o tema da navegação pública e preserva seus vínculos históricos.
- PDFs ficam em volume privado, com identificadores gerados pelo servidor.
  Parse, contagem, senha, SHA-256 e capa são processados pelo Celery, fora da requisição.
  Limite: 1–300 páginas e `MAX_PDF_BYTES` (padrão 200 MiB). Capa JPG/PNG opcional,
  até 5 MiB e 16 megapixels, com orientação EXIF corrigida e redução de dimensões.
- Job persistente: queued → processing → ready/failed. Lease impede resultado antigo
  de sobrescrever nova execução. Reexecução de ready é idempotente. Há endpoint de
  repetição e comando de recuperação de jobs queued/stale ao iniciar o worker.
  O comando pode ser executado manualmente; não é um agendador periódico.
- A API autoriza arquivos a cada acesso, entrega blocos de 64 KiB e suporta HEAD,
  Range 206, Content-Range, If-Range e 416. Arquivar bloqueia URLs públicas conhecidas.
  Delegação a Nginx, retenção de órfãos e backup ainda pertencem à entrega operacional.
- Avaliação anônima persiste uma nota por cookie assinado/edição. Alterar a nota atualiza
  o voto e a média sem aumentar a contagem. Configuração institucional e rate limit de
  avaliações ainda não foram integrados.

## Leitor e decisão de animação

PDF.js **6.5.438** e worker da mesma versão são carregados apenas ao entrar em `/ler`.
CMaps, fontes padrão e WASM são servidos localmente; não há CDN obrigatória.
Núcleo de índice/renderização em TypeScript **7.0.2**; telas React existentes preservadas.

O adaptador `PageTurn` usa Motion **14.9.0**: recebe somente o par atual, sem conhecer o
PDF. Transição de saída + entrada de aproximadamente 320 ms. `prefers-reduced-motion`
e o controle “Sem animação” removem a transição. Texto selecionável, links externos
HTTP(S)/mailto e destinos internos usam camadas separadas.

O contrato de [StPageFlip](https://nodlik.github.io/StPageFlip/docs/classes/pageflip.html)
carrega uma coleção de elementos de páginas. É possível virtualizar o conteúdo desses
elementos, mas isso exigiria conciliar o ciclo de vida imperativo com React/PDF.js.
A escolha desta entrega foi a transição sobre o par atual, que manteve limites simples
e passou a navegação longa. **Não foi feito benchmark executável de StPageFlip:** a
comparação completa prevista em FUND-04 continua aberta. Não se afirma que StPageFlip
exija 300 canvases nem que tenha desempenho inferior medido.

No workspace com pelo menos 900 px: capa isolada, pares 2–3, 4–5 e última página válida.
Em espaços menores: uma página por vez, sem pular as pares. Há navegação por botões,
teclado, salto validado, miniaturas virtualizadas, busca textual no PDF, zoom 60–200%,
ajuste, download e tela cheia. O código de gesto aceita deslize horizontal em zoom
ajustado; o teste de toque em dispositivo físico está pendente.

## Orçamento de superfícies

Estado estável: até **2 canvases de página**, no máximo **4 milhões de pixels cada**;
janela de **10 miniaturas**, até **40 mil pixels cada**. A capa usa JPEG em vez de canvas.
No cenário 390 px, apenas 1 canvas de página e nenhuma miniatura montada. Cancelar
renderizações e mudar zoom cria superfícies independentes: o cancelamento de uma
execução antiga não apaga o canvas de sua sucessora. PDFPageProxy.cleanup libera os
recursos de página e destruir o documento encerra seu worker.

O limite de páginas completas é menor que a proposta inicial de seis/três; miniaturas
possuem orçamento próprio. Não são mantidas 300 imagens/canvases. O teto teórico de
raster estável no desktop é 8,4 milhões de pixels, aproximadamente 32 MiB RGBA. Isso
**não mede memória total do processo**, decodificação de imagens, heap nem GPU.

## Evidência local

Máquina: MacBookAir10,1, 8 GiB RAM, 8 CPUs lógicas; Docker em contexto Colima.
Navegador interno do Codex, viewport observado de 1280 × 720. A API de override de
viewport não alterou essa aba; a verificação responsiva usou iframe local com viewport
real de conteúdo de 390 × 844 (não teste de hardware móvel). Harness temporário removido
antes do build final, screenshots fora do Git em `/tmp/revista-s02-evidence/`.

| Verificação | Resultado |
|---|---|
| Suite backend com PostgreSQL | 30 testes; arquivos, autorização, privacidade, Range, categorias, votos, idempotência e autenticação |
| Núcleo de navegação TS | 3 testes, percorrem limites de 1, 2, 299 e 300 páginas e janela de miniaturas |
| Upload pelo wizard | PDF textual real de 300 páginas → job → rascunho → preview privado → publicação → leitor público |
| HTTP real + Celery | Digitalizado 300, textuais 1/2/299 prontos; 301 reprovado; downloads comparados por SHA-256 |
| Download pelo navegador | SHA-256 `78c405c2c1aa82806b0efbce35359ba196912a468a284b69137442bf6fab4338`, igual ao fixture textual de 300 |
| Recuperação de worker | Upload permaneceu queued com worker parado e virou ready (2 páginas) após reinício; reenvios não duplicam publicação |
| Arquivamento pelo painel | Publicado → arquivado → rascunho, com estado confirmado na interface; sessão encerrada ao final |
| Links e busca | Link interno abre página 300; busca “Pagina 178 de” retorna a página correta |
| Navegação longa | Textual e digitalizado: 100 avanços e 50 retornos; amostras a cada 10 avanços: 2 páginas + até 10 miniaturas; até 1.471.224 pixels somados nos canvases de PDF |
| Desktop | Páginas duplas, zoom, ajuste, limites, entrada/saída de tela cheia e console sem erros em aba nova |
| Layout 390 px | Página 300 renderizada; scrollWidth=390, 1 página e 0 miniaturas |

Na sequência HTTP, envio + polling até pronto levou 0,57–0,70 s nos fixtures pequenos
(0,3 MiB textual e 3,9 MiB digitalizado), em rede local. Isso não mede o tempo da primeira
página do navegador nem comprova os alvos de 10 Mbps/80 ms. O script gerador é versionado;
os PDFs sintéticos e as credenciais temporárias de QA não entram no Git.

## Aceite ainda pendente

FUND-04: comparação executável alternativa e medição de heap/GPU/tempo de primeira página.
READ/QA: teste físico de toque, rede limitada, rotação/tamanhos mistos e navegadores adicionais.
VIS: comparação/aprovação do responsável e todos os breakpoints do painel.
Sprint 1: usuários, autores, pareceristas, configurações institucionais e rate limit dos votos.
Sprint 3: auditoria editorial, Nginx/HTTPS, retenção, backup/restauração, homologação, deploy
 e entrega operacional. Esses itens seguem abertos; telas antigas desses cadastros ainda
não representam persistência implementada.

Após a validação, as 5 publicações sintéticas, 7 arquivos enviados, categoria temporária
e conta de QA foram removidos do ambiente local. O portal inicia vazio, pronto para
conteúdo real, sem credencial de demonstração. Os fixtures reproduzíveis permanecem em /tmp.

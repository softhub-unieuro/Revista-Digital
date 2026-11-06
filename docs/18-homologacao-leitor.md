# Consolidação da Sprint 3 — leitor, rede e concorrência

Rodada de **04/11/2026**, posterior ao pacote Docker do PR #39. A base continua sendo
o frontend final fornecido pelo responsável. Não foi criada outra sprint nem contratado
host: esta entrega avança a homologação que permanecia aberta.

## Correções entregues

**Conflito editorial.** Cada publicação tem `edit_version` crescente. PATCH e ações
publish/archive/restore exigem `If-Match: "UUID:edit_version"`. A versão é conferida
depois de bloquear a linha no PostgreSQL, na mesma transação da gravação e do histórico.
Sem token: 428; token antigo/inválido: 412, sem alteração de dados ou auditoria falsa.
Campos somente leitura não permitem escolher a próxima versão pelo payload.

O frontend envia a versão lida. Se outra sessão já salvou, preserva o formulário,
bloqueia novo salvamento e oferece carregar os dados atuais, avisando para copiar textos
antes de substituí-los. O wizard usa a versão confirmada nas etapas de salvar/publicar.
A migração é aditiva e inicializa edições existentes na versão 1. Atualize frontend/API
juntos; abas antigas precisam recarregar para usar o contrato novo. Os clientes externos
também devem enviar o token. As versões do documento PDF e da edição têm propósitos distintos.

**Recuperação do leitor.** Recarregar PDF recria documento/worker e conserva a página e
a versão do arquivo da leitura atual, inclusive depois de uma tentativa que falhou.
Erros de transporte ganham orientação em português, sem URL interna/mensagem técnica.
Falhas de página oferecem repetição e a busca textual pode ser cancelada.
Não há promessa de retomar a posição depois de fechar a aba ou recarregar todo o site.

**Limite de bytes.** Excesso de tamanho detectado na API retorna 413 e informa o limite,
em vez de erro genérico de formulário 400. O limite continua em 200 MiB/300 páginas.

## Provas executadas

Ambiente: MacBook Air Apple Silicon, 8 GiB, PostgreSQL/Redis/Celery em Colima; navegador
integrado CUA. Browser plugin não disponível. Banco de testes separado da aplicação.
`make check`: **54 testes backend e 5 Node**, lint, tipos, migrações sem divergência,
build e npm audit sem vulnerabilidades. `make schema` valida OpenAPI sem avisos.

Seis testes novos de concorrência cobrem ausência/token inválido, versão obsoleta,
as três ações editoriais e duas conexões simultâneas disputando save/archive. Exatamente
uma aceita a gravação; a outra recebe 412. Na interface, duas abas com descrições
conflitantes reproduziram a rejeição, conservaram o segundo texto e carregaram o primeiro
texto confirmado após a ação explícita do usuário.

`capacity_probe.py` enviou seis PDFs com até três uploads concorrentes, seguidos de um
arquivo grande: 1, 2, 299 e 300 páginas de texto, digitalizado 300, misto/rotacionado 300
e arquivo de **209.501.481 bytes (199,796 MiB)**. Todos processados e publicados. Um arquivo
com 200 MiB + 1 byte foi recusado com 413. O fixture grande usa um anexo de preenchimento;
isso mede transporte/armazenamento/hash, não decodificação de 200 MiB de fotografias.

| Medida HTTP local | Resultado observado |
|---|---|
| Recepção dos seis arquivos pequenos | 27–62 ms |
| Fila + processamento dos seis pequenos | 218–452 ms |
| Recepção do arquivo grande | 1.495 ms |
| Fila + processamento do arquivo grande | 233 ms |
| Range concorrente | 28 requisições, até 8 simultâneas; bytes/Content-Range corretos |
| Latência Range | Mediana 65 ms, máximo 117 ms |

Essas medições são uma execução local e não representam capacidade do servidor final.
O worker continua com um processo por vez; uploads concorrentes entram na fila. O worker
também foi parado: um job sintético de 2 páginas permaneceu queued no banco/Redis e
ficou ready após o reinício, com o mesmo identificador de documento.

## Rede e superfícies no navegador

O utilitário `qa_gateway.py` serve o build estático e encaminha leituras à API local,
com 10 Mbps **por conexão**, atraso fixo de 80 ms **por resposta** e cache desativado.
Isso não emula TCP móvel, perda de pacotes nem banda agregada do host. Há controle local
para devolver 503 somente no PDF, sem desligar serviços ou desativar autenticação/TLS.

| Verificação | Resultado |
|---|---|
| Documento digitalizado pronto para o leitor | 8.798 ms entre início da consulta de metadados e primeira página obtida pelo PDF.js |
| Digitalizado: navegação sem animação | 100 avanços + 50 retornos; índice e páginas coerentes |
| Amostras durante navegação | 2 páginas + até 10 miniaturas; 1.471.224 pixels de canvas somados |
| Tempo de render das amostras | 54–62 ms por página, após os dados estarem disponíveis |
| PDF grande pronto | 2.271 ms; última página renderizada em 33 ms |
| Transporte do PDF grande até a página 300 | 408.873 bytes observados no gateway; anexo de preenchimento não baixado inteiro |
| Falha e recuperação desktop | PDF 503 após recarga na página 178; nova tentativa retomou 178–179 da mesma versão |
| Tela de 390×844 | Páginas 2, 7, 14, 299, 300 do PDF misto; 1 canvas, 0 miniaturas, scrollWidth 390 |
| Rotação/tamanhos mistos em 390 px | 371.400–699.160 pixels por amostra; controles utilizáveis |
| Falha móvel | Orientação em português e botão de repetição; retorno à página 300 |

O tempo de documento pronto exclui o download inicial do bundle e não é uma medição
precisa do primeiro pixel pintado. As medidas de canvas não são heap, GPU ou memória
total. O digitalizado de teste precisou de quase todo o arquivo para sua abertura;
Range não garante abertura parcial de todo PDF não linearizado. A disposição dos objetos
do arquivo influencia o carregamento. Não extrapolar os tempos para PDFs arbitrários.

`data-document-ready-ms` no leitor e `data-render-ms` nos canvases fornecem os tempos
locais usados nessa verificação, sem telemetria externa ou dados pessoais. As capturas
de conflito/recuperação e mobile são entregues no chat; fixtures e credenciais de QA não
são versionados nem carregados automaticamente em produção.

## Repetir as provas

```bash
uv run --project backend python scripts/generate_pdf_fixtures.py --large
npm run build --prefix frontend
python3 scripts/qa_gateway.py --root frontend/dist --control /tmp/revista-qa-network.json --report /tmp/revista-qa-network.jsonl
```

O gateway escuta apenas `127.0.0.1:15174`; é ferramenta de QA, sem suporte a deploy ou
escritas administrativas. `{ "fail_pdf": true }` no arquivo de controle ativa a falha;
`{}` restaura a rede. Pare o processo ao concluir. Use o portal normal em 15173 para login.

Para a prova HTTP, crie uma conta temporária `@qa.local.test`, com nome iniciado por QA,
e um JSON privado (modo 600) contendo e-mail/senha. Não registre esse arquivo no Git:

```bash
python3 scripts/capacity_probe.py --credentials /caminho/privado/qa.json --include-large --output /tmp/capacidade.json
```

O programa exige origem HTTP em loopback e conta de QA; cria publicações sintéticas.
Remova somente os registros/arquivos dessa conta depois da prova, preservando dados reais.
Não reutilize credenciais de produção. O teste HTTPS do CI continua usando um projeto
Docker descartável e agora também confirma rejeição de versão editorial obsoleta.

## Pendências que continuam abertas

Heap/GPU, concorrência de leitores completos em múltiplos aparelhos, dispositivos físicos,
matriz Firefox/Safari/Edge/Chrome e toque, revisão completa de acessibilidade, comparação
executável da alternativa de animação e aceite visual humano. O plano de produção ainda
precisa de host/domínio, renovação TLS, cópia externa/agendamento de backups, alertas com
responsável, treinamento e aceite. Esta rodada não encerra esses critérios nem cria v1.0.0.

Referências: [ciclo de vida PDF.js](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib-PDFDocumentProxy.html)
e [If-Match/412](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/412).

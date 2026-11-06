# PDFs de até 300 páginas e leitor

## Capacidade que precisa ser comprovada

A base recebida mostrava HTML fictício. A implementação atual abre PDFs reais de 1 a
300 páginas; evidências e limitações em [Sprint 2](14-sprint2-pdf-real.md). Os itens abaixo
registram o plano e os alvos de homologação. Contador em 300 não comprova suporte.
O limite de bytes é independente: proposta inicial de 200 MiB, configurável e alinhada
entre proxy, API e worker.

## Pipeline de publicação

1. Receber em streaming e salvar em área temporária privada, sem nome de caminho fornecido pelo cliente.
2. Validar tamanho e identificação básica; criar upload e job duráveis.
3. Worker faz parse, conta páginas, verifica senha/integridade e calcula hash.
4. Rejeitar 0 ou mais de 300 páginas; informar o erro pelo job sem liberar publicação.
5. Extrair metadados necessários e gerar capa com limite de pixels.
6. Marcar ready somente após banco e arquivos estarem consistentes.
7. Administrador/editor confirma publicação. Nova versão falha não substitui a versão vigente.
8. Limpar temporários, versões expiradas e arquivos órfãos segundo retenção documentada.

Aplicar timeout e limite de memória ao worker; renderizador separado do servidor web.
Usar [pypdf](https://pypdf.readthedocs.io/en/stable/) para inspeção e avaliar
[pypdfium2](https://pypdfium2.readthedocs.io/en/stable/) para rasterização de capa em FUND-04.
Confirmar manutenção, versão e comportamento antes de fixar dependências. Não gerar
300 imagens em alta resolução como pré-condição para publicar.

## Renderização no navegador

PDF.js e worker da mesma versão, carregados sob demanda ao entrar no leitor. Renderizar
páginas visíveis e uma janela pequena de vizinhas. Orçamento inicial: até seis canvases
de página em desktop e três no celular, com teto de pixels por canvas. Cancelar trabalho
obsoleto, limpar canvases e liberar URLs ao trocar documento ou sair do leitor.

Solicitar partes do arquivo com HTTP Range quando suportado. Medir os bytes e as
respostas 206 no ambiente final; um PDF e sua estrutura interna podem exigir leituras
distintas. Fonte: [FAQ do PDF.js](https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions).

## Índices e navegação

Guardar página selecionada de forma única. A implementação usa base 1 de ponta a ponta
na interface e converte destinos internos do PDF.js quando necessário.

- Celular: uma página por vez; próxima soma um, anterior subtrai um.
- Desktop: capa isolada; depois pares 2–3, 4–5 e assim por diante, respeitando a última página.
- Por padrão, computadores mostram duas páginas e celulares uma. Os controles permitem escolher explicitamente uma ou duas páginas; a preferência manual permanece enquanto a tela é redimensionada.
- No zoom ajustado, o leitor dimensiona as páginas pela largura e altura realmente disponíveis no canvas; o modo de página única aproveita a altura livre.
- Mudar de tamanho preserva a página selecionada dentro do par correspondente.
- Documento de 1 página não avança; documento de 300 nunca tenta renderizar a 301.
- Indicador informa exatamente as páginas visíveis.
- Deslize navega em zoom ajustado; em zoom ampliado, arrasto move a página sem saltar edição.
- Teclado e clique continuam disponíveis; salto direto valida o intervalo.
- Nova animação não pode atualizar o índice duas vezes em evento repetido.

O comportamento a evitar é esconder a segunda página no celular e continuar somando dois.
O teste deve percorrer todas as páginas e provar que nenhuma página par fica inacessível.

## Animação

Em duas páginas, a navegação avança o fólio da direita para a esquerda e volta o fólio
da esquerda para a direita, mantendo as páginas que não viram no lugar. Em página única,
a página atual vira para revelar a próxima ou a anterior. A frente da folha e seu verso
são renderizados só durante a transição, sem carregar o livro inteiro.
Respeitar prefers-reduced-motion. Usuário deve conseguir ler e navegar sem animação.
Texto selecionável e links não podem ser encobertos pela camada de gestos.


## Matriz de arquivos

| Arquivo | Resultado esperado |
|---|---|
| PDF textual de 1 página | Abre, capa correta, sem próximo |
| PDF de 2 páginas | Ambas acessíveis nos dois modos |
| PDF textual de 299 e de 300 páginas | Nenhuma página perdida; limites corretos |
| PDF escaneado de 300 páginas | Abre sem renderizar tudo; zoom legível |
| PDF de 301 páginas | Job reprovado; publicação bloqueada |
| Arquivo acima de 200 MiB | Rejeitado pelo limite configurado, sem órfãos |
| PDF com senha, corrompido ou falso | Erro claro; sem travamento ou publicação |
| Páginas rotacionadas ou tamanhos mistos | Capa e navegação preservadas |
| Rede interrompida e pedido parcial inválido | Erro recuperável; Range inválido retorna 416 |

Arquivos de teste devem ser reproduzíveis e autorizados. Não guardar grandes PDFs no
histórico Git; usar geração de fixtures e armazenamento de testes documentado.

## Metas iniciais de desempenho

Metas a validar/calibrar em FUND-04 e confirmar em QA-03, não resultados já atingidos:

- Arquivo textual com 300 páginas e até 25 MiB: primeira página em até 4 s.
- Arquivo escaneado de 300 páginas dentro do limite: alvo de primeira página em até 8 s.
- Página já no cache: resposta ao comando em até 150 ms, sem incluir duração da animação.
- Animação em torno de 350–500 ms, configurável; comandos rápidos não corrompem o índice.
- Cache mantém o teto de canvases/pixels durante 100 avanços e 50 retornos.
- Memória estabiliza após navegação repetida, sem crescimento contínuo a cada página.

Perfil de comparação inicial: desktop com 8 GB de RAM, navegador atual; celular real
de referência a registrar; rede simulada em 10 Mbps/80 ms e caso de rede limitada.
Registrar CPU, dispositivo, navegador, tipo/tamanho de PDF e estado do cache junto à
medição. Metas inviáveis devem gerar ajuste explícito no plano antes do aceite.

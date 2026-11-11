export const editions = [
  { id: 12, slug: 'saude-mental-transformacao', issue: 'N. 12', month: 'Outubro', year: 2024, title: 'Saúde Mental em Tempos de Transformação', subtitle: 'Desafios contemporâneos da saúde mental, com abordagens interdisciplinares sobre bem-estar, subjetividade e contextos sociais em mudança.', pages: 124, cover: '/covers/cover-hero.png', categories: ['Saúde Mental', 'Psicologia Social'], rating: 4.8, ratings: 52, status: 'Publicado' },
  { id: 11, slug: 'relacoes-humanas-bem-estar', issue: 'N. 11', month: 'Abril', year: 2024, title: 'Relações Humanas e Bem-Estar', subtitle: 'Diálogos entre indivíduo, vínculos, comunidade e qualidade de vida.', pages: 112, cover: '/covers/cover-11.png', categories: ['Psicologia Social', 'Psicologia Familiar'], rating: 4.6, ratings: 34, status: 'Publicado' },
  { id: 10, slug: 'psicologia-educacao', issue: 'N. 10', month: 'Dezembro', year: 2023, title: 'Psicologia e Educação', subtitle: 'Práticas, aprendizagem e caminhos para novos futuros.', pages: 98, cover: '/covers/cover-10.png', categories: ['Psicologia Escolar'], rating: 4.5, ratings: 29, status: 'Publicado' },
  { id: 9, slug: 'diversidade-inclusao', issue: 'N. 09', month: 'Agosto', year: 2023, title: 'Diversidade e Inclusão', subtitle: 'Perspectivas para uma sociedade plural e relações mais inclusivas.', pages: 104, cover: '/covers/cover-09.png', categories: ['Psicologia Social'], rating: 4.7, ratings: 40, status: 'Publicado' },
  { id: 8, slug: 'desenvolvimento-humano', issue: 'N. 08', month: 'Abril', year: 2023, title: 'Desenvolvimento Humano ao Longo da Vida', subtitle: 'Teoria, pesquisa e práticas sobre desenvolvimento humano.', pages: 96, cover: '/covers/cover-08.png', categories: ['Desenvolvimento Humano'], rating: 4.3, ratings: 23, status: 'Publicado' },
  { id: 7, slug: 'processos-psicologicos', issue: 'N. 07', month: 'Dezembro', year: 2024, title: 'Processos Psicológicos Contemporâneos', subtitle: 'Leituras atuais sobre subjetividade, cognição e comportamento.', pages: 110, cover: '/covers/cover-2.svg', categories: ['Saúde Mental'], rating: 4.5, ratings: 19, status: 'Publicado' },
  { id: 6, slug: 'psicologia-sociedade-politicas', issue: 'N. 06', month: 'Agosto', year: 2024, title: 'Psicologia, Sociedade e Políticas Públicas', subtitle: 'Pesquisa e atuação psicológica em contextos sociais e institucionais.', pages: 102, cover: '/covers/cover-1.svg', categories: ['Psicologia Social'], rating: 4.4, ratings: 17, status: 'Publicado' },
  { id: 5, slug: 'subjetividade-cultura', issue: 'N. 05', month: 'Abril', year: 2024, title: 'Subjetividade e Cultura', subtitle: 'Indivíduo, linguagem, cultura e formas contemporâneas de existência.', pages: 88, cover: '/covers/cover-3.svg', categories: ['Psicologia Social'], rating: 4.3, ratings: 14, status: 'Publicado' },
  { id: 4, slug: 'familia-desenvolvimento', issue: 'N. 04', month: 'Dezembro', year: 2023, title: 'Família e Desenvolvimento', subtitle: 'Vínculos, cuidado e desenvolvimento ao longo da vida.', pages: 92, cover: '/covers/cover-6.svg', categories: ['Psicologia Familiar'], rating: 4.2, ratings: 11, status: 'Publicado' },
  { id: 3, slug: 'aprendizagem-inclusao', issue: 'N. 03', month: 'Agosto', year: 2023, title: 'Aprendizagem e Inclusão', subtitle: 'Escola, diversidade e práticas educacionais inclusivas.', pages: 94, cover: '/covers/cover-5.svg', categories: ['Psicologia Escolar'], rating: 4.5, ratings: 16, status: 'Publicado' },
  { id: 2, slug: 'neuropsicologia-pratica', issue: 'N. 02', month: 'Abril', year: 2023, title: 'Neuropsicologia: Ciência e Prática', subtitle: 'Cognição, avaliação e intervenção em diferentes contextos.', pages: 108, cover: '/covers/cover-4.svg', categories: ['Neuropsicologia'], rating: 4.7, ratings: 22, status: 'Publicado' },
  { id: 1, slug: 'psicologia-clinica-contemporanea', issue: 'N. 01', month: 'Dezembro', year: 2022, title: 'Psicologia Clínica Contemporânea', subtitle: 'Escuta, cuidado e novas perspectivas para a prática clínica.', pages: 86, cover: '/covers/cover-2.svg', categories: ['Saúde Mental'], rating: 4.4, ratings: 20, status: 'Publicado' },
]

export const categories = [
  { name: 'Saúde Mental', slug: 'saude-mental', count: 26, icon: 'brain' },
  { name: 'Psicologia Escolar', slug: 'psicologia-escolar', count: 18, icon: 'school' },
  { name: 'Psicologia Familiar', slug: 'psicologia-familiar', count: 14, icon: 'family' },
  { name: 'Psicologia Social', slug: 'psicologia-social', count: 12, icon: 'network' },
  { name: 'Desenvolvimento Humano', slug: 'desenvolvimento-humano', count: 9, icon: 'leaf' },
  { name: 'Neuropsicologia', slug: 'neuropsicologia', count: 8, icon: 'nodes' },
]

export const adminRows = [
  ...editions.slice(0, 8),
  { id: 13, slug: 'processos-emocionais', issue: 'N. 13', month: 'Novembro', year: 2026, title: 'Processos Emocionais e Vida Cotidiana', pages: 136, cover: '/covers/cover-3.svg', categories: ['Saúde Mental'], rating: 0, ratings: 0, status: 'Rascunho' },
]

# LG webOS TV — tela inicial própria e limpeza

Projeto pessoal: deixei minha TV **LG NanoCell (webOS 6, 2021)** mais rápida e com cara de console, trocando a tela inicial da LG por uma tela própria estilo PS5 e removendo o excesso de anúncios e apps.

Este repositório traz a **parte de personalização** — o launcher e as modificações da tela inicial — mais um **relato técnico** do processo. Ele **não** inclui código de exploit: o root foi feito com o método público da comunidade webOS (veja os créditos), que não é republicado aqui.

## Por que

A interface da webOS estava lenta e cheia de anúncios, recomendações e apps que eu não uso. Em vez de só reclamar, fui atrás de deixar a TV do meu jeito: uma tela inicial limpa, rápida, que abre direto no que importa, e um modo de jogos retrô usando os meus próprios backups.

A webOS não pode ser substituída (o sistema é fechado e mexer demais "brica" a TV), então "limpar" aqui significa **desativar e bloquear**, nunca apagar partes do sistema.

## Como foi feito (visão geral)

1. **Verificação de firmware.** Confirmei a versão da TV e se ela era passível de root pelo método da comunidade.
2. **Root pela comunidade webOS.** Usei o **Homebrew Channel** (webosbrew) e um exploit público já conhecido (CVE-2025-38352). O código do exploit é de outros autores e está creditado abaixo — não faz parte deste repositório.
3. **Descoberta interessante na persistência.** O root não sobrevivia ao reinício. A causa estava em `/etc/init/devmode.conf`: no boot, o sistema faz uma **verificação de assinatura** de um script do modo desenvolvedor; quando o arquivo existe mas a assinatura não confere (e nunca confere, porque a chave privada é da LG), o boot **apaga** a pasta do modo desenvolvedor e os apps. A correção foi simplesmente **não deixar esse arquivo existir** — sem ele, o boot pula a verificação inteira e a personalização sobrevive. Esse diagnóstico está em [`home-mods/README-engenharia-reversa.md`](home-mods/README-engenharia-reversa.md).
4. **Limpeza (debloat).** Bloqueio de dezenas de domínios de anúncio e telemetria da LG pelo `/etc/hosts`, e remoção de apps que eu não uso pela própria tela da TV.
5. **Tela inicial própria.** Um launcher em HTML/CSS/JS estilo PS5 (pasta [`launcher/`](launcher/)) e ajustes no `home.xml` da webOS (pasta [`home-mods/`](home-mods/)).
6. **Jogos retrô.** RetroArch instalado pela loja da comunidade (webosbrew), rodando **apenas os meus próprios backups** — este repositório não inclui nenhuma ROM.

## O que tem aqui

| Pasta | O que é |
|---|---|
| [`launcher/`](launcher/) | A tela inicial estilo PS5 (app webOS em HTML/CSS/JS): carrossel de apps, barra com relógio, clima, entradas HDMI, rede e ajustes. Os ícones dos apps são lidos da própria TV em tempo de execução. |
| [`home-mods/`](home-mods/) | Modificações do `home.xml` da webOS (reorganização da tela da LG) e o relato de engenharia reversa de como o layout funciona, com as ferramentas que usei para testar a navegação por tecla e tirar prints da TV. |

## Detalhes legais do launcher

- O **clima** usa a API gratuita Open-Meteo (sem chave). As coordenadas no código são um exemplo (`0, 0`); troque pelas da sua cidade.
- O launcher **chama serviços da própria TV** (via a ponte de serviço da webOS) para listar e abrir apps, ler o estado da rede e trocar de entrada.
- Os scripts de deploy usam SSH como `root` com a senha `alpine` — que é o **padrão público** do Homebrew Channel após o root, não um segredo. O endereço da TV vem da variável de ambiente `TV_HOST`.

## Aviso

Mexer no sistema de uma TV tem risco de inutilizá-la (brick). Isto é um **registro técnico** do que fiz no meu próprio aparelho, não um passo a passo para reproduzir. Faça por sua conta e risco.

## Créditos

- **[webosbrew / Homebrew Channel](https://github.com/webosbrew)** — a comunidade de homebrew da webOS, o Homebrew Channel e a documentação de root.
- **CVE-2025-38352** e o exploit público usado para o root — de seus respectivos autores. O código do exploit **não** está neste repositório; procure o projeto original da comunidade.
- **[RetroArch](https://www.retroarch.com/)** — o emulador, instalado pela loja da webosbrew.

## Licença

[MIT](LICENSE) para o código e os textos deste repositório.

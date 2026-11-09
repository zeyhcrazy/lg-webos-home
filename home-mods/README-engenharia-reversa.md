# Engenharia reversa da Início padrão da LG (webOS 6 — com.webos.app.home)

TV: LG 55NANO80TSA, webOS 6, rooted. App Início = **Flutter v2.0.0** em
`/usr/palm/applications/com.webos.app.home` (46,7 MB). `/usr` é **overlay READ-ONLY**
(`lowerdir=/overlay/bsppart/bsp/usr:/usr`), então nada escreve direto lá —
mexemos por **bind-mount** (mesma técnica das animações com `wam-conf.sh`).

## Como a tela é montada

O layout NÃO é todo compilado: vem de XMLs em
`data/flutter_assets/assets/`:

| Arquivo | Quando é usado |
|---|---|
| `home.xml` | **modo normal (o ativo nesta TV)** |
| `home_wee.xml` | modo "wee" / simples |
| `home_senior.xml` | modo sênior |
| `home_lg.xml` | variante ShelfView (não usada aqui) |
| `/mnt/platform-plugins/conf/home_layoutShelfView.xml` | variante ShelfView externa — **read-only, nem existe nesta TV** |

Cada `<item>` do `home.xml` é uma fileira (shelf), na ordem da tela.
**Esconder uma fileira = colocar `itemWidth="0" itemHeight="0" focusType="none"`**
(é o que a própria LG faz em `quickGuide`, `localKeyGuide`, `recentApps`).

### Fileiras do home.xml e o que cada uma é na tela

| id no XML | O que aparece | Mexer? |
|---|---|---|
| `container` → `globalline` | coluna esquerda: perfil, sino, engrenagem, busca | **não** (quebra navegação) |
| `container` → `herobanner` | banner de topo "Inicie uma nova experiência com webOS" + "Acesse o Apps" | pode esconder |
| `qcardList` | cartão "Editar" | pode esconder |
| `appList` | **seus apps** (APPS, streamings, RetroArch, lápis) | **não** (é o que você usa) |
| `recommendedShelf` | **"Entrada Recente" + "Funções do Dispositivo"** (GUIA, Guia do Usuário, Hub Inicial) | **pode esconder — é o alvo** |
| `quickGuide` | já escondido (0x0) | — |

Confirmação da identidade do `recommendedShelf` nas strings do `libapp.so`:
`RecommendedShelf`, `isRecommendShelf`, `[DeviceFunctionProvider] showTVGuideTile:`,
`moveToUserGuide`, `com.webos.app.tvuserguide`, `com.webos.app.tvguidejpn`, `Home Hub`.
Ela aparece como *fallback* porque as recomendações estão desligadas — quando não há
recomendação/anúncio, a LG preenche o espaço com os cards de "Funções do Dispositivo".

## O que dá pra mudar — 2 caminhos

### A) Ajustes (settings) — seguro, reversível, sem risco
Já aplicados no debloat anterior e verificados agora:
- `homePromotion = off`
- `contentRecommendation = off`
- `homeEffect = off` (animações da home)
- `bannerPosition = none`

Outro lever disponível:
- `webOSPromotionVideo` (`on`→`off`): tira o vídeo promocional do banner de topo.

Via luna (somos root):
`luna-send -n 1 -f luna://com.webos.settingsservice/setSystemSettings '{"category":"option","settings":{"webOSPromotionVideo":"off"}}'`

### B) Override do layout por bind-mount — reversível, precisa de root + boot hook
Arquivos deste diretório:
- `home.xml` — cópia do original com `recommendedShelf` zerado (some "Funções do Dispositivo").
- `apply-home-mods.sh` — faz/desfaz o bind-mount (`apply-home-mods.sh off` reverte).
- `92-home-mods` — hook HBC (`/var/lib/webosbrew/init.d/`) que reaplica no boot.

Deploy: copiar `home.xml` + `apply-home-mods.sh` p/ `/media/developer/home-mods/`,
`92-home-mods` p/ `/var/lib/webosbrew/init.d/`, rodar o apply e **reiniciar** (a Início
relê o XML ao subir). Reverter: `apply-home-mods.sh off` (ou apagar o hook) + reboot.

## Estado final aplicado (2026-10-20)
`home.xml` deste diretório é o que está na TV (mesmo md5). Layout no topo:
`margin 45` / `container` 3840x640 **focusType="none"** [**herobanner 0x0 PRIMEIRO**, `globalline` 300x640 scope]
/ `margin 80` / `appList` 3840x248 autoFocus / `margin 1147` / `quickGuide` 0x0 (total = 2160).
Ícones em coluna no topo-esquerdo, carrossel logo abaixo. `qcardList` e `recommendedShelf` **removidos**
(não só 0x0 — shelf com conteúdo precisa ser removido, senão vira fantasma de foco + rótulo).

Navegação verificada com print a cada tecla: **CIMA de qualquer app → G**; descendo pelos ícones
volta pro app onde estava; BAIXO nos apps não cai em fantasma; esquerda/direita normais.

### Aprendizados de foco/render (importantes)
- **Modelo real de navegação**: CIMA/BAIXO pulam pra prateleira anterior/seguinte (precisa sobrepor
  na horizontal — por isso o `container` tem que ter largura total 3840); ESQUERDA/DIREITA só andam
  dentro da prateleira. A lista de apps **trava** esquerda no 1º item e cima quando não há nada acima
  (não é loop). Consequência: com apps **ao lado** dos ícones (mesmo container) não existe tecla que
  leve dos apps aos ícones — por isso o layout final empilha ícones em cima e apps embaixo.
- **`herobanner` tem que ficar no mesmo `container` que `globalline`** — remover, deixar o container
  sem ele, ou pôr num container separado = TELA PRETA (testado 3x).
- `itemX`/`itemY`/`type` são ignorados no layout overlay (`type="row"` não põe prateleiras lado a lado).
- `herobanner` primeiro na ordem + `container` com `focusType="none"` = sem fantasmas de foco.
- Margem de 80 entre ícones e apps: com 20 o APPS selecionado (que cresce) encosta na lupa.

### Ferramentas de teste (sem precisar do controle)
- `deploy_home.py [xml]` — sobe o XML, remonta e recarrega a Início (mata todos os processos dela).
- `tvnav.py <pasta> "cap:a LEFT cap:b UP cap:c"` — injeta teclas no `/dev/input/event1` e tira print
  via `luna://com.webos.service.capture/executeOneShot`.
- `sheet.py <saida.png> "arq.png=rótulo" ...` — monta uma folha comparando os prints.
- Esperar ~10 s depois do reload antes de testar: logo após subir, a Início ainda está inicializando
  e o foco se comporta diferente (dá falso positivo).
- Persistência: hook `92-home-mods` monta o home.xml e **mata a Início** no boot (ela sobe antes do init.d e cacheia o XML; sem o kill o reboot não aplica). **Ordem do boot (corrigido 2026-10-20):** o HBC roda os hooks em fila (`run-parts`) e o `90-performance` tinha um `sleep 45` em primeiro plano que atrasava o 92 até depois da Início subir (~87s de uptime) → layout original por ~40s ao ligar. Agora o sleep do 90 é em segundo plano, o 92 roda ~30s ANTES da Início, e ela já lê os arquivos modificados (testado com reboot + captura: primeira Início já no layout novo, sem kill). O kill só acontece se a Início já estiver aberta quando o hook montar (3s depois, e reabre via `luna-send` se o SAM não reabrir em 2s). Log: `/tmp/home-mods.log`. Aplicar sem reboot: trocar fonte + `apply-home-mods.sh` + `kill -9 $(pgrep -f com.webos.app.home)` + relançar.
- **Fundo/wallpaper**: inviável — Início é transparent e o recurso depende do app `artisticdisplay`, removido no debloat.

## Banner com imagem própria (aurora) — 2026-10-20
O app Início não tem wallpaper e só é transparente sobre o **plano de vídeo** (Live TV/HDMI) —
apps atrás ficam pretos. O único lugar pra imagem é o **banner** (`herobanner`): a imagem padrão dele
(o carro na estrada) é o arquivo `assets/images/{4k,2k,hd}/bg_banner_img.png` (3492x900 / 1746x450 /
1264x326), e os textos "Inicie uma nova experiência com webOS." / "Acesse o Apps" vêm de `assets/i18n/pt.json`.
- `make_bg.py <saida>` gera a aurora (ondas de luz azul/roxo/verde-água que somem no preto) nas 3 resoluções → `bg/`.
- `pt.json` = cópia do original com 'Start a new experience with webOS.', 'Go to Apps' e 'Smart experience with webOS' vazios.
- `home.xml` reativa o banner: `container` [globalline 300x640, herobanner 3492x640]. **Sem os textos o banner fica
  sem botão e não pega foco** — CIMA de qualquer app continua indo pro G (verificado por print).
- `apply-home-mods.sh` monta os 5 arquivos (home.xml, 3 imagens, pt.json); `off` desmonta todos.
  **Pegadinha:** `assets/i18n` é link simbólico p/ `/mnt/lg/wee/ui_l10n/...` — o kernel registra o mount no caminho
  real, então o script usa `readlink -f` (senão não reconhece que já montou, o `off` pula e o `apply` empilha).
- **A LG ENCAIXA a imagem inteira no espaço (contain), não corta.** Então o PNG tem que ter o formato exato do
  herobanner do home.xml: hoje 3492x640 (4K), 1746x320 (2K), 1264x232 (HD). Com 3492x900 ela encolhe e fica uma
  "janelinha" com bordas pretas.
- Imagem atual (escolhida pelo usuário): **cidade à beira do lago com montanhas nevadas ao entardecer**, Unsplash
  (https://unsplash.com/photos/NEcxEGEVdY8, licença Unsplash, 5539x3116), original em
  `bg/cidade_lago_montanhas_unsplash_NEcxEGEVdY8.jpg`, gerada com `make_banner.py <foto> <saida> 0.34 0.42 center 640`.
- Antes: **vila com barcos no lago** do Windows Spotlight, original salva em
  `bg/vila_lago_spotlight_1920x1080.jpg` (`make_banner.py bg/vila_lago_spotlight_1920x1080.jpg <saida> 0.326 0.51 center 640`).
  Alternativas prontas: `bg/lago_por_do_sol_*` e `bg/aurora_*`.
- Antes: **pôr do sol no lago** do próprio Windows (`C:\Windows\Web\Screen\img102.jpg`, 6400x4000), gerada com
  `python make_banner.py C:/Windows/Web/Screen/img102.jpg <saida> 0.31 0.49 center 640` (fração da altura mostrada,
  centro vertical, alinhamento, altura do espaço). `bg/aurora_*` = a versão gerada antes (alternativa).
- Outras boas do PC: wallpapers do Windows em `C:\Windows\Web\Wallpaper\*` (3840x2400) e `C:\Windows\Web\Screen\*`,
  e as do Windows Spotlight em `%LOCALAPPDATA%\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets`.
- Trocar a imagem: gerar/colocar PNGs nesses 3 tamanhos em `/media/developer/home-mods/bg/` e recarregar a Início.

### Banner "quase tela cheia" (atual, 2026-10-20)
Tela cheia de verdade (imagem atrás de tudo) é impossível: a Início é fila de prateleiras sem camadas e só é transparente
sobre o vídeo da TV. O mais perto: `container` com **1747** de altura [globalline 300x1747, herobanner 3492x1747],
margem 30, appList 248, margem 90 (soma 2160) → a foto cobre quase a TV toda e os apps ficam numa faixa embaixo.
Imagem gerada com `make_banner.py <foto> <saida> 0.89 0.5 center 1747 0` (PNGs 3492x1747 / 1746x873 / 1264x632);
o último arg `0` = sem vinheta. **Escolhida pelo usuário: COM vinheta** (padrão, sem o `0`) — as bordas se apagam no
preto e disfarçam a coluna de ícones e a faixa de apps (sem vinheta aparece a borda reta da foto; ele testou e achou pior).
A versão limpa ficou em `bg/cidade1747_limpa_*`; a com vinheta = `bg/cidade1747_vinheta_*` = a atual. Se a foto ficar poucos px mais estreita que o
espaço, o gerador estica em vez de preencher a borda (senão aparecia uma faixa de degradê na esquerda).
Navegação verificada por print: CIMA de qualquer app → G; descendo os ícones volta pro app onde estava.
A versão anterior (banner 640, apps logo abaixo dos ícones) ficou em `home_banner640.xml` + `bg/cidade640_*`.

## Apps ocultos
Os 9 da "Lista de aplicativos ocultos": 8 de sistema (LG Channels, Hub Inicial, Esportes, Reprodutor de Mídia, Alexa,
Câmera, LG Gallery+, Live TV) + **Homebrew Channel (ícone rosa da caneca — NÃO remover, é o root)**. Nenhum roda em
segundo plano nem gasta memória/animação (os ícones só carregam na tela "Editar lista"). Não dá pra tirá-los da lista:
`removeLaunchPoint` recusa app de sistema, `updateLaunchPoint {visible:false}` não grava nada, e o gerenciador de apps
não tem rescan — deixados como estão.

## O que NÃO dá / quebra
- **Escrever em `/usr` ou `/mnt/platform-plugins`** — overlay read-only. Só bind-mount.
- **Editar a lógica compilada** (`libapp.so`, `DeviceFunctionProvider`) — frágil, não vale.
- **Remover `appList` ou `globalline`** — quebra o uso básico da tela.
- **Substituir a Início inteira** por bind-mount sobre o app — o SAM cacheia o tipo
  "flutter" e renderiza errado (já testado e documentado). Pra trocar a Início de verdade,
  o caminho é o launcher próprio (`tld.my.customhome`) como app separado + serviço da tecla Home.
- **Reiniciar só o processo da Início por SSH** é instável (SAM pode travar); reboot limpo
  (`/sbin/reboot`) é o jeito confiável de aplicar.

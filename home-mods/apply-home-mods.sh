#!/bin/sh
# ============================================================
# LG 55NANO80TSA (webOS 6) - Mods na Inicio padrao da LG
# ------------------------------------------------------------
# /usr e overlay READ-ONLY: cada arquivo modificado e sobreposto
# por bind-mount (mesmo truque das animacoes com wam-conf.sh).
#   home.xml          -> layout (icones no topo, apps embaixo,
#                        sem "Editar"/"Funcoes do Dispositivo")
#   bg/bg_banner_img_* -> imagem do banner (aurora) em 4k/2k/hd
#   pt.json           -> textos do banner LG esvaziados
# Uso: apply-home-mods.sh        (aplica)
#      apply-home-mods.sh off    (reverte tudo pro original)
# ============================================================
D=/media/developer/home-mods
A=/usr/palm/applications/com.webos.app.home/data/flutter_assets/assets

PAIRS="$D/home.xml:$A/home.xml
$D/bg/bg_banner_img_4k.png:$A/images/4k/bg_banner_img.png
$D/bg/bg_banner_img_2k.png:$A/images/2k/bg_banner_img.png
$D/bg/bg_banner_img_hd.png:$A/images/hd/bg_banner_img.png
$D/pt.json:$A/i18n/pt.json"

bound() { grep -qF " $1 " /proc/self/mounts 2>/dev/null; }

echo "$PAIRS" | while IFS=: read -r SRC DST; do
    [ -n "$SRC" ] || continue
    # i18n/ e um symlink p/ /mnt/lg/wee/ui_l10n/...: o kernel registra o mount no caminho real
    DST=$(readlink -f "$DST")
    if [ "$1" = "off" ]; then
        while bound "$DST"; do umount -l "$DST" || break; done
        echo "revertido: $DST"
    else
        [ -f "$SRC" ] || { echo "falta $SRC (pulei)"; continue; }
        bound "$DST" || mount --bind "$SRC" "$DST"
        bound "$DST" && echo "OK: $DST" || echo "FALHOU: $DST"
    fi
done

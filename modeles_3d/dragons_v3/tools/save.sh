#!/bin/bash
# Sauvegarde le travail sur la branche dragons-v3-wip de robloxgame
set -e
W=/home/claude/work; R=/home/claude/robloxgame; D=$R/modeles_3d/dragons_v3
cd $W && python3 tools/etat.py
cd $R
git checkout -q dragons-v3-wip 2>/dev/null || git checkout -q -b dragons-v3-wip
mkdir -p $D
for x in kit data ref out tools; do rm -rf $D/$x; cp -r $W/$x $D/; done; find $D -name '*.full.py' -delete; find $D -name __pycache__ -prune -exec rm -rf {} +
cp $W/build.py $W/run_check.py $W/REPRISE.md $W/ETAT.md $D/
mkdir -p $D/renders
for f in $W/renders/*.png; do b=$(basename "$f" .png); [ -f "$D/renders/$b.jpg" ] && [ "$D/renders/$b.jpg" -nt "$f" ] && continue; python3 -c "from PIL import Image;import sys;i=Image.open(sys.argv[1]).convert('RGB');i.thumbnail((900,900));i.save(sys.argv[2],quality=78)" "$f" "$D/renders/$b.jpg"; done
[ -n "$1" ] && cp "$1" $D/ || true
git add -A modeles_3d/dragons_v3
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "Dragons v3 : sauvegarde du travail en cours ($(date +%H:%M))

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01CwxFA9SpcRrjuz2gzvR7rp" || echo "rien à sauvegarder"
git push -q -u origin dragons-v3-wip 2>&1 | tail -2
echo "sauvegarde OK"

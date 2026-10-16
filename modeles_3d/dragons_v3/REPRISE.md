# Reprise : docx des 42 dragons v3 (stylés selon la rareté)

Demande de Raboul : nouveau docx avec les 42 dragons × 3 stades (Bébé, Ado, Adulte), chacun avec un prompt
au format de l'exemple « Adulte Mirage » et un script Blender au niveau du Mirage v3, plus stylé selon la rareté.
Choix validés : les 126 stades ; économiser les crédits (sous-agents Sonnet, vérification dans Blender).

## Où sont les choses (dossier modeles_3d/dragons_v3 de la branche dragons-v3-wip)
- kit/kit.py : fonctions communes injectées à la place de `# @@KIT@@` ; kit/template.py : début de script ;
  kit/BRIEF.md : consignes complètes pour un sous-agent (budgets par rareté, stades, morphologies, rendu de rareté, format du prompt).
- data/<SLUG>.md : ancien prompt du dragon (palette, signes, descriptions) ; data/dragons.json : les 42 fiches.
- ref/ : prompt et script Mirage d'exemple, images de concept (mondes 1-2).
- out/<SLUG>/{BEBE,ADO,ADULTE}.py + *_prompt.md + report.json : le travail par dragon.
- build.py + run_check.py : `python3 build.py out/<SLUG>/ADULTE.py --render` (nécessite `pip install bpy`).
- renders/ : aperçus.

## État
Voir ETAT.md (mis à jour à chaque sauvegarde).

## Pour reprendre
Dire « reprends les dragons » dans la conversation Claude. Claude clone la branche, relit ETAT.md et continue
les dragons non finis, puis assemble le docx.

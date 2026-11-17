# Retraite 2027 — données des programmes

Fichier public lu par l'application Retraite 2027 :
`https://rangornrar.github.io/retraite2027-data/v1/scenarios.json`

- Chaque valeur modélisée porte sa source et sa date ; l'historique Git sert de journal public.
- Même grille pour tous les candidats : chaque paramètre est soit précisé et sourcé,
  soit marqué `{ "status": "unspecified" }` (l'app reprend alors la loi actuelle et l'affiche).
- Avant tout envoi : `python3 tools/valider.py v1/scenarios.json` (lancé aussi par GitHub Actions,
  qui publie sur GitHub Pages si tout est valide).
- Signaler une erreur : ouvrir une *issue* sur ce dépôt.

# Compare 2027 — données des programmes

Fichiers publics lus par l'application Compare 2027 (anciennement Retraite 2027) :

- `https://rangornrar.github.io/retraite2027-data/v1/scenarios.json` : retraites (loi actuelle, réforme 2023, candidats) ;
- `https://rangornrar.github.io/retraite2027-data/v1/fiscalite.json` : impôts des particuliers et des entreprises
  (loi 2026 et mesures fiscales des mêmes candidats). Un volet qu'un programme ne permet pas de chiffrer est listé
  dans `notComputable` : l'app le compte selon la loi actuelle et le signale.

**Ajouter ou retirer un candidat** : le faire dans les deux fichiers (même `id`). `fiscalite.json` est produit par
`python3 tools/generer_fiscalite.py v1/fiscalite.json v1/scenarios.json`, qui vérifie que les deux listes concordent.

- Chaque valeur modélisée porte sa source et sa date ; l'historique Git sert de journal public.
- Même grille pour tous les candidats : chaque paramètre est soit précisé et sourcé,
  soit marqué `{ "status": "unspecified" }` (l'app reprend alors la loi actuelle et l'affiche).
- Avant tout envoi : `python3 tools/valider.py v1/scenarios.json` et
  `python3 tools/valider_fiscalite.py v1/fiscalite.json v1/scenarios.json` (lancés aussi par GitHub Actions,
  qui publie sur GitHub Pages si tout est valide).
- Signaler une erreur : ouvrir une *issue* sur ce dépôt.

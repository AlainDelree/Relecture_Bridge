# Aide-mémoire Git

Référence personnelle des commandes git courantes, avec explications.
Pense à consulter tes fichiers `.diff` / `_annote.md` dans `~/Relecture_Bridge/`
pour t'entraîner à lire ce que ces commandes produisent concrètement.

---

## 1. Configuration (une fois par machine)

```bash
git config --global user.name "Alain"
git config --global user.email "alain@example.com"
```
Identité utilisée dans chaque commit (visible dans `Author:` de `git show`).

```bash
git config --global init.defaultBranch master
```
Nom par défaut de la branche principale à la création d'un dépôt (`master` ou `main`
selon convention — Bridge_Agent utilise `master`).

```bash
git config --list
```
Affiche tous les réglages actifs (globaux + locaux au dépôt courant).

---

## 2. Créer / récupérer un dépôt

```bash
git init
```
Transforme le dossier courant en dépôt git (crée le sous-dossier `.git/`).
C'est ce que fait la démo qu'on a faite pour tester le hook `post-commit`.

```bash
git clone <url>
```
Copie un dépôt distant en entier (historique inclus) dans un nouveau dossier local.
C'est ce que fait `watcher.py` au tout premier démarrage sur un projet.

---

## 3. Le cycle de base : modifier, préparer, committer

```bash
git status
```
Montre l'état actuel : fichiers modifiés, fichiers prêts à être committés
("staged"), fichiers non suivis. **La commande la plus utile au quotidien**,
à taper avant toute autre action si tu hésites.

```bash
git add <fichier>
git add .
```
Ajoute un fichier (ou tout le dossier courant) à la "zone de préparation"
(staging area) — ce que le prochain commit va inclure. `git add .` ajoute
tout ce qui est modifié/nouveau dans le dossier courant et ses sous-dossiers.

```bash
git diff
```
Montre les changements **non encore ajoutés** (`git add`) par rapport au
dernier commit. Format identique à ce que tu vois dans tes fichiers `.diff`.

```bash
git diff --staged
```
Montre les changements déjà ajoutés (`git add`) mais pas encore committés.

```bash
git commit -m "message"
```
Enregistre un instantané (snapshot) de tout ce qui est dans la zone de
préparation, avec un message expliquant le pourquoi. C'est ce qui déclenche
ton hook `post-commit`.

```bash
git commit -am "message"
```
Raccourci qui fait `git add` sur tous les fichiers **déjà suivis** (pas les
nouveaux fichiers) puis commit en une seule commande.

---

## 4. Consulter l'historique

```bash
git log
```
Liste tous les commits, du plus récent au plus ancien (hash, auteur, date, message).

```bash
git log --oneline
```
Version compacte : un commit par ligne (hash court + message).

```bash
git log --oneline --graph --all
```
Comme ci-dessus, mais avec un graphe ASCII montrant les branches et leurs
points de divergence/fusion. Très utile pour visualiser l'historique.

```bash
git show <hash>
```
Détail complet d'un commit précis : message, auteur, date, et diff. C'est
exactement ce que ton hook `post-commit` capture automatiquement.

```bash
git show HEAD
```
`HEAD` désigne toujours "le commit sur lequel je suis actuellement" — donc
`git show HEAD` = le dernier commit fait.

```bash
git blame <fichier>
```
Montre, ligne par ligne, quel commit (et quel auteur) a écrit chaque ligne
d'un fichier en dernier. Utile pour retrouver le contexte d'une ligne suspecte.

---

## 5. Branches

```bash
git branch
```
Liste les branches locales (celle avec `*` est la branche courante).

```bash
git branch <nom>
```
Crée une nouvelle branche à partir de la position actuelle, **sans** basculer dessus.

```bash
git checkout <nom>
git switch <nom>
```
Bascule sur une branche existante. `switch` est la commande plus récente et
plus claire, dédiée uniquement aux branches (`checkout` fait aussi d'autres
choses, ce qui prêtait à confusion).

```bash
git checkout -b <nom>
git switch -c <nom>
```
Crée une branche **et** bascule dessus en une seule commande. C'est la
commande la plus utilisée en pratique — comme évoqué plus tôt pour une
branche de travail purement locale, jamais poussée sur GitHub.

```bash
git branch -d <nom>
```
Supprime une branche locale (refuse si elle contient des commits non fusionnés
ailleurs — sécurité). `-D` majuscule force la suppression même dans ce cas.

---

## 6. Fusionner : merge vs rebase

C'est LA question qui revient tout le temps. Les deux résolvent le même
problème — intégrer les changements d'une branche dans une autre — mais
d'une manière très différente sur l'historique final.

### Le contexte de départ

Imagine que tu as créé une branche `feature` à partir de `master`, et que les
deux ont continué à avancer chacune de leur côté :

```
master:   A---B---C
               \
feature:        D---E
```

### `git merge` — préserve l'historique tel quel

```bash
git checkout master
git merge feature
```

Crée un **nouveau commit de fusion** qui a deux parents (le dernier commit de
chaque branche). L'historique garde une trace explicite que deux lignes de
travail ont existé puis ont été réunies :

```
master:   A---B---C-------M
               \         /
feature:        D-------E
```

**Avantages** : rien n'est réécrit, l'historique reflète fidèlement ce qui
s'est réellement passé, aucun risque de casser des références existantes.
**Inconvénient** : l'historique peut devenir difficile à lire si beaucoup de
branches se croisent (beaucoup de "commits de merge").

### `git rebase` — réécrit l'historique pour le rendre linéaire

```bash
git checkout feature
git rebase master
```

Prend les commits de `feature` (`D`, `E`) et les **rejoue un par un** comme
s'ils avaient été écrits après `C`, en leur donnant de **nouveaux hash** :

```
master:   A---B---C
                    \
feature:             D'---E'
```

Ensuite, un simple `git merge feature` depuis `master` avance juste le
pointeur, sans commit de fusion (« fast-forward ») :

```
master:   A---B---C---D'---E'
```

**Avantages** : historique final linéaire, propre, facile à lire (`git log`
ressemble à une seule ligne droite).
**Inconvénients / risques** :
- Les commits sont **réécrits** (nouveaux hash) — si quelqu'un d'autre avait
  déjà ces commits (`D`, `E`) sur sa machine, son historique divergera du tien.
  **Règle d'or : ne jamais rebase une branche déjà poussée et partagée avec
  quelqu'un d'autre.** Sur une branche purement locale (comme évoqué plus
  tôt), aucun risque.
- Peut nécessiter de résoudre les mêmes conflits plusieurs fois (un par
  commit rejoué), contre une seule fois avec `merge`.

### En résumé

| | `merge` | `rebase` |
|---|---|---|
| Historique | fidèle, avec commits de fusion | linéaire, réécrit |
| Sécurité sur branche partagée | ✅ toujours sûr | ⚠️ dangereux si déjà poussée |
| Lisibilité de `git log` | peut être touffu | propre, linéaire |
| Cas d'usage typique | intégrer une branche terminée dans `master` | nettoyer une branche perso avant de la partager |

Pour Bridge_Agent, vu que CCL commit en local sans jamais pousser, et que
c'est toi qui pousses après vérification (§5 de la doc), tu es dans un
contexte où les deux sont sûrs tant que ça reste sur ta machine avant le push.

---

## 7. Annuler / revenir en arrière

```bash
git restore <fichier>
```
Annule les modifications non ajoutées (`git add`) d'un fichier — revient à
la version du dernier commit. (Ancienne syntaxe équivalente : `git checkout -- <fichier>`.)

```bash
git restore --staged <fichier>
```
Retire un fichier de la zone de préparation sans annuler ses modifications
(l'inverse d'un `git add` sur ce fichier).

```bash
git reset --soft HEAD~1
```
Annule le **dernier commit**, mais garde tous les changements en zone de
préparation (comme si tu venais de faire `git add` mais pas encore commit).
Utile pour refaire un message de commit ou regrouper des commits.

```bash
git reset --hard HEAD~1
```
⚠️ Annule le dernier commit **et supprime tous les changements associés**,
sans retour possible facile. C'est la commande qu'on a utilisée pour annuler
ton commit de test sur Scrabble.

```bash
git revert <hash>
```
Crée un **nouveau commit** qui annule les changements d'un commit précis,
sans réécrire l'historique existant. Plus sûr que `reset` sur du code déjà
partagé/poussé, puisque rien n'est supprimé — l'annulation est elle-même tracée.

---

## 8. Mettre de côté sans committer (stash)

```bash
git stash
```
Met de côté temporairement tes modifications non committées (comme un
tiroir), et remet ton dossier de travail propre. Utile si tu dois changer
de branche rapidement sans avoir fini ton travail en cours.

```bash
git stash pop
```
Récupère le dernier "tiroir" mis de côté et l'applique de nouveau à ton
dossier de travail.

```bash
git stash list
```
Liste tous les tiroirs en attente (tu peux en avoir plusieurs empilés).

---

## 9. Travailler avec un dépôt distant (GitHub)

```bash
git remote -v
```
Liste les dépôts distants configurés (typiquement `origin`) avec leurs URLs.

```bash
git fetch
```
Récupère les nouveautés du distant **sans** les fusionner dans ta branche
actuelle — juste pour regarder ce qui a changé ailleurs.

```bash
git pull
```
Équivaut à `git fetch` + `git merge` en une seule commande : récupère et
fusionne immédiatement.

```bash
git pull --ff-only
```
Comme `git pull`, mais refuse s'il faut créer un commit de fusion — n'avance
que si c'est un simple "fast-forward". C'est exactement ce que fait
`watcher.py` en début de cycle (§1 de la doc Bridge_Agent) : sûr par
construction, jamais de commit de fusion surprise, jamais d'écrasement.

```bash
git push
```
Envoie tes commits locaux vers le dépôt distant. **Jamais utilisé par CCL**
dans Bridge_Agent — c'est toujours toi qui pousses après vérification.

```bash
git push origin <branche>
```
Pousse spécifiquement une branche donnée (utile la première fois qu'une
branche locale doit être envoyée).

---

## 10. Fichiers à ignorer

```
# .gitignore
configs/*.conf
logs/
venv/
ssl/
```
Liste des fichiers/dossiers que git doit ignorer complètement — jamais
suivis, jamais proposés par `git status`. C'est exactement le mécanisme
utilisé dans Bridge_Agent pour les secrets (mots de passe hashés, clés SSL,
tokens).

```bash
git rm --cached <fichier>
```
Arrête de suivre un fichier déjà committé par le passé (sans le supprimer du
disque) — utile si tu as oublié de l'ajouter à `.gitignore` avant son premier commit.

---

## 11. Étiqueter une version

```bash
git tag v1.0
```
Marque le commit courant avec une étiquette lisible (souvent un numéro de
version), plus facile à retrouver qu'un hash.

```bash
git tag
```
Liste toutes les étiquettes existantes.

---

## 12. Commandes de diagnostic utiles

```bash
git log --oneline origin/master..HEAD
```
Liste les commits que tu as en local mais qui ne sont **pas encore** sur le
distant — exactement la commande citée dans la doc Bridge_Agent (§13) pour
vérifier ce qui reste à pousser.

```bash
git diff origin/master..HEAD
```
Montre le diff complet cumulé de tout ce que tu as en local mais pas encore
poussé — utile pour une relecture globale avant un `git push`, en
complément des fichiers unitaires déjà exportés dans `Relecture_Bridge`.

```bash
git show --stat HEAD
```
Résumé rapide d'un commit : liste des fichiers touchés et nombre de lignes
ajoutées/supprimées, sans le détail ligne par ligne.

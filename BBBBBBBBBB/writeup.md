# 🧩 CTF Challenge Review: `BBBBBBBBBB`

Acesta este un rezumat tehnic al rezolvării provocării CTF `BBBBBBBBBB`, unde a trebuit să curățăm un fișier JPEG corupt de secvențe injectate, să reconstruim o imagine validă și să extragem un flag din ea folosind OCR.


## 🗃️ Structura Inițială

Am primit un fișier:

chall-zip-in-zip.zip


După dezarhivare:

## 🔎 1. Verificare fișier JPEG

```bash
unzip -l chall-zip-in-zip.zip
file chall.jpg


🧪 2. Analiză inițială

Comenzi folosite pentru a căuta posibile fișiere ascunse sau steganografie:
strings chall.jpg | less

binwalk chall.jpg

steghide extract -sf chall.jpg

exiftool chall.jpg

Rezultatul: imaginea părea validă, dar conținea mult text repetitiv de forma:

BBBBBBBBBB

🧠 3. Observație cheie

Secvența BBBBBBBBBB este injectată în fișierul binar ca un marker corupător:
→ ASCII: 4242 4242 4242 4242 4242

📂 5. Verificare și vizualizare imagine reconstruită
file hidden_image.jpg
xdg-open hidden_image.jpg

Imaginea reconstruită conține flag-ul în format vizual.

🧠 6. OCR: Extragerea textului din imagine

tesseract hidden_image.jpg out_text

cat out_text.txt

⚠️ 7. Dacă apar erori OCR (ex: boxClipToRectangle)

Se întâmplă dacă imaginea are DPI corupt sau transparență.

✅ Soluție: Preprocesare cu ImageMagick

sudo apt install imagemagick

convert hidden_image.jpg -strip -resize 300% -type Grayscale -sharpen 0x1 prepped.jpg
tesseract prepped.jpg stdout

🏁 8. Rezultatul final

Flag-ul real, vizibil în imagine, era:

TFCCTF{the_fl4g_1s_th3_w4y}

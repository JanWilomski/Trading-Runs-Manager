# Trading Runs Manager - Architektura Aplikacji

## 📋 Ogólny Opis

Aplikacja do zarządzania "runami" tradingowymi - zamiast grać dużym kontem z małym ryzykiem, gramy małym kontem z większym ryzykiem % na trade. Aplikacja monitoruje połączenie z MetaTrader 5 w czasie rzeczywistym.

---

## 🎯 Główne Funkcjonalności

### Zakładki aplikacji:
1. **Dashboard/Overview** - szybki przegląd wszystkich runów, statystyki ogólne
2. **Current Run** - aktywny run z real-time statystykami i ustawieniami
3. **History** - lista wszystkich runów + możliwość utworzenia nowego
4. **Settings** - ustawienia wizualne aplikacji + defaulty dla runów

### Kluczowe zasady:
- **Dzienny Stop Loss** - np. 25% konta (max strata dziennie)
- **Ogólny Stop Loss** - np. 50% konta początkowego (kończy runa)
- Run kończy się **tylko** przy osiągnięciu ogólnego stop lossa
- Monitoring MT5 **w czasie rzeczywistym** (ciągłe połączenie)
- Śledzenie **pojedynczych trade'ów** w ramach runa

---

## 🗄️ Struktura Bazy Danych (SQLite)

### Tabela: `runs`
| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Unikalny ID runa |
| `name` | TEXT NOT NULL | Nazwa runa |
| `start_date` | TEXT NOT NULL | Data i czas rozpoczęcia (ISO format) |
| `end_date` | TEXT | Data i czas zakończenia (NULL jeśli aktywny) |
| `initial_capital` | REAL NOT NULL | Początkowy kapitał |
| `current_capital` | REAL NOT NULL | Aktualny kapitał (aktualizowany automatycznie) |
| `max_loss_percentage` | REAL NOT NULL | Ogólny stop loss w % (np. 50) |
| `max_daily_loss_percentage` | REAL NOT NULL | Dzienny stop loss w % (np. 25) |
| `status` | TEXT NOT NULL | Status: 'active', 'completed', 'stopped' |
| `mt5_account_id` | INTEGER NOT NULL | ID konta MT5 (klucz obcy) |
| `created_at` | TEXT NOT NULL | Kiedy utworzono w aplikacji |

**Klucz obcy:** `mt5_account_id` → `mt5_accounts(id)`

---

### Tabela: `mt5_accounts`
| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Unikalny ID |
| `account_id` | INTEGER UNIQUE NOT NULL | Login MT5 |
| `account_password` | TEXT NOT NULL | ZASZYFROWANE hasło MT5 |
| `account_name` | TEXT | Opcjonalna nazwa (np. "Konto Demo") |
| `server` | TEXT | Serwer MT5 (np. "MetaQuotes-Demo") |
| `created_at` | TEXT NOT NULL | Data utworzenia |

**Uwaga:** Hasła szyfrowane master passwordem użytkownika!

---

### Tabela: `trades`
| Kolumna | Typ | Opis |
|---------|-----|------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Unikalny ID trade'a |
| `run_id` | INTEGER NOT NULL | ID runa (klucz obcy) |
| `symbol` | TEXT NOT NULL | Symbol (np. "EURUSD") |
| `type` | TEXT NOT NULL | Typ: 'buy' lub 'sell' |
| `volume` | REAL NOT NULL | Wielkość pozycji (lots) |
| `open_price` | REAL NOT NULL | Cena otwarcia |
| `close_price` | REAL | Cena zamknięcia (NULL jeśli otwarty) |
| `open_time` | TEXT NOT NULL | Czas otwarcia (ISO format) |
| `close_time` | TEXT | Czas zamknięcia (NULL jeśli otwarty) |
| `profit` | REAL | Zysk/strata w walucie (NULL jeśli otwarty) |
| `profit_percent` | REAL | Zysk/strata w % względem kapitału przy otwarciu |
| `mt5_ticket` | INTEGER | Numer ticketu z MT5 |

**Klucz obcy:** `run_id` → `runs(id)`

---

## 📁 Plik Konfiguracyjny (JSON)

### `settings.json`
```json
{
  "master_password_hash": "hashed_password_here",
  "default_max_loss_percentage": 50,
  "default_max_daily_loss_percentage": 25,
  "theme": "dark",
  "last_used_account_id": null
}
```

**Opis pól:**
- `master_password_hash` - zahashowane master password (do weryfikacji przy logowaniu)
- `default_max_loss_percentage` - domyślny ogólny stop loss
- `default_max_daily_loss_percentage` - domyślny dzienny stop loss
- `theme` - motyw aplikacji (dark/light)
- `last_used_account_id` - ostatnio używane konto MT5

---

## 🔒 Bezpieczeństwo

### Master Password System:
1. **Przy pierwszym uruchomieniu:** Użytkownik tworzy master password
2. **Zapisywanie konta MT5:** Hasło MT5 szyfrowane master passwordem → zapisywane do bazy
3. **Przy każdym uruchomieniu:** 
   - Użytkownik podaje master password
   - Aplikacja weryfikuje (porównuje hash)
   - Odszyfrowuje hasła MT5
   - Loguje do kont MT5

**Biblioteka do szyfrowania:** `cryptography` (Python)

---

## Architektura plików

trading_runs_manager/

├── main.py                          # Punkt wejścia\
├── data/                            # Dane (gitignore!)\
│   ├── trading_runs.db              # Baza SQLite\
│   └── settings.json                # Ustawienia\
├── database/                        # Data Access Layer\
│   ├── __init__.py\
│   ├── db_manager.py                # Obsługa SQLite\
│   └── models.py                    # Struktury danych (Run, Trade, Account)\
├── managers/                        # Business Logic Layer\
│   ├── __init__.py\
│   ├── run_manager.py               # Logika runów\
│   ├── mt5_manager.py               # Połączenie z MT5\
│   ├── settings_manager.py          # Obsługa settings.json\
│   └── encryption_manager.py        # Szyfrowanie\
├── gui/                             # GUI Layer\
│   ├── __init__.py\
│   ├── main_window.py               # Główne okno\
│   ├── dashboard_tab.py             # Zakładka Dashboard\
│   ├── current_run_tab.py           # Zakładka Current Run\
│   ├── history_tab.py               # Zakładka History\
│   └── settings_tab.py              # Zakładka Settings\
├── utils/                           # Narzędzia pomocnicze\
│   ├── __init__.py\
│   └── validators.py                # Walidacje danych\
├── requirements.txt                 # Zależności (pip)\
└── README.md                        # Dokumentacja\

---

## 🔄 Przepływ Danych

### Aktualizacja kapitału:
1. MT5 zwraca informacje o nowym/zamkniętym trade
2. Aplikacja zapisuje trade do tabeli `trades`
3. **Automatycznie** przelicza `current_capital` w `runs`
4. Sprawdza czy osiągnięto stop loss (dzienny lub ogólny)
5. Jeśli tak - zmienia status runa na 'stopped'

### Statystyki dzienne:
- Liczone **na bieżąco** z trade'ów (filtrowanie po dacie)
- Nie zapisywane osobno - zawsze fresh data

---

## 📚 Stack Technologiczny

- **Python** - język programowania
- **SQLite** - baza danych
- **MetaTrader5** - biblioteka do połączenia z MT5
- **cryptography** - szyfrowanie haseł
- **GUI Framework** - do wyboru (CustomTkinter/PyQt/Tkinter)
- **pandas** - analiza danych (opcjonalnie)
- **matplotlib/plotly** - wykresy (opcjonalnie)

---

## 📝 Uwagi Implementacyjne

### Format dat:
Wszędzie używamy **ISO 8601**: `YYYY-MM-DD HH:MM:SS`
Przykład: `2024-01-15 14:30:00`

### Status runa:
- `active` - run jest aktywny, można tradować
- `completed` - run zakończony sukcesem (nie używane przy obecnych zasadach)
- `stopped` - run zatrzymany przez stop loss

### Profit percentage:
Procent zysku/straty liczone względem **kapitału runa w momencie otwarcia trade'a**, nie początkowego kapitału.

---

## 🚀 Kolejne Kroki Implementacji

1. **Struktura projektu** - foldery i pliki
2. **Database Manager** - klasa do obsługi SQLite
3. **Settings Manager** - klasa do obsługi JSON
4. **Encryption Manager** - szyfrowanie/deszyfrowanie haseł
5. **MT5 Manager** - połączenie i monitoring MT5
6. **Run Manager** - logika runów
7. **GUI** - interfejs użytkownika

---

*Dokument utworzony: 2025-12-08*
*Projekt: Trading Runs Manager*

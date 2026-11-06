"""Feste Exit-Codes des Programms (Spec `runtime-configuration`, Requirement „Exit-Codes").

Ein Dienst-Manager kann damit gewollte Stopps von Fehlern unterscheiden.
"""

EXIT_OK = 0  # gewollter Stopp (Strg-C, SIGTERM, Taste c)
EXIT_ERROR = 1  # Laufzeitfehler, auch ein CUDA-Fehler in der Inferenz
EXIT_CONFIG = 2  # ungültige Konfiguration (Change `config-file`)
EXIT_NO_GPU = 3  # keine nutzbare GPU beim Start
EXIT_WATCHDOG = 4  # Hauptschleife hängt (Watchdog)

REASONS = {
    EXIT_OK: "gewollter Stopp",
    EXIT_ERROR: "Laufzeitfehler",
    EXIT_CONFIG: "ungültige Konfiguration",
    EXIT_NO_GPU: "keine nutzbare GPU beim Start",
    EXIT_WATCHDOG: "Watchdog: Hauptschleife hängt",
}

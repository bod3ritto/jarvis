"""
test_discord_automation.py — Testy i narzędzie diagnostyczne dla automatyzacji Discord.

WYMAGANE PRZED UŻYCIEM:
1. Discord musi być uruchomiony i widoczny (niezminimalizowany).
2. Ustawienia użytkownika > Dostępność > włącz "Obsługa czytnika ekranu".
3. Dla mute/deafen: Ustawienia > Głos i wideo > Skróty klawiszowe > dodaj
   "Toggle Mute" = Ctrl+Shift+M i "Toggle Deafen" = Ctrl+Shift+D,
   oba z opcją "działa globalnie" (patrz config.py).

Uruchom:
    python test_discord_automation.py            # menu interaktywne
    python test_discord_automation.py dump        # zrzut drzewa UI do kalibracji
"""
import sys

from automation.discord_automation import DiscordAutomation


def dump_ui_tree(max_elements: int = 300):
    """Zrzuca listę elementów UI Discorda (control_type + nazwa) — pomaga dostroić selektory."""
    discord = DiscordAutomation()
    window = discord._connect_uia()
    if window is None:
        print("❌ Nie udało się podłączyć do okna Discord.")
        return

    print("📋 Elementy UI Discorda (control_type: nazwa):\n")
    count = 0
    for element in window.descendants():
        try:
            text = element.window_text()
            ctrl_type = element.element_info.control_type
        except Exception:
            continue
        if text:
            print(f"  [{ctrl_type}] {text}")
            count += 1
        if count >= max_elements:
            print(f"\n... obcięto po {max_elements} elementach")
            break

    print(f"\n✅ Wypisano {count} elementów z nazwami.")


def interactive_menu():
    discord = DiscordAutomation()

    print("🎛️  Test automatyzacji Discord")
    print("1. Toggle Mute (globalny skrót)")
    print("2. Toggle Deafen (globalny skrót)")
    print("3. Przełącz kanał")
    print("4. Wycisz użytkownika (tylko dla mnie) [eksperymentalne]")
    print("5. Pokaż ekran użytkownika [eksperymentalne]")
    print("6. Zrzuć drzewo UI (kalibracja)")

    choice = input("Wybór: ").strip()

    if choice == "1":
        discord.toggle_mute()
    elif choice == "2":
        discord.toggle_deafen()
    elif choice == "3":
        name = input("Nazwa kanału: ").strip()
        discord.switch_channel(name)
    elif choice == "4":
        name = input("Nazwa użytkownika: ").strip()
        discord.mute_user(name)
    elif choice == "5":
        name = input("Nazwa użytkownika: ").strip()
        discord.view_user_screen(name)
    elif choice == "6":
        dump_ui_tree()
    else:
        print("Nieznany wybór")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dump":
        dump_ui_tree()
    else:
        interactive_menu()

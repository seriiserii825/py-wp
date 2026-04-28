from rich import print

from classes.utils.Command import Command
from classes.utils.Menu import Menu
from classes.utils.Print import Print


def _run_best_effort(cmd: str):
    try:
        Command.run(cmd)
    except RuntimeError as e:
        Print.error(str(e))


def update_translations():
    active = Command.run_quiet("wp option get WPLANG") or "en_US"
    Command.run("wp language core update")
    _run_best_effort(f"wp language plugin --all install {active}")
    _run_best_effort("wp language plugin --all update")
    _run_best_effort(f"wp language theme --all install {active}")
    _run_best_effort("wp language theme --all update")


def _list_installed_languages() -> list[str]:
    data = Command.run_json(
        "wp language core list --fields=language,status --format=json"
    )
    return [
        item["language"] for item in data if item["status"] in ("installed", "active")
    ]


def _print_language_status():
    active = Command.run_quiet("wp option get WPLANG") or "en_US"
    installed = _list_installed_languages()
    if active != "en_US" and active not in installed:
        Command.run_quiet("wp option update WPLANG ''")
        active = "en_US"
    print("=" * 20)
    print(f"[green]Active language: [bold]{active}[/bold]")
    if installed:
        print(f"[blue]Installed: {', '.join(installed)}")
    else:
        print("[blue]Installed: none")
    print("=" * 20)


def _show_all_languages():
    raw = Command.run_quiet(
        "wp language core list --fields=language,english_name,status --format=table"
    )
    print(raw)


def _add_language():
    all_raw = Command.run_quiet("wp language core list --field=language")
    all_langs = {lang for lang in all_raw.splitlines() if lang}
    installed = set(_list_installed_languages())
    available = sorted(all_langs - installed)
    if not available:
        Print.error("No new languages to install.")
        return
    choice = Menu.select_fzf(available)
    if choice == -1:
        return
    lang = available[choice]
    Command.run(f"wp language core install {lang}")
    _run_best_effort(f"wp language plugin --all install {lang}")
    _run_best_effort(f"wp language theme --all install {lang}")


def _select_language():
    installed = _list_installed_languages()
    if not installed:
        Print.error("No languages installed.")
        return
    choice = Menu.select_fzf(installed)
    if choice == -1:
        return
    lang = installed[choice]
    # WordPress stores en_US as empty string in WPLANG
    wplang = "" if lang == "en_US" else lang
    Command.run(f"wp option update WPLANG '{wplang}'")


def _delete_language():
    installed = _list_installed_languages()
    if not installed:
        Print.error("No languages installed.")
        return
    choice = Menu.select_fzf(installed)
    if choice == -1:
        return
    lang = installed[choice]
    active = Command.run_quiet("wp option get WPLANG") or "en_US"
    Command.run(f"wp language core uninstall {lang}")
    _run_best_effort(f"wp language plugin --all uninstall {lang}")
    _run_best_effort(f"wp language theme --all uninstall {lang}")
    if lang == active:
        Command.run("wp option update WPLANG ''")


def change_site_language_menu():
    _print_language_status()
    options = [
        "0).Add new",
        "1).Select one",
        "2).Delete one",
        "3).Show all",
        "4).Back",
    ]
    choice = Menu.select_fzf(options)
    if choice == 0:
        _add_language()
        change_site_language_menu()
    elif choice == 1:
        _select_language()
        change_site_language_menu()
    elif choice == 2:
        _delete_language()
        change_site_language_menu()
    elif choice == 3:
        _show_all_languages()
        change_site_language_menu()


def site_settings_menu():
    options = [
        "0).Update Translations",
        "1).Change Site Language",
        "2).Back",
    ]
    choice = Menu.select_fzf(options)
    if choice == 0:
        update_translations()
        site_settings_menu()
    elif choice == 1:
        change_site_language_menu()
        site_settings_menu()

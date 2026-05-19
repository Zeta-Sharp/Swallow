import os
import warnings
import tomllib
import tomli_w
from pathlib import Path
import json
import shutil
from send2trash import send2trash


def swallow_init(args, toml_path):
    settings = {}
    is_modification = False
    if os.path.exists(toml_path):
        with open(toml_path, "rb") as f:
            settings = tomllib.load(f)
        is_modification = True

    site_root_current = settings.get("site_root", None)
    msg = "Enter the site root URL (e.g., https://example.com)"
    if site_root_current:
        msg += f"push enter to use current: [{site_root_current}]: "
    else:
        msg += ": "
    settings["site_root"] = input(msg) or site_root_current
    if not settings["site_root"]:
        raise ValueError("Site root URL is required.")

    default_lang_current = settings.get("default_lang", None)
    msg = "Enter the default language code (e.g., en)"
    if default_lang_current:
        msg += f" push enter to use current: [{default_lang_current}]: "
    else:
        msg += ": "
    settings["default_lang"] = input(msg) or default_lang_current
    if not settings["default_lang"]:
        raise ValueError("Default language code is required.")

    available_langs_current = settings.get("available_langs", None)
    msg = "Enter the all accepted language codes separated by commas (e.g., en,ja) (including the default language)"
    if available_langs_current:
        msg += f" push enter to use current: [{','.join(available_langs_current)}]: "
    else:
        msg += ": "
    langs_input = input(msg).replace(" ", "")
    if langs_input:
        settings["available_langs"] = langs_input.split(",")
    else:
        settings["available_langs"] = available_langs_current
    if not settings["available_langs"]:
        settings["available_langs"] = []
        settings["available_langs"].append(settings["default_lang"])
        print("Accepted languages cannot be empty. Default language has been added to accepted languages.")

    if settings["default_lang"] not in settings["available_langs"]:
        settings["available_langs"].append(settings["default_lang"])
        print("Accepted languages must include the default language. Default language has been added automatically.")

    from_current = settings.get("from", None)
    msg = "Enter the source directory path (e.g., ./src)"
    if from_current:
        msg += f" push enter to use current: [{from_current}]: "
    else:
        msg += ": "
    from_path_str = input(msg) or str(from_current)
    settings["from"] = Path(from_path_str).resolve()
    if not os.path.exists(settings["from"]):
        os.makedirs(settings["from"])
        print(f"Directory '{settings['from']}' created.")
    if not os.path.exists(settings["from"] / "markdown"):
        os.makedirs(settings["from"] / "markdown")
        print(
            f"Directory '{settings['from'] / 'markdown'}' created.",
            "Place your markdown files here.")

    if os.path.exists(settings["from"] / "templates") and any((settings["from"] / "templates").iterdir()):
        print(f"Directory '{settings['from'] / 'templates'}' is not empty.")
        msg = f"Do you want to clean up and copy default templates to '{settings['from'] / 'templates'}'? (y/n): "
        if input(msg).lower() == "y":
            send2trash(settings["from"] / "templates")
            shutil.copytree(Path(__file__).parent / "swallow_assets" / "default_templates", settings["from"] / "templates")
            shutil.copy2(Path(__file__).parent / "swallow_assets" / "extensions.json", settings["from"] / "extensions.json")
            print(
                f"Default templates copied to '{settings['from'] / 'templates'}'.",
                "You can modify them or replace them with your own templates.")
    else:
        if os.path.exists(settings["from"] / "templates"):
            send2trash(settings["from"] / "templates")
        shutil.copytree(Path(__file__).parent / "swallow_assets" / "default_templates", settings["from"] / "templates")
        shutil.copy2(Path(__file__).parent / "swallow_assets" / "extensions.json", settings["from"] / "extensions.json")
        print(
            f"Default templates copied to '{settings['from'] / 'templates'}'.",
            "You can modify them or replace them with your own templates.")

    to_current = settings.get("to", None)
    msg = "Enter the target directory path (e.g., ./dist)"
    if to_current:
        msg += f" push enter to use current: [{to_current}]: "
    else:
        msg += ": "
    to_path_str = input(msg) or str(to_current)
    settings["to"] = Path(to_path_str).resolve()
    if os.path.exists(settings["to"]) and any(settings["to"].iterdir()):
        select = input(
            f"Directory '{settings['to']}' is not empty. Do you want to overwrite it? (y/n): ")
        if select.lower() == "y":
            send2trash(settings["to"])
            os.makedirs(settings["to"])
            print(f"Directory '{settings['to']}' has been cleared (Still remaining in trash).")
        else:
            warnings.warn(
                "Proceeding may cause overwrite conflicts or unintended publication.")
    else:
        os.makedirs(settings["to"])
        print(
            f"Directory '{settings['to']}' created.",
            "Generated blog index will be placed here.")
    if not os.path.exists(settings["to"] / "articles"):
        os.makedirs(settings["to"] / "articles")
        print(
            f"Directory '{settings['to'] / 'articles'}' created.",
            "Generated articles and metadata will be placed here.")

    if os.path.exists(settings["to"] / "assets") and any((settings["to"] / "assets").iterdir()):
        print(f"Directory '{settings['to'] / 'assets'}' is not empty.")
        msg = f"Do you want to clean up and copy default assets to '{settings['to'] / 'assets'}'? (y/n): "
        if input(msg).lower() == "y":
            send2trash(settings["to"] / "assets")
            shutil.copytree(Path(__file__).parent / "swallow_assets" / "default_assets", settings["to"] / "assets")
            print(
                f"Default assets copied to '{settings['to'] / 'assets'}'.",
                "You can modify them or replace them with your own assets.")
    else:
        shutil.copytree(Path(__file__).parent / "swallow_assets" / "default_assets", settings["to"] / "assets")
        print(
            f"Default assets copied to '{settings['to'] / 'assets'}'.",
            "You can modify them or replace them with your own assets.")

    to_Path = settings["to"]
    settings["from"] = str(settings["from"].relative_to(Path.cwd()))
    settings["to"] = str(settings["to"].relative_to(Path.cwd()))

    parse_extensions_current = settings.get("parse_extensions", None)
    msg = "Enter the file extensions to parse separated by commas (e.g., fenced_code, codehighlight, table, md_in_html) (please make sure the corresponding extensions are included in your environment)"
    if parse_extensions_current:
        msg += f" \npush enter to use current: [{','.join(parse_extensions_current)}]: "
    else:
        msg += ": "
    parse_extensions_input = input(msg).replace(" ", "")
    if parse_extensions_input:
        settings["parse_extensions"] = parse_extensions_input.split(",")
    else:
        settings["parse_extensions"] = parse_extensions_current

    site_names_current = settings.get("site_name", {})
    if "site_name" not in settings:
        settings["site_name"] = {}
    for lang in settings["available_langs"]:
        msg = f"Enter the site name in {lang} (e.g., My Blog)"
        site_name_current = site_names_current.get(lang, None)
        if site_names_current and lang in site_names_current:
            site_name_current = site_names_current[lang]
            msg += f" push enter to use current: [{site_name_current}]: "
        else:
            msg += ": "
        settings["site_name"][lang] = input(msg) or site_name_current

    site_descriptions_current = settings.get("site_description", {})
    if "site_description" not in settings:
        settings["site_description"] = {}
    for lang in settings["available_langs"]:
        msg = f"Enter the site description in {lang} (e.g., This is my personal blog.)"
        site_description_current = site_descriptions_current.get(lang, None)
        if site_descriptions_current and lang in site_descriptions_current:
            site_description_current = site_descriptions_current[lang]
            msg += f" push enter to use current: [{site_description_current}]: "
        else:
            msg += ": "
        settings["site_description"][lang] = input(msg) or site_description_current

    with open(toml_path, "wb") as f:
        tomli_w.dump(settings, f)
    print(f"Configuration saved to {toml_path} successfully.")

    del settings["from"]
    del settings["to"]
    del settings["parse_extensions"]
    with open(to_Path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
    print(f"Metadata saved to {to_Path / 'metadata.json'} successfully.")

    if is_modification:
        print("Modified settings will be applied to the next generation.")

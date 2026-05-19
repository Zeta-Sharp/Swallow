#!/usr/bin/env python3

import json
import os
import re
import sys
from jinja2 import Environment, FileSystemLoader
import frontmatter
import datetime
from typing import Union
from pathlib import Path
import tomllib

import markdown

toml_path = "./config.toml"


class SwallowSSG():
    article_id = None

    def __init__(self):
        self.article_id = None
        if not os.path.exists(toml_path):
            raise FileNotFoundError(
                "Config file not found. Please run 'init' mode first to create the config file.")
        with open(toml_path, "rb") as f:
            self.settings = tomllib.load(f)
            self.settings["from"] = Path(self.settings["from"]).resolve()
            self.settings["to"] = Path(self.settings["to"]).resolve()
            self.env = Environment(
                loader=FileSystemLoader(self.settings["from"] / "templates"))

    def run(self, mode=None, file=None):
        # is_commited = False

        match mode:
            case "1":
                self.add_article(
                    target_file_default=file if file else "")
                self.regenerate_index()
            case "2":
                self.regenerate_index()
            case "3":
                self.regenerate_all_articles()
                self.regenerate_index()
            case "4":
                self.regenerate_sitemap()
            case _:
                print("Invalid choice. Exiting.")
                sys.exit()

    def add_article(
            self,
            target_file_default: Union[str, Path, None] = None,
            output: Union[dict, None] = None, no_interact: bool = False):
        default_lang = self.settings["default_lang"]
        available_langs = self.settings["available_langs"]

        article_data = {}

        if default_lang not in available_langs:
            raise ValueError(
                f"Default language '{default_lang}' is not in the list of supported languages: {available_langs}")
        if not target_file_default:
            if no_interact:
                raise ValueError(
                    "No target file provided for non-interactive mode.")
            else:
                target_file_default = input(
                    f"Enter the target file name in {default_lang} (ends with _{default_lang}.md): ")

        target_file_default = Path(target_file_default).resolve()

        if target_file_default.suffix != ".md" \
            or not target_file_default.stem.endswith(
                f"_{default_lang}") or not target_file_default.is_file():
            raise FileNotFoundError(
                "Invalid file name. Please ensure it ends with _<lang>.md and exists.")

        for lang in available_langs:
            if lang == default_lang:
                continue
            target_file = target_file_default.with_name(
                target_file_default.stem.replace(
                    f"_{default_lang}", f"_{lang}")
                + target_file_default.suffix)
            if not os.path.isfile(target_file):
                raise FileNotFoundError(
                    f"{lang} version {target_file} does not exist.")

        post = frontmatter.load(str(target_file_default))

        required_title_keys = [f"title_{lang}" for lang in available_langs]
        required_summary_keys = [f"summary_{lang}" for lang in available_langs]

        required_keys = required_title_keys + ["date"] + required_summary_keys
        missing = [k for k in required_keys if k not in post]
        if missing:
            raise KeyError(
                "Missing required metadata in ",
                f"{target_file_default}: {', '.join(missing)}")

        is_draft = post.get("draft", False)
        if is_draft:
            print(
                f"Article '{post.get(f'title_{default_lang}')}' is marked as draft.",
                "Skipping generation.")
            return output

        article_data = {
            "title": {
                lang: str(post.get(f"title_{lang}"))
                for lang in available_langs
            },
            "date": post.get("date"),
            "content": {},
            "tags": post.get("tags", []),
            "summary": {
                lang: str(post.get(f"summary_{lang}"))
                for lang in available_langs
            },
            "extensions": post.get("extensions", [])
        }

        extensions_html = ""

        if article_data["extensions"]:
            with open(
                    self.settings["from"] / "extensions.json",
                    "r", encoding="utf-8") as f:
                all_extensions = json.load(f)
            if not isinstance(article_data["extensions"], list):
                raise ValueError("Extensions should be a list.")
            for ext in article_data["extensions"]:
                if ext not in all_extensions:
                    raise ValueError(
                        f"Extension '{ext}' is not defined in extensions.json.")
                extensions_html += all_extensions[ext]

        match_date = r"^\d{4}-\d{2}-\d{2}$"
        if isinstance(article_data["date"], datetime.date):
            date = article_data["date"].strftime("%Y-%m-%d")
        else:
            date = str(article_data["date"])
            match_date = r"^\d{4}-\d{2}-\d{2}$"
            if not re.match(match_date, date):
                raise ValueError(
                    "Invalid date format.",
                    "Please enter the date in YYYY-MM-DD format.")
        article_data["date"] = date

        article_id = date.replace("-", "")
        article_data["id"] = article_id
        parse_extensions = self.settings.get("parse_extensions", [])

        for lang in available_langs:
            target_file = target_file_default.with_name(
                target_file_default.stem.replace(
                    f"_{default_lang}", f"_{lang}")
                + target_file_default.suffix)
            md_content = frontmatter.load(str(target_file)).content
            html_content = markdown.markdown(
                md_content,
                extensions=parse_extensions)
            article_data["content"][lang] = html_content

        article_template = self.env.get_template("article_template.html")
        article_html = article_template.render(
            site_name=self.settings["site_name"][default_lang],
            site_root=self.settings["site_root"],
            available_langs=self.settings["available_langs"],
            article=article_data["content"][default_lang],
            title=article_data["title"][default_lang],
            description=article_data["summary"][default_lang],
            date=article_data["date"],
            tags=article_data["tags"],
            extensions=extensions_html if extensions_html else ""
        )

        target_path = self.settings["to"] / "articles" / f"{article_id}.html"
        with open(
                target_path,
                "w", encoding="utf-8") as f:
            f.write(article_html)

        article_metadata = article_data.copy()

        if output is not None:
            output[article_id] = {
                "id": article_id,
                "title": {lang: article_data["title"][lang]
                          for lang in available_langs},
                "date": article_data["date"],
                "tags": article_data["tags"],
                "summary":
                    {lang: article_data["summary"][lang]
                     for lang in available_langs},
                "translation_file": f"articles/{article_data['id']}.json"
            }
            ids_list = sorted(list(output.keys()), reverse=True)
            articles_index_data = output
        else:
            target_path = self.settings["to"] / "article_data.json"
            with open(
                    target_path,
                    encoding="utf-8") as f:
                articles_index_data = json.load(f)

            articles_index_data[article_id] = {
                "id": article_id,
                "title": {lang: article_data["title"][lang]
                          for lang in available_langs},
                "date": article_data["date"],
                "tags": article_data["tags"],
                "summary":
                    {lang: article_data["summary"][lang]
                     for lang in available_langs},
                "translation_file": f"articles/{article_data['id']}.json"
            }
            sorted_data = dict(
                sorted(
                    articles_index_data.items(),
                    key=lambda x: x[0], reverse=True))
            ids_list = sorted(list(sorted_data.keys()), reverse=True)
            with open(
                    target_path,
                    "w", encoding="utf-8") as f:
                json.dump(sorted_data, f, ensure_ascii=False, indent=4)

        older_id = (ids_list[ids_list.index(article_id) + 1]
                    if article_id in ids_list
                    and ids_list.index(article_id) + 1 < len(ids_list)
                    else None)
        older_metadata = {}

        if older_id is not None:
            target_path = \
                self.settings["to"] / "articles" / f"{older_id}.json"
            with open(
                    target_path,
                    "r", encoding="utf-8") as f:
                older_metadata = json.load(f)

            with open(
                    target_path,
                    "w", encoding="utf-8") as f:
                older_metadata["newer_article_id"] = article_id
                older_metadata["newer_article_title"] = {
                    lang: article_data["title"][lang]
                    for lang in available_langs}
                json.dump(older_metadata, f, ensure_ascii=False, indent=4)

        article_metadata["older_article_id"] = older_id
        article_metadata["older_article_title"] = {
            lang: older_metadata["title"][lang] if older_id is not None
            else None for lang in available_langs
        }
        article_metadata["newer_article_id"] = None
        article_metadata["newer_article_title"] = {
            lang: None for lang in available_langs
        }

        target_path = \
            self.settings["to"] / "articles" / f"{article_id}.json"

        with open(
                target_path,
                "w", encoding="utf-8") as f:
            json.dump(article_metadata, f, ensure_ascii=False)
        print(f"Article {article_id} added successfully.")
        if output is not None:
            return output

    def regenerate_all_articles(self):
        all_article_data = {}
        target_base = self.settings["from"] / "markdown"
        target_files = sorted(list(
            target_base.glob(f"*_{self.settings['default_lang']}.md")))

        if not target_files:
            print(f"No articles found in {target_base}")
            return
        print(f"Found {len(target_files)} articles. Regenerating...")

        for file_path in target_files:
            try:
                all_article_data = self.add_article(
                    target_file_default=file_path, output=all_article_data)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        if all_article_data is not None:
            sorted_data = dict(
                sorted(all_article_data.items(),
                       key=lambda x: x[0], reverse=True))
            target_path = self.settings["to"] / "article_data.json"
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(sorted_data, f, ensure_ascii=False, indent=4)
            print("All articles and article_data.json have been updated.")
        else:
            raise ValueError("all_article_data is missed.")

    def regenerate_index(self):
        target_path = self.settings["to"] / "article_data.json"
        with open(
                target_path,
                "r", encoding="utf-8") as f:
            article_data = json.load(f)

        article_list = sorted(
            article_data.values(), key=lambda x: x["date"], reverse=True)
        for article in article_list:
            article["link"] = f"/articles/{article['id']}.html"

        tag_list = set()
        for article in article_list:
            for tag in article["tags"]:
                tag_list.add(tag)

        list_template = self.env.get_template("list_template.html")
        index_html = list_template.render(
            site_name=self.settings["site_name"][self.settings["default_lang"]],
            site_root=self.settings["site_root"],
            site_description=self.settings["site_description"][self.settings["default_lang"]],
            articles=article_list,
            tags=sorted(tag_list),
            full_data_json=json.dumps(article_data, ensure_ascii=False),
            available_langs=self.settings["available_langs"]
            )

        target_path = self.settings["to"] / "index.html"
        with open(
                target_path,
                "w", encoding="utf-8") as f:
            f.write(index_html)
        print("Index regenerated successfully.")

    def regenerate_sitemap(self):
        article_index_file = self.settings["to"] / "index.html"
        if not os.path.isfile(article_index_file):
            raise FileNotFoundError(
                "Blog index not found. Please regenerate index first.")
        article_index_data = {
            "link": f"{self.settings['site_root']}/",
            "date":
                datetime.datetime.fromtimestamp(
                    Path(article_index_file).stat().st_mtime)
                .strftime("%Y-%m-%dT%H:%M:%S+09:00")
            }
        base_articles_dir = self.settings["to"] / "articles"
        articles_file_paths = list(base_articles_dir.glob("*.html"))
        index_path = self.settings["to"] / "articles" / "index.html"
        article_files = [
            f for f in articles_file_paths if f.is_file() and f != index_path]

        article_data = [{
            "link":
                f"{self.settings['site_root']}/articles/{os.path.basename(f)}",
            "date":
                datetime.datetime.fromtimestamp(
                    Path(f).stat().st_mtime)
                .strftime("%Y-%m-%dT%H:%M:%S+09:00")
                }
            for f in article_files]

        sitemap_template = self.env.get_template("sitemap_template.xml")
        sitemap_xml = sitemap_template.render(
            article_index_data=article_index_data,
            article_data=article_data)
        with open(self.settings["to"] / "sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sitemap_xml)
        print("Sitemap regenerated successfully.")

import argparse
from textwrap import dedent

from swallow_init import swallow_init
from swallow_core import SwallowSSG

toml_path = "./config.toml"


def handle_init(args):
    swallow_init(args, toml_path)


def handle_add(args):
    generator = SwallowSSG()
    generator.add_article(target_file_default=args.file, no_interact=True)
    generator.regenerate_index()


def handle_regenerate(args):
    generator = SwallowSSG()
    if args.all:
        generator.regenerate_all_articles()
        generator.regenerate_index()
        generator.regenerate_sitemap()
        return
    match args.target:
        case "articles":
            generator.regenerate_all_articles()
        case "sitemap":
            generator.regenerate_sitemap()
        case "index":
            generator.regenerate_index()
        case _:
            raise ValueError("Invalid target for regeneration.")


def main():
    arg_parser = argparse.ArgumentParser(
        description="Static site generator made by Python")
    subparsers = arg_parser.add_subparsers(
        dest="mode",
        title="Modes",
        description="Available modes of operation")

    parser_init = subparsers.add_parser(
        "init", help="Initialize the project structure and config file. Also can be used to modify existing config.")
    parser_init.set_defaults(handler=handle_init)

    parser_add = subparsers.add_parser(
        "add", help="Add a new article and regenerate index.")
    parser_add.add_argument(
        "-F", "--file", dest="file", type=str,
        help="Target markdown file for adding article (required for 'add' mode).")
    parser_add.set_defaults(handler=handle_add)

    parser_regenerate = subparsers.add_parser(
        "regenerate", help="Regenerate index without adding new article.")
    parser_regenerate.add_argument(
        "-T", "--target", dest="target", choices=["index", "articles", "sitemap"], default="index",
        help="Specify what to regenerate: index (default), all articles, or sitemap.")
    parser_regenerate.add_argument(
        "-A", "--all", dest="all", action="store_true",
        help="Regenerate all articles, index, and sitemap (overrides -T).")
    parser_regenerate.set_defaults(handler=handle_regenerate)

    args = arg_parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)

    if not args.mode:
        message = dedent("""Select mode:
            1. Add Article and Regenerate Index
            2. Regenerate Index
            3. Regenerate All Articles and Index
            4. Regenerate Sitemap
            Enter choice (1/2/3/4): """)
        mode = input(message)
        generator = SwallowSSG()
        generator.run(mode=mode)


if __name__ == "__main__":
    main()

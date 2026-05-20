# Swallow

─ Convey your words without walls of language.

![PythonBadge](https://img.shields.io/badge/Python-3.14-3776AB?logo=python)
![Jinja2Badge](https://img.shields.io/badge/Jinja2-7E0C1B?logo=jinja)
![AlpineBadge](https://img.shields.io/badge/Alpine.js-3.x.x-8BC0D0?logo=alpinedotjs)

License: Mit License

## Table of Contents

<nav>
<ol>
<li><a href=#about>About</a></li>
<li><a href=#main_functions>Main functions</a></li>
<li><a href=#installation>Installation</a></li>
<li><a href=#writing>Write articles</a></li>
<li><a href=#contributing>Contributing</a></li>
<li><a href=#conclusion>Conclusion</a></li>
</ol>
</nav>

<section id=about>

## About

"Swallow" is a minimal, fast, multi-language SSG (Static Site Generator) written in Python and Alpine.js.

The most unique point is multi-language support. Swallow is made to fly over borders with your words. No longer worrying the language barrier.

</section>
<section id=main_functions>

## Main functions

Swallow has 3 main functions.

1. Multi-language
2. On-demand extensions loading
3. SPA-like transition

### 1. Multi-language

This is Swallow's core point. If you want to write articles in several languages, only to update settings and write another markdown ends with `_[language-code].md`.

Please make sure all of articles have translated version. Without this, build doesn't success.

Currently, We're considering to make "default message" settings, whitch displayed when translated version is not available. Please make patience for Update.

### 2. On-demand extensions loading

On client side, Swallow loads external scripts only if needed. If article requires Twitter embed post, load Twitter widget. If article requires code highlights, load Prism.js. However, not every time. Only to write like

```md
extensions:
 - Twitter
 - codeblock
```

in your article frontmatter, Swallow picks them, and loads appropriate time.

### 3. SPA-like transition

Exported JSON is not only for used to translate.

When you write ankerlinks between your articles, Swallow replaces only main contents. With prefetch, client doesn't have to see white screens and wait the article loaded.

</section>
<section id=installation>

## Installation

1. Clone this repository.
2. Run `poetry install` to install dependencies.
3. Run `swallow init` and input necessary settings.  
Note: "Enter the target directory path (e.g., ./dist)", where Blog index placed should be site root.
4. Write articles freely in `markdown\` !

</section>
<section id=writing>

## Write articles

Seeing is believing. This is an example with two languages, English and Japanese.

*YYYY-MM-DD_Hello_World_en.md*

```md
---
title_ja: こんにちは、世界！
title_en: Hello, World!
date: YYYY-MM-DD
tags:
  - blog
summary_ja: これはこのブログの記念すべき第一記事です
summary_en: This is my first article in my blog!
---
Hello, World!
```

*YYYY-MM-DD_Hello_World_ja.md*

```md
こんにちは、世界！
```

Swallow works with any file name of markdown ends with `_[language].md`, but for proper sorting, we recommend to include dates in the file name.

Frontmatter must be placed in your "default language" file.

- `title_[language]`: Title of article. Required for all languages.
- `date`: Date of this article published / written. This becomes ID, file name of this article HTML and JSON. Required.
- `tags`: Tag of this article. This can be used to tag search in index, so please use freely. Optional.
- `summary_[language]`: Summary of article. Required for all languages.
- `extensions`: Requires external scripts to Swallow.  
Currently, `Twitter` and `codeblock` is available. With your contribution, this function will be stronger. Optional.
- `draft`: If true, Swallow skips generation. Optional.

</section>
<section id=contributing>

## Contributing

Thank you for your interest! I'm welcoming contributions

for example...

- Add new extentions
- Add new custom themes
- Bug 🐞 Fixes

I'm waiting for your contributions!

I'll write CONTRIBUTING.md later, so please make patience a bit.

</section>
<section id=conclusion>

## Conclusion

Swallow fly over borders with your words.

Make your articles free from barrier of language.

</section>

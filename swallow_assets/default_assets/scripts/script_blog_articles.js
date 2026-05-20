// Blog Article Page Script

document.addEventListener('alpine:init', () => {
    Alpine.data('blogArticlePage', () => ({
        // Menu state
        open: false,

        // Language state
        lang: localStorage.getItem('selectedLang') || navigator.language.split('-')[0] || 'en',

        // Article state
        texts: null,
        currentURL: window.location.href,
        match: null,
        articleId: null,
        newerArticleId: null,
        olderArticleId: null,
        articles_cache: {},
        cacheSize: 5,
        extensionsManagerInstance: null,

        // Blog Metadata
        metaData: {},

        init() {
            const htmlTag = document.querySelector('html');
            htmlTag.removeAttribute('translate');

            this.extensionsManagerInstance = new ExtensionsManager();
            this.syncFromUrl();

            window.addEventListener('popstate', () => {
                this.syncFromUrl();
            });
            fetch('/metadata.json')
                .then(response => response.json())
                .then(data => {
                    this.metaData = data;
                    if (this.metaData["available_langs"].includes(this.lang)) {
                        this.toggleLanguage(this.lang);
                    } else {
                        this.toggleLanguage(this.metaData["default_lang"]);
                    }
                });
        },

        async prefetchArticle(targetArticleId) {
            if (!targetArticleId || this.articles_cache[targetArticleId] || targetArticleId === this.articleId) return;

            try {
                const response = await fetch(`/articles/${targetArticleId}.json`);
                if (response.ok) {
                    const data = await response.json();
                    this.articles_cache[targetArticleId] = data;
                    console.log(`Prefetched: ${targetArticleId}`);
                }
                if (Object.keys(this.articles_cache).length > this.cacheSize) {
                    const oldestKey = Object.keys(this.articles_cache)[0];
                    delete this.articles_cache[oldestKey];
                }
            } catch (error) {
                console.error('Prefetch error:', error);
            }
        },

        async loadLanguageFile(pushHistory = false) {
            if (!this.articleId) return;

            try {
                if (this.articles_cache[this.articleId]) {
                    this.articles_cache[this.articleId]["content"] =
                        this.escapeHtml(this.articles_cache[this.articleId]["content"]);
                    this.texts = this.articles_cache[this.articleId];
                    delete this.articles_cache[this.articleId];
                    this.articles_cache[this.articleId] = this.texts;
                } else {
                    const response = await fetch(`/articles/${this.articleId}.json`);
                    var data = await response.json();
                    data["content"] = this.escapeHtml(data["content"]);
                    this.texts = data;
                    this.articles_cache[this.articleId] = this.texts;
                }
                if (Object.keys(this.articles_cache).length > this.cacheSize) {
                    const oldestKey = Object.keys(this.articles_cache)[0];
                    delete this.articles_cache[oldestKey];
                }

                this.newerArticleId = this.texts.newer_article_id ?? null;
                this.olderArticleId = this.texts.older_article_id ?? null;

                this.updateLanguage();

                if (pushHistory) {
                    history.pushState({ articleId: this.articleId }, '', `/articles/${this.articleId}.html`);
                    window.scrollTo({ top: 0, behavior: "instant" });
                }
            } catch (error) {
                console.error('Error loading language file:', error);
            }
        },

        escapeHtml(text) {
            const articleContents = text;
            const allowedTags = ['h2', 'h3', 'h4', 'h5', 'h6', 'b', 'i', 'u', 'del', 'a', 'p', 'br',
                'hr', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'strong', 'em',
                'span', 'div', 'blockquote', 'code', 'pre', 'img', 'sup', 'sub', 'figure', 'figcaption',
                'cite', 'kbd', 'section', 'article', 'details', 'summary', 'nav'];
            const allowedAttributes = ['class', 'id', 'href', 'target', 'rel', 'src', 'alt', 'title'];

            for (const lang in articleContents) {
                if (articleContents.hasOwnProperty(lang)) {
                    articleContents[lang] = DOMPurify.sanitize(articleContents[lang], { ALLOWED_TAGS: allowedTags, ALLOWED_ATTR: allowedAttributes });
                };
            }
            return articleContents;
        },

        updateLanguage() {
            if (!this.texts) return;

            const htmlTag = document.querySelector('html');
            const title = this.texts.title?.[this.lang] ?? '';
            const summary = this.texts.summary?.[this.lang] ?? '';

            localStorage.setItem('selectedLang', this.lang);
            htmlTag.setAttribute('lang', this.lang);
            document.title = `${title} - ${this.metaData["site_name"][this.lang]}`;

            const ogTitle = document.querySelector('meta[property="og:title"]');
            const ogDescription = document.querySelector('meta[property="og:description"]');

            if (ogTitle) {
                ogTitle.setAttribute('content', `${title} - ${this.metaData["site_name"][this.lang]}`);
            }
            if (ogDescription) {
                ogDescription.setAttribute('content', `${this.metaData["site_description"][this.lang]} ${summary}`);
            }
            this.$nextTick(() => {
                this.solveExtensions(this.texts.extensions);
                this.enableBlogFunctions();
            });
        },

        solveExtensions(extensions) {
            if (extensions) {
                this.extensionsManagerInstance.reload(extensions);
            }
        },

        enableBlogFunctions() {
            this.activateToc();
            const links = document.querySelectorAll('.article-body a');
            if (!links) return;
            links.forEach(link => {
                const url = new URL(link.href);
                if (url.origin !== this.metaData["site_root"].origin) return;
                const match = link.getAttribute('href').match(/\/articles\/([0-9]{8})\.html$/);
                if (match) {
                    const targetArticleId = match[1];
                    link.setAttribute('@pointerenter', `prefetchArticle('${targetArticleId}')`);
                    link.setAttribute('@click.prevent', `showArticle('${targetArticleId}')`);
                }
            });
            Alpine.initTree(document.querySelector('.article-body'));
        },

        activateToc() {
            const tocElement = document.querySelector('.toc-container');
            if (tocElement) {
                tocElement.setAttribute('x-data', '{ open: true }');
                const tocButton = tocElement.querySelector('.toc-button');
                if (tocButton) {
                    tocButton.setAttribute('@click', 'open = !open');
                }
                const tocButtonIcon = tocElement.querySelector('.toc-button span');
                if (tocButtonIcon) {
                    tocButtonIcon.setAttribute('x-text', "open ? '▲' : '▼'");
                }
                const tocNav = tocElement.querySelector('.toc-nav');
                if (tocNav) {
                    tocNav.setAttribute('x-show', 'open');
                    tocNav.setAttribute('x-collapse', '');
                }
                Alpine.initTree(tocElement);
            }
        },

        async showArticle(targetArticleId) {
            if (!targetArticleId || targetArticleId === this.articleId) return;

            this.articleId = targetArticleId;
            await this.loadLanguageFile(true);
        },

        syncFromUrl() {
            const match = location.pathname.match(/\/articles\/([0-9]{8})\.html$/);
            if (match) {
                const articleId = match[1];
                if (articleId) {
                    if (this.articleId !== articleId) {
                        this.articleId = articleId;
                        this.loadLanguageFile(false);
                    }
                }
            } else {
                console.warn('Invalid or missing article format.');
            }
        },

        toggleLanguage(lang) {
            if (lang === this.lang) return;
            if (!this.metaData["available_langs"].includes(lang)) {
                console.warn(`Language ${lang} not available for this article.`);
                return;
            }
            this.lang = lang;
            this.updateLanguage();
        },
    }));
});

// Remove no-js class from article navigation for better styling when JavaScript is enabled

document.addEventListener('DOMContentLoaded', () => {
    const articleNavigation = document.querySelector('.article-navigation');
    if (articleNavigation) {
        articleNavigation.classList.remove('no-js');
    }
});
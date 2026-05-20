// Blog Page Script

let articlesData = null;
let isJapanese = localStorage.getItem('selectedLang') === 'ja' || navigator.language.startsWith('ja');

// Tag-Based Article Filtering

document.addEventListener('alpine:init', () => {
    Alpine.data('blogIndex', () => ({
        activeTags: [],
        articlesData: {},
        metaData: {},
        lang: localStorage.getItem('selectedLang') || navigator.language.split('-')[0] || 'en',

        init() {
            fetch('/metadata.json')
                .then(r => r.json())
                .then(data => {
                    this.metaData = data;
                    if (this.metaData["available_langs"].includes(this.lang)) {
                        this.toggleLanguage(this.lang);
                    } else {
                        this.toggleLanguage(this.metaData["default_lang"]);
                    }
                });
            fetch("/article_data.json")
                .then(r => r.json())
                .then(data => {
                    this.articlesData = data
                });
        },

        toggleTag(tag) {
            if (this.activeTags.includes(tag)) {
                this.activeTags = this.activeTags.filter(t => t !== tag)
            } else {
                this.activeTags.push(tag)
            }
        },

        isArticleVisible(id) {
            id = String(id)
            if (!this.articlesData || this.activeTags.length === 0)
                return true
            /** @type {{tags: string[]}} */
            const article = this.articlesData[id]
            return this.activeTags.every(tag =>
                article.tags.includes(tag)
            )
        },

        get hasNoResults() {
            if (!this.articlesData || this.activeTags.length === 0)
                return false
            return !Object.values(this.articlesData).some(article =>
                this.activeTags.every(tag =>
                    article.tags.includes(tag)
                )
            )
        },

        updateLanguage() {
            if (!this.articlesData) return;

            const htmlTag = document.querySelector('html');
            const title = this.articlesData?.title?.[this.lang] ?? '';
            const summary = this.articlesData?.summary?.[this.lang] ?? '';

            localStorage.setItem('selectedLang', this.lang);
            htmlTag.setAttribute('lang', this.lang);
            document.title = this.metaData["site_name"][this.lang];

            const ogTitle = document.querySelector('meta[property="og:title"]');
            const ogDescription = document.querySelector('meta[property="og:description"]');

            if (ogTitle) {
                ogTitle.setAttribute('content', this.metaData["site_name"][this.lang]);
            }
            if (ogDescription) {
                ogDescription.setAttribute('content', this.metaData["site_description"][this.lang]);
            }
        },

        toggleLanguage(lang) {
            if (lang === this.lang) return;
            if (!this.metaData["available_langs"].includes(lang)) {
                console.warn(`Language ${lang} not available for this article index.`);
                return;
            }
            this.lang = lang;
            this.updateLanguage();
        },
    }))
})

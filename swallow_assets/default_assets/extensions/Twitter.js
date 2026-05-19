// Twitter.js - An extension to embed Twitter posts when a Twitter URL is detected.

export default class TwitterExtension {
    constructor() {
        this.name = "Twitter";
        this.description = "Embeds Twitter posts when a Twitter URL is detected.";
    }

    initialize() {
        if (!window.twttr) {
            const script = document.createElement('script');
            script.src = 'https://platform.twitter.com/widgets.js';
            script.async = true;
            script.onload = () => {
                window.twttr?.widgets?.load();
            };
            document.head.appendChild(script);
        } else {
            this.reload();
        }
    }

    reload() {
        window.twttr?.widgets?.load();
    }
}
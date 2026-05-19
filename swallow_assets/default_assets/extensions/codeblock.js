// CodeBlockExtension.js - An extension to add Prism.js syntax highlighting to code blocks.

export default class CodeBlockExtension {
    constructor() {
        this.name = "CodeBlock";
        this.description = "Adds Prism.js syntax highlighting to code blocks.";
    }

    initialize() {
        if (!window.Prism) {
            const linkLight = document.createElement('link');
            linkLight.rel = 'stylesheet';
            linkLight.href = '/assets/prism/prism_light.css';
            linkLight.media = '(prefers-color-scheme: light)';
            document.head.appendChild(linkLight);
            const linkDark = document.createElement('link');
            linkDark.rel = 'stylesheet';
            linkDark.href = '/assets/prism/prism_dark.css';
            linkDark.media = '(prefers-color-scheme: dark)';
            document.head.appendChild(linkDark);
            const script = document.createElement('script');
            script.src = '/assets/prism/prism.js';
            script.async = true;
            document.head.appendChild(script);
            script.onload = () => {
                this.reload();
            };
        } else {
            this.reload();
        }
    }

    reload() {
        window.Prism?.highlightAll();
    }
}
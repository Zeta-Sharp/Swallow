// Solves and manages extensions for the blog/project articles page.

class ExtensionsManager {
    loadedExtensions = {};

    constructor() {

    }

    async init(extensions) {
        for (const extRaw of extensions) {
            const ext = this.purify(extRaw);
            if (!ext) continue;
            if (this.loadedExtensions[ext]) {
                console.warn(`Extension ${ext} is already loaded.`);
                continue;
            }
            try {
                const module = await import(`/assets/extensions/${ext}.js`);
                if (typeof module.default == "function") {
                    this.loadedExtensions[ext] = new module.default();
                    this.loadedExtensions[ext].initialize?.();
                } else {
                    console.warn(`Extension ${ext} does not export a default class.`);
                }
            } catch (err) {
                console.error(`Failed to load extension ${ext}.`);
            }
        }
    }

    async reload(extensions) {
        for (const extRaw of extensions) {
            const ext = this.purify(extRaw);
            if (!ext) continue;
            if (!this.loadedExtensions[ext]) {
                await this.init([ext]);
            }
            this.loadedExtensions[ext]?.reload?.();
        }
    }

    purify(string) {
        return string.replace(/[^a-zA-Z0-9\-_]/g, "");
    }
}
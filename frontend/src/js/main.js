import Navbar from '@components/navbar.js';
import {insert_icons} from "@helpers/helper_functions.js"
import {icons} from '@helpers/icons.js';


class App {
    constructor() {
        new Navbar();
        this.mainContent = document.getElementById('main-content')

        // Insert dashboard and prediction icons
        insert_icons({'nav-analysis': icons.dashboard, 'nav-prediction': icons.prediction});

        this.loadView('analysis');
        document.addEventListener('viewChanged', (e) => this.loadView(e.detail.view));
    }

    async loadView(view) {
        try {
            const response = await fetch(`./partials/${view}.html`); //Load the appropriate HTML
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const html = await response.text();
            this.mainContent.innerHTML = `<div class="content-area active">${html}</div>`; //Add fade-in animation class

            // Initialize view-specific JavaScript with a small delay
            setTimeout(() => {
                if (view === 'analysis' && typeof initAnalysisView === 'function') {
                    initAnalysisView();
                }
                else if (view === 'prediction' && typeof initPredictionView === 'function') {
                    initPredictionView();
                }
            }, 50);

        } catch (error) {
            console.error('Failed to load view:', error);
            this.mainContent.innerHTML = `
                <div class="flex items-center justify-center h-full">
                    <div class="text-center">${icons.error_svg}
                        <h2 class="text-xl font-semibold text-blue-800 mb-2">Failed to load content</h2>
                        <p class="text-blue-600">Please try again later.</p>
                        <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg 
                            hover:bg-blue-500">Retry</button>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => new App());

import initNavbar from '@components/navbar.js'
import {sidebar, initSidebarToggle} from '@components/sidebar.js'


class App {
    constructor() {
        this.mainContent = document.getElementById('main-content');
        this.currentView = null;

        this.initializeLayout();
        document.addEventListener('viewChanged', (e) => {
            const newView = e.detail.view;

            // Prevent reload if already active
            if (this.currentView === newView) return;

            this.loadView(newView);
        });
    };

    async initializeLayout() {
        // Load sidebar first
        await sidebar();

        // Initialize navbar AFTER sidebar exists
        initNavbar();
        initSidebarToggle();

        // Load default view
        this.loadView('analysis');
    }

    async loadView(view) {
        try {
            const response = await fetch(`./partials/${view}.html`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const html = await response.text();
            this.mainContent.innerHTML = `<div class="content-area active">${html}</div>`;
            this.currentView = view;

            // Initialize view-specific logic
            if (view === 'analysis' && typeof window.initAnalysisView === 'function') {
                window.initAnalysisView();
            } else if (view === 'prediction' && typeof window.initPredictionView === 'function') {
                window.initPredictionView();
            }

        } catch (error) {
            console.error('Failed to load view:', error);
            this.renderError();
        }
    }

    renderError() {
        this.mainContent.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="text-center">
                    <h2 class="text-xl font-semibold text-blue-800 mb-2">
                        Failed to load content
                    </h2>
                    <p class="text-blue-600">Please try again later.</p>
                    <button onclick="location.reload()"
                        class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500">
                        Retry
                    </button>
                </div>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => new App());

import Navbar from './components/navbar.js';


class App {
    constructor() {
        new Navbar();
        this.mainContent = document.getElementById('main-content');

        this.loadView('analysis');
        document.addEventListener('viewChanged', (e) => {
            this.loadView(e.detail.view);
        });
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
                    <div class="text-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-500 mb-4" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <h2 class="text-xl font-semibold text-steel-800 mb-2">Failed to load content</h2>
                        <p class="text-steel-600">Please try again later.</p>
                        <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-steel-600 text-white rounded-lg hover:bg-steel-500">Retry</button>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => new App());

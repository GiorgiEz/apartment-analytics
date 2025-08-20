import Navbar from './components/navbar.js';

// Main application controller
class App {
    constructor() {
        this.navbar = new Navbar();
        this.mainContent = document.getElementById('main-content');

        this.init();
    }

    init() {
        // Load default view
        this.loadView('analysis');

        // Listen for view changes
        document.addEventListener('viewChanged', (e) => {
            this.loadView(e.detail.view);
        });
    }

    async loadView(view) {
        try {
            // Show loading state
            this.mainContent.innerHTML = `
                <div class="flex items-center justify-center h-full">
                  <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-steel-600"></div>
                </div>
              `;

            // Load the appropriate HTML
            const response = await fetch(`./partials/${view}.html`);
            const html = await response.text();

            // Add fade-in animation class
            this.mainContent.innerHTML = `
                <div class="content-area active">
                  ${html}
                </div>
              `;

            // Initialize view-specific JavaScript
            if (view === 'analysis' && typeof initAnalysisView === 'function') {
                initAnalysisView();
            }
            else if (view === "prediction" && typeof initPredictionView === 'function') {
                initPredictionView();
            }

        } catch (error) {
            console.error('Failed to load view:', error);
            this.mainContent.innerHTML = `
                <div class="flex items-center justify-center h-full">
                  <div class="text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h2 class="text-xl font-semibold text-steel-800 mb-2">Failed to load content</h2>
                    <p class="text-steel-600">Please try again later.</p>
                  </div>
                </div>
              `;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new App();
});

// Make loadView available globally for direct calls
window.loadView = function(view) {
    const app = new App();
    app.loadView(view);
};
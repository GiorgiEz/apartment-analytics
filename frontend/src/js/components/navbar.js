// Navigation component
class Navbar {
    constructor() {
        this.navAnalysis = document.getElementById('nav-analysis');
        this.navPrediction = document.getElementById('nav-prediction');
        this.currentView = 'analysis'; // Default view

        this.init();
    }

    init() {
        // Add event listeners
        this.navAnalysis.addEventListener('click', () => this.setActiveView('analysis'));
        this.navPrediction.addEventListener('click', () => this.setActiveView('prediction'));
    }

    setActiveView(view) {
        // Update UI
        this.navAnalysis.classList.remove('active');
        this.navPrediction.classList.remove('active');

        if (view === 'analysis') {
            this.navAnalysis.classList.add('active');
            this.navAnalysis.classList.remove('hover:bg-steel-600');
        } else {
            this.navPrediction.classList.add('active');
            this.navPrediction.classList.remove('hover:bg-steel-600');
        }

        // Update current view
        this.currentView = view;

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('viewChanged', {
            detail: { view }
        }));
    }

    getCurrentView() {
        return this.currentView;
    }
}

// Export for use in other modules
export default Navbar;
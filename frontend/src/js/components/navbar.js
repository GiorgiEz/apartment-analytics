function initNavbar() {
    const navAnalysis = document.getElementById('nav-analysis');
    const navPrediction = document.getElementById('nav-prediction');

    if (!navAnalysis || !navPrediction) return;

    navAnalysis.addEventListener('click', () => setActiveView('analysis'));
    navPrediction.addEventListener('click', () => setActiveView('prediction'));

    function setActiveView(view) {
        navAnalysis.classList.remove('active');
        navPrediction.classList.remove('active');

        if (view === 'analysis') {
            navAnalysis.classList.add('active');
            navAnalysis.classList.remove('hover:bg-steel-600');
        } else {
            navPrediction.classList.add('active');
            navPrediction.classList.remove('hover:bg-steel-600');
        }

        document.dispatchEvent(new CustomEvent('viewChanged', {
            detail: { view }
        }));
    }
}
export default initNavbar;

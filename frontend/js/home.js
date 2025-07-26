document.addEventListener('DOMContentLoaded', () => {
  const mainContent = document.getElementById('main-content');
  const navAnalysis = document.getElementById('nav-analysis');
  const navPrediction = document.getElementById('nav-prediction');

  let currentScript = null;

  async function loadView(view, scriptPath) {
    try {
      const res = await fetch(`/html/${view}.html`);
      mainContent.innerHTML = await res.text();

      if (currentScript) {
        currentScript.remove();
      }
      
      // Dynamically load script after content is loaded
      currentScript = document.createElement("script");
      currentScript.src = scriptPath;
      currentScript.type = "text/javascript";
      currentScript.onload = () => {
        if (view === "analysis" && window.initAnalysisView) {
          window.initAnalysisView();
        }
        else if (view === "prediction" && window.initPredictionView) {
          window.initPredictionView()
        }
      };
      document.body.appendChild(currentScript);
    } catch (error) {
      mainContent.innerHTML = `<p class="text-red-500">Error loading view: ${error.message}</p>`;
      throw new Error('Error loading view: ' + error.message);
    }
  }

  loadView("analysis", "/js/analysis.js");  // Load analysis by default

  navAnalysis.addEventListener('click', () =>
      loadView('analysis', "/js/analysis.js"));
  navPrediction.addEventListener('click', () =>
      loadView('prediction', "/js/prediction.js"));
});

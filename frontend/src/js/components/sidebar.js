export async function sidebar() {
    try {
        const response = await fetch('partials/components/sidebar.html');
        if (!response.ok) {
            throw new Error(`Failed to load sidebar: ${response.status}`);
        }

        document.getElementById('sidebar-container').innerHTML = await response.text();

    } catch (error) {
        console.error(error);
    }
}

export function initSidebarToggle() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    const title = document.getElementById('sidebar_title');
    const navAnalysis = document.getElementById('nav-analysis');
    const navPrediction = document.getElementById('nav-prediction');

    if (!toggleBtn || !sidebar) return;

    const MOBILE_BREAKPOINT = 800;
    let collapsed = window.innerWidth < MOBILE_BREAKPOINT;

    function applyDesktopCollapsed() {
        sidebar.classList.remove('fixed');
        sidebar.classList.remove('w-64');
        sidebar.classList.add('w-14');

        overlay.classList.add('hidden');

        title.classList.add('hidden');
        navAnalysis.classList.add('hidden');
        navPrediction.classList.add('hidden');
    }

    function applyDesktopExpanded() {
        sidebar.classList.remove('fixed');
        sidebar.classList.remove('w-14');
        sidebar.classList.add('w-64');

        overlay.classList.add('hidden');

        title.classList.remove('hidden');
        navAnalysis.classList.remove('hidden');
        navPrediction.classList.remove('hidden');
    }

    function applyMobileClosed() {
        sidebar.classList.remove('w-64');
        sidebar.classList.add('w-14');
        sidebar.classList.remove('fixed');

        overlay.classList.add('hidden');

        title.classList.add('hidden');
        navAnalysis.classList.add('hidden');
        navPrediction.classList.add('hidden');
    }

    function applyMobileOpened() {
        sidebar.classList.remove('w-14');
        sidebar.classList.add('w-64');

        sidebar.classList.add('fixed', 'top-0', 'left-0', 'h-full');

        overlay.classList.remove('hidden');

        title.classList.remove('hidden');
        navAnalysis.classList.remove('hidden');
        navPrediction.classList.remove('hidden');
    }

    toggleBtn.addEventListener('click', () => {
        const isMobile = window.innerWidth < MOBILE_BREAKPOINT;

        collapsed = !collapsed;

        if (isMobile) {
            collapsed ? applyMobileClosed() : applyMobileOpened();
        } else {
            collapsed ? applyDesktopCollapsed() : applyDesktopExpanded();
        }
    });

    overlay.addEventListener('click', () => {
        if (window.innerWidth < MOBILE_BREAKPOINT) {
            collapsed = true;
            applyMobileClosed();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth < MOBILE_BREAKPOINT) {
            collapsed = true;
            applyMobileClosed();
        } else {
            collapsed = false;
            applyDesktopExpanded();
        }
    });

    // Initial state
    if (collapsed) {
        applyMobileClosed();
    } else {
        applyDesktopExpanded();
    }
}

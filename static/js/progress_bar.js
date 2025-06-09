
function initProgressTracker() {
 
    const config = {
        totalPointsNeeded: 100,
        currentPoints: 20,
        progressFillId: 'progressFill',
        pointsCountSelector: '.points-count',
        progressTitleSelector: '.progress-title'
    };


    const elements = {
        progressFill: document.getElementById(config.progressFillId),
        pointsCount: document.querySelector(config.pointsCountSelector),
        progressTitle: document.querySelector(config.progressTitleSelector),
        container: document.querySelector('.progress-container')
    };

    function calculateProgress() {
        const progressPercentage = (config.currentPoints / config.totalPointsNeeded) * 100;
        animateProgressBar(progressPercentage);
    }

    function animateProgressBar(percentage) {
        setTimeout(() => {
            elements.progressFill.style.width = `${percentage}%`;
        }, 300);
    }

    function updatePointsDisplay() {
        elements.pointsCount.textContent = `Points accumulated this week: ${config.currentPoints}`;
        elements.progressTitle.textContent = `Awesome! you are ${config.totalPointsNeeded - config.currentPoints} points away from gold!`;
    }

    // buat tes klik biar nambah 10 pts
    function setupDemoInteraction() {
        elements.container.addEventListener('click', function() {
            config.currentPoints = Math.min(config.currentPoints + 10, config.totalPointsNeeded);           
            const newPercentage = (config.currentPoints / config.totalPointsNeeded) * 100;
            elements.progressFill.style.width = `${newPercentage}%`;
            updatePointsDisplay();
        });
    }

    updatePointsDisplay();
    calculateProgress();
    setupDemoInteraction();
}

initProgressTracker();
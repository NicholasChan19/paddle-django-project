document.addEventListener("DOMContentLoaded", function () {
    const countdownElement = document.getElementById("countdown");

    function getNextMonthStart() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth();
        return new Date(year, month + 1, 1, 0, 0, 0);
    }

    function updateCountdown() {
        const now = new Date();
        const target = getNextMonthStart();
        const diff = target - now;

        if (diff <= 0) {
            countdownElement.textContent = "Rank has been reset!";
            clearInterval(intervalId);
            return;
        }

        const seconds = Math.floor(diff / 1000) % 60;
        const minutes = Math.floor(diff / (1000 * 60)) % 60;
        const hours = Math.floor(diff / (1000 * 60 * 60)) % 24;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        const formatted = `${days} days ${hours} hours ${minutes} minutes ${seconds} seconds`;
        countdownElement.textContent = `Rank resets in: ${formatted}`;
    }

    const intervalId = setInterval(updateCountdown, 1000);
    updateCountdown();
});

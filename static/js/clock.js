function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-GB');

    //settingan format
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateString = now.toLocaleDateString(undefined, options);

    document.getElementById('current-time').textContent = timeString;
    document.getElementById('current-date').textContent = dateString;
}

updateClock();
setInterval(updateClock, 1000);


const config = {
    updatedSummary: 21,
    updatedCerti: 1,
    updatedClasses: 46
};
    
function updateStats(){
    document.getElementById('summaryValue').textContent = config.updatedSummary;
    document.getElementById('certificatesValue').textContent = config.updatedCerti;
    document.getElementById('classesValue').textContent = config.updatedClasses;
};

updateStats()
// Replace this with your actual API URL
const API_URL = 'https://ebantisaiapi.ebantis.com/aiapi/v1.0/activitydetails';

// Fetch and display data
async function fetchProductivityData(employeeId) {
    const currentTime = new Date();
    const fromDate = new Date(currentTime.setHours(0, 0, 0, 0)).toISOString();
    const toDate = new Date(currentTime.setHours(23, 59, 59, 999)).toISOString();

    const body = {
        fromDate,
        toDate,
        employeeTransactionId: employeeId,
    };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (response.ok) {
            const data = await response.json();
            displayResults(data);
        } else {
            displayError('No data found or an error occurred.');
        }
    } catch (error) {
        displayError('An error occurred while fetching the data.');
        console.error(error);
    }
}

// Display results on the page
function displayResults(data) {
    const resultSection = document.getElementById('resultSection');
    const resultContent = document.getElementById('resultContent');
    resultContent.innerHTML = '';

    const activityDetails = data.ActivityDetails || {};
    const productivityGraph = data.ProductivityGraph || [];

    let content = `
        <p><strong>Productivity Ratio:</strong> ${activityDetails.ProductivityRatio || 'N/A'}%</p>
        <p><strong>Total Time:</strong> ${activityDetails.totalTime || 'N/A'}</p>
        <p><strong>Active Time:</strong> ${activityDetails.ActiveTime || 'N/A'}</p>
        <p><strong>Undefined Time:</strong> ${activityDetails.UndefinedTime || 'N/A'}</p>
        <hr>
        <h5>Productivity Graph:</h5>
    `;

    productivityGraph.forEach(entry => {
        content += `<p><strong>Date:</strong> ${entry.productivityDate || 'N/A'}</p>`;
        entry.collectedData.forEach(data => {
            content += `<p>Start Time: ${data.StartTime || 'N/A'} | Duration: ${data.Duration || 'N/A'}s</p>`;
        });
    });

    resultContent.innerHTML = content;
    resultSection.classList.remove('d-none');
}

// Display error message
function displayError(message) {
    const resultSection = document.getElementById('resultSection');
    const resultContent = document.getElementById('resultContent');
    resultContent.innerHTML = `<p class="text-danger">${message}</p>`;
    resultSection.classList.remove('d-none');
}

// Handle form submission
document.getElementById('employeeForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const employeeId = document.getElementById('employeeId').value;
    fetchProductivityData(employeeId);
});

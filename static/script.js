document.addEventListener('DOMContentLoaded', () => {
    fetchReport();

    const form = document.getElementById('chat-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleChat();
    });
});

async function fetchReport() {
    try {
        const response = await fetch('/api/report');
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        // Update Metrics
        document.getElementById('accuracy-val').innerText = (data.accuracy * 100).toFixed(1) + '%';
        document.getElementById('hallucination-val').innerText = (data.hallucination_rate * 100).toFixed(1) + '%';
        document.getElementById('total-tests-val').innerText = data.total_tests;

        // Render Chart
        renderChart(data.failure_distribution);

    } catch (err) {
        console.error("Failed to fetch report:", err);
    }
}

function renderChart(distribution) {
    const ctx = document.getElementById('failureChart').getContext('2d');
    
    // Gradient for the chart
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0.8)');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(distribution),
            datasets: [{
                data: Object.values(distribution),
                backgroundColor: [
                    '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f8fafc', font: { family: 'Inter' } }
                }
            },
            cutout: '70%'
        }
    });
}

async function handleChat() {
    const context = document.getElementById('context-input').value;
    const question = document.getElementById('question-input').value;
    const btnText = document.querySelector('.btn-primary span');
    const spinner = document.getElementById('loading-spinner');
    const resultBox = document.getElementById('result-box');

    if (!context || !question) return;

    // UI Loading state
    btnText.style.display = 'none';
    spinner.style.display = 'block';
    resultBox.classList.add('hidden');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context, question })
        });

        const data = await response.json();

        // Populate results
        document.getElementById('res-answer').innerText = data.Answer || 'N/A';
        document.getElementById('res-confidence').innerText = data.Calculated_Confidence 
            ? (data.Calculated_Confidence * 100).toFixed(1) + '%' 
            : '0%';
        
        const quotesList = document.getElementById('res-quotes');
        quotesList.innerHTML = '';
        if (data.Quotes_Cited && data.Quotes_Cited.length > 0) {
            data.Quotes_Cited.forEach(q => {
                const li = document.createElement('li');
                li.innerText = q;
                quotesList.appendChild(li);
            });
        } else {
            quotesList.innerHTML = '<li>No quotes cited.</li>';
        }

        resultBox.classList.remove('hidden');
    } catch (err) {
        console.error("Chat error:", err);
    } finally {
        btnText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

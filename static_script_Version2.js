document.getElementById('scanBtn').onclick = async function() {
    const text = document.getElementById('inputText').value.trim();
    const resultDiv = document.getElementById('result');
    resultDiv.style.display = 'none';

    if (!text) {
        resultDiv.textContent = "Please paste a message to scan.";
        resultDiv.className = "result";
        resultDiv.style.display = 'block';
        return;
    }

    resultDiv.textContent = "Scanning...";
    resultDiv.className = "result";
    resultDiv.style.display = 'block';

    try {
        const resp = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await resp.json();

        let cls = "low";
        if (data.likelihood.toLowerCase() === "high") cls = "high";
        else if (data.likelihood.toLowerCase() === "medium") cls = "medium";

        resultDiv.innerHTML = `<strong>Scam Likelihood: <span>${data.likelihood}</span></strong><br>
        <ul>${data.reasons.map(r => `<li>${r}</li>`).join('')}</ul>`;
        resultDiv.className = `result ${cls}`;
    } catch (e) {
        resultDiv.textContent = "Failed to scan. Please try again.";
        resultDiv.className = "result";
    }
};
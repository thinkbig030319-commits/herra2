async function scanFile() {
    const fileInput = document.getElementById("fileInput");
    const resultDiv = document.getElementById("result");

    if (fileInput.files.length === 0) {
        resultDiv.innerHTML = "⚠ Please select a file.";
        resultDiv.style.color = "orange";
        return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
        resultDiv.innerHTML = "⚠ You must be logged in to scan files.";
        resultDiv.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("http://localhost:8000/scan", {
            method: "POST",
            headers: {
                // BUG FIX: Was hitting port 5000 but API runs on 8000.
                // Also added Authorization header — /scan now requires auth.
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        // BUG FIX: Was checking data.malware (doesn't exist).
        // API returns threat_level: "HIGH" or "LOW".
        if (data.threat_level === "HIGH") {
            resultDiv.innerHTML = `❌ Threat Detected! (${data.yara_result} / AI: ${data.ai_prediction} @ ${(data.confidence * 100).toFixed(1)}%)`;
            resultDiv.style.color = "red";
        } else {
            resultDiv.innerHTML = `✅ File is Safe. (AI: ${data.ai_prediction} @ ${(data.confidence * 100).toFixed(1)}%)`;
            resultDiv.style.color = "green";
        }

    } catch (error) {
        resultDiv.innerHTML = "Server Error. Make sure backend is running.";
        resultDiv.style.color = "red";
    }
}
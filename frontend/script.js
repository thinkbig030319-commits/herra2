const API = "http://localhost:8000";

// On page load, show correct card
window.onload = () => {
    if (localStorage.getItem("token")) showScanCard();
};

function showScanCard() {
    document.getElementById("authCard").style.display = "none";
    document.getElementById("scanCard").style.display = "block";
}

function showAuthCard() {
    document.getElementById("authCard").style.display = "block";
    document.getElementById("scanCard").style.display = "none";
}

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    const el = document.getElementById("authResult");
    if (res.ok) {
        el.style.color = "green";
        el.innerHTML = "✅ Registered! Now login.";
    } else {
        el.style.color = "red";
        el.innerHTML = `❌ ${data.error}`;
    }
}

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    const el = document.getElementById("authResult");
    if (res.ok) {
        localStorage.setItem("token", data.access_token);
        showScanCard();
    } else {
        el.style.color = "red";
        el.innerHTML = `❌ ${data.error}`;
    }
}

function logout() {
    localStorage.removeItem("token");
    showAuthCard();
}

async function scanFile() {
    const fileInput = document.getElementById("fileInput");
    const resultDiv = document.getElementById("result");

    if (fileInput.files.length === 0) {
        resultDiv.innerHTML = "⚠ Please select a file.";
        resultDiv.style.color = "orange";
        return;
    }

    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch(`${API}/scan`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData
        });
        const data = await response.json();

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
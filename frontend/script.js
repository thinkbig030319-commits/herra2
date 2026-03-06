async function scanFile() {
    const fileInput = document.getElementById("fileInput");
    const resultDiv = document.getElementById("result");

    if (fileInput.files.length === 0) {
        resultDiv.innerHTML = "⚠ Please select a file.";
        resultDiv.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("http://localhost:5000/scan", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.malware === true) {
            resultDiv.innerHTML = "❌ Malware Detected!";
            resultDiv.style.color = "red";
        } else {
            resultDiv.innerHTML = "✅ File is Safe.";
            resultDiv.style.color = "green";
        }

    } catch (error) {
        resultDiv.innerHTML = "Server Error. Make sure backend is running.";
        resultDiv.style.color = "red";
    }
}
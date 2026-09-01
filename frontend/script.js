const imageUpload = document.getElementById("imageUpload");
const contributorSelect = document.getElementById("contributor");
const previewImage = document.getElementById("previewImage");
const noImageText = document.getElementById("noImageText");
const analyzeBtn = document.getElementById("analyzeBtn");

const prediction = document.getElementById("prediction");
const confidence = document.getElementById("confidence");

const imageIntegrity = document.getElementById("imageIntegrity");
const modelIntegrity = document.getElementById("modelIntegrity");
const inferenceIntegrity = document.getElementById("inferenceIntegrity");
const overallStatus = document.getElementById("overallStatus");

// Handle Image Preview
imageUpload.addEventListener("change", function () {
    const file = imageUpload.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            previewImage.src = event.target.result;
            previewImage.style.display = "block";
            noImageText.style.display = "none";
        };
        reader.readAsDataURL(file);
    }
});

// Run End-to-End Pipeline
analyzeBtn.addEventListener("click", async function () {
    const file = imageUpload.files[0];
    if (!file) {
        alert("Please select an image first!");
        return;
    }

    // Set Loading States
    prediction.textContent = "ANALYZING...";
    confidence.textContent = "--";
    imageIntegrity.textContent = "CHECKING...";
    modelIntegrity.textContent = "CHECKING...";
    inferenceIntegrity.textContent = "CHECKING...";
    overallStatus.textContent = "PROCESSING...";
    overallStatus.className = "status waiting";

    // Build Payload matching backend/main.py parameters
    const formData = new FormData();
    formData.append("file", file);
    formData.append("contributor", contributorSelect ? contributorSelect.value : "Default Contributor");
    formData.append("model_version", "yolo_v8_recon");
    formData.append("simulate_poison", "false");
    formData.append("simulate_backdoor", "false");
    formData.append("simulate_tamper", "false");

    try {
        const response = await fetch("/process-pipeline", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();

        // Update UI with response data
        prediction.textContent = `🚗 ${data.prediction}`;
        confidence.textContent = data.confidence;

        imageIntegrity.textContent = `${data.checks.image_integrity} PASS`;
        modelIntegrity.textContent = `${data.checks.model_integrity} PASS`;
        inferenceIntegrity.textContent = `${data.checks.result_integrity} PASS`;

        if (data.is_trusted) {
            overallStatus.textContent = `🟢 ${data.status}`;
            overallStatus.className = "status trusted";
        } else {
            overallStatus.textContent = `🔴 ${data.status}`;
            overallStatus.className = "status compromised";
        }

    } catch (err) {
        console.error("API error:", err);
        overallStatus.textContent = "⚠️ SERVER ERROR";
        overallStatus.className = "status error";
        alert("Failed to connect to FastAPI backend. Check the server terminal.");
    }
});
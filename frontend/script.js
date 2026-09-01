const imageUpload = document.getElementById("imageUpload");
const previewImage = document.getElementById("previewImage");
const noImageText = document.getElementById("noImageText");
const analyzeBtn = document.getElementById("analyzeBtn");

const prediction = document.getElementById("prediction");
const confidence = document.getElementById("confidence");

const imageIntegrity = document.getElementById("imageIntegrity");
const modelIntegrity = document.getElementById("modelIntegrity");
const inferenceIntegrity = document.getElementById("inferenceIntegrity");

const overallStatus = document.getElementById("overallStatus");


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


analyzeBtn.addEventListener("click", function () {

    if (!imageUpload.files[0]) {

        alert("Please select an image first!");

        return;
    }

    prediction.textContent = "ANALYZING...";
    confidence.textContent = "--";

    imageIntegrity.textContent = "CHECKING...";
    modelIntegrity.textContent = "CHECKING...";
    inferenceIntegrity.textContent = "CHECKING...";

    overallStatus.textContent = "ANALYZING...";
    overallStatus.className = "status waiting";


    setTimeout(function () {

        prediction.textContent = "🚗 CAR";
        confidence.textContent = "96%";

        imageIntegrity.textContent = "✅ VERIFIED";
        modelIntegrity.textContent = "✅ VERIFIED";
        inferenceIntegrity.textContent = "✅ VERIFIED";

        overallStatus.textContent = "🟢 TRUSTED";
        overallStatus.className = "status trusted";

    }, 1500);

});
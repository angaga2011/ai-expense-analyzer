"use strict";

const API_URL = "http://127.0.0.1:8000";

async function analyze() {
    const fileInput = document.getElementById("file");
    const btn = document.getElementById("analyzeBtn");
    const resultCard = document.getElementById("result");
    const errorCard = document.getElementById("error");
    const output = document.getElementById("output");
    const errorMsg = document.getElementById("errorMsg");

    resultCard.style.display = "none";
    errorCard.style.display = "none";

    const file = fileInput.files[0];
    if (!file) {
        showError("Please select a file before analyzing.");
        return;
    }

    btn.disabled = true;
    btn.textContent = "Analyzing…";

    try {
        const file_base64 = await encodeBase64(file);

        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify({
                file_name: file.name,
                content_type: file.type,
                file_base64,
            }),
        });

        const data = await response.json();
        output.textContent = JSON.stringify(data, null, 2);
        resultCard.style.display = "block";
    } catch (err) {
        showError(`Request failed: ${err.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = "Analyze";
        fileInput.value = "";
    }
}

function encodeBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.toString().replace(/^data:(.*,)?/, ""));
        reader.onerror = (err) => reject(err);
    });
}

function previewFile(input) {
    const preview = document.getElementById("preview");
    const file = input.files[0];
    if (!file || file.type === "application/pdf") {
        preview.style.display = "none";
        return;
    }
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
    preview.onclick = () => openModal(preview.src);
}

function openModal(src) {
    document.getElementById("modalImg").src = src;
    document.getElementById("modal").style.display = "flex";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

function showError(message) {
    const errorCard = document.getElementById("error");
    document.getElementById("errorMsg").textContent = message;
    errorCard.style.display = "block";
}

"use strict";

const API_URL = "http://127.0.0.1:8000";

async function analyze() {
  const fileInput = document.getElementById("file");
  const btn = document.getElementById("analyzeBtn");
  const resultSection = document.getElementById("result");
  const errorCard = document.getElementById("error");

  resultSection.style.display = "none";
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

    document.getElementById("output").textContent = JSON.stringify(data, null, 2);

    if (data.success && data.data) {
      renderFormatted(data.data);
    }

    resultSection.style.display = "block";
    switchView("formatted");

  } catch (err) {
    showError(`Request failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze Document";
    fileInput.value = "";
  }
}

function renderFormatted(data) {
  setText("fDocType", formatDocType(data.document_type));
  setText("fEntity", data.entity || "—");
  setText("fDate", data.date !== "N/A" ? formatDate(data.date) : "—");
  setText("fAmount", data.amount !== "N/A" ? `$${data.amount}` : "—");
  setText("fSummary", data.summary || "");

  const items = data.line_items?.items || [];
  const summary = data.line_items?.summary || [];

  const itemsBody = document.getElementById("itemsBody");
  const summaryBody = document.getElementById("summaryBody");
  itemsBody.innerHTML = "";
  summaryBody.innerHTML = "";

  items.forEach(item => {
    itemsBody.appendChild(makeRow(item.text, item.amount));
  });

  summary.forEach(item => {
    summaryBody.appendChild(makeRow(item.text, item.amount, true));
  });

  const lineItemsSection = document.getElementById("lineItemsSection");
  const summaryTableBlock = document.getElementById("summaryTableBlock");

  lineItemsSection.style.display = (items.length > 0 || summary.length > 0) ? "block" : "none";
  summaryTableBlock.style.display = summary.length > 0 ? "block" : "none";
}

function makeRow(label, amount, isBold = false) {
  const tr = document.createElement("tr");
  if (isBold) tr.classList.add("total-row");
  tr.innerHTML = `
    <td>${escapeHtml(label)}</td>
    <td class="col-amount mono">$${escapeHtml(amount)}</td>
  `;
  return tr;
}

function switchView(view) {
  const isFormatted = view === "formatted";
  document.getElementById("viewFormatted").style.display = isFormatted ? "block" : "none";
  document.getElementById("viewRaw").style.display = isFormatted ? "none" : "block";
  document.getElementById("btnFormatted").classList.toggle("active", isFormatted);
  document.getElementById("btnRaw").classList.toggle("active", !isFormatted);
}

function formatDocType(raw) {
  if (!raw) return "—";
  return raw.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

function formatDate(dateStr) {
  try {
    const [y, m, d] = dateStr.split("-");
    const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    return `${months[parseInt(m, 10) - 1]} ${parseInt(d, 10)}, ${y}`;
  } catch {
    return dateStr;
  }
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
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
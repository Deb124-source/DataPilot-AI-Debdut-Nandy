const API_URL = "https://datapilot-ai-debdut-nandy.onrender.com";

let datasetId = null;
let cleanedDatasetId = null;
let selectedFile = null;
let cleaningSuggestions = [];
let activeCharts = [];

const fileInput = document.getElementById("file-input");
const chooseFileButton = document.getElementById("choose-file-btn");
const uploadButton = document.getElementById("upload-btn");
const uploadArea = document.getElementById("upload-area");
const selectedFileContainer = document.getElementById("selected-file");
const selectedFileName = document.getElementById("selected-file-name");

const navItems = document.querySelectorAll(".nav-item");
const contentSections = document.querySelectorAll(".content-section");
const pageTitle = document.getElementById("page-title");

navItems.forEach(item => {
    item.addEventListener("click", () => {
        const section = item.dataset.section;

        navItems.forEach(nav => nav.classList.remove("active"));
        contentSections.forEach(content => content.classList.remove("active"));

        item.classList.add("active");

        const selectedSection = document.getElementById(section);
        if (selectedSection) selectedSection.classList.add("active");

        pageTitle.textContent = item.textContent.trim();

        if (section === "datasets") loadDatasets();
    });
});

chooseFileButton.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", event => {
    const file = event.target.files[0];
    if (!file) return;

    selectedFile = file;
    selectedFileName.textContent = file.name;
    selectedFileContainer.classList.remove("hidden");
});

uploadArea.addEventListener("dragover", event => {
    event.preventDefault();
    uploadArea.classList.add("drag-over");
});

uploadArea.addEventListener("dragleave", () => {
    uploadArea.classList.remove("drag-over");
});

uploadArea.addEventListener("drop", event => {
    event.preventDefault();
    uploadArea.classList.remove("drag-over");

    const file = event.dataTransfer.files[0];
    if (!file) return;

    selectedFile = file;
    selectedFileName.textContent = file.name;
    selectedFileContainer.classList.remove("hidden");
});

uploadButton.addEventListener("click", uploadDataset);

async function uploadDataset() {
    if (!selectedFile) {
        alert("Please select a dataset first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    uploadButton.textContent = "Uploading...";
    uploadButton.disabled = true;

    try {
        const response = await fetch(`${API_URL}/upload/`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed.");
        }

        datasetId = data.dataset_id;

        updateActiveDatasetUI(data.filename);
        displayUploadResult(data);
        displayDatasetPreview(data);
        loadDatasets();

        alert("Dataset uploaded successfully!");

    } catch (error) {
        alert("Upload Error: " + error.message);
    } finally {
        uploadButton.textContent = "Upload Dataset";
        uploadButton.disabled = false;
    }
}

function displayUploadResult(data) {
    const container = document.getElementById("upload-result");

    container.innerHTML = `
        <div class="result-card">
            <h2>Dataset Uploaded Successfully</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>${data.rows}</h3>
                    <p>Rows</p>
                </div>

                <div class="stat-card">
                    <h3>${data.columns}</h3>
                    <p>Columns</p>
                </div>
            </div>

            <h3>Columns</h3>

            <div class="column-list">
                ${data.column_names.map(column =>
                    `<span class="column-tag">${escapeHtml(column)}</span>`
                ).join("")}
            </div>
        </div>
    `;
}

function displayDatasetPreview(data) {
    const container = document.getElementById(
        "dataset-preview-container"
    );

    if (!data.preview || data.preview.length === 0) return;

    const columns = data.column_names;

    let html = `
        <div class="preview-card">
            <h2>Dataset Preview</h2>
            <div class="table-wrapper">
                <table>
                    <thead><tr>
    `;

    columns.forEach(column => {
        html += `<th>${escapeHtml(column)}</th>`;
    });

    html += `</tr></thead><tbody>`;

    data.preview.forEach(row => {
        html += "<tr>";

        columns.forEach(column => {
            const value = row[column] ?? "—";
            html += `<td>${escapeHtml(String(value))}</td>`;
        });

        html += "</tr>";
    });

    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function updateActiveDatasetUI(filename) {
    document.getElementById(
        "active-dataset-label"
    ).textContent = `Active: ${filename}`;

    document.getElementById(
        "dataset-status"
    ).textContent = "Dataset Active";
}

document.getElementById(
    "generate-profile-btn"
).addEventListener("click", generateProfile);

async function generateProfile() {
    if (!datasetId) {
        alert("Please upload or select a dataset first.");
        return;
    }

    const container = document.getElementById("profile-content");
    container.innerHTML = `<div class="empty-state">Generating dataset profile...</div>`;

    try {
        const response = await fetch(`${API_URL}/profile/${datasetId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Profile generation failed.");
        }

        displayProfile(data.profile);

    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                Profile Error:<br>${escapeHtml(error.message)}
            </div>
        `;
    }
}

function displayProfile(profile) {
    const container = document.getElementById("profile-content");

    let html = `
        <div class="result-card">
            <h2>Dataset Overview</h2>

            <div class="stats-grid">
                <div class="stat-card"><h3>${profile.rows}</h3><p>Rows</p></div>
                <div class="stat-card"><h3>${profile.columns}</h3><p>Columns</p></div>
                <div class="stat-card"><h3>${profile.missing_values}</h3><p>Missing Values</p></div>
                <div class="stat-card"><h3>${profile.duplicate_rows}</h3><p>Duplicates</p></div>
            </div>
        </div>

        <div class="result-card">
            <h2>Column Information</h2>
    `;

    Object.entries(profile.column_info || {}).forEach(
        ([column, info]) => {
            html += `
                <div class="profile-column-card">
                    <h3>${escapeHtml(column)}</h3>
                    <p><strong>Data Type:</strong> ${escapeHtml(String(info.dtype ?? "—"))}</p>
                    <p><strong>Missing Values:</strong> ${info.missing_values ?? "—"}</p>
                    <p><strong>Unique Values:</strong> ${info.unique_values ?? "—"}</p>
                </div>
            `;
        }
    );

    html += `</div>`;
    container.innerHTML = html;
}

document.getElementById(
    "analyze-cleaning-btn"
).addEventListener("click", analyzeCleaning);

async function analyzeCleaning() {
    if (!datasetId) {
        alert("Please upload or select a dataset first.");
        return;
    }

    const container = document.getElementById("cleaning-content");
    container.innerHTML = `<div class="empty-state">Analyzing dataset...</div>`;

    try {
        const response = await fetch(
            `${API_URL}/cleaning/suggestions/${datasetId}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Cleaning analysis failed.");
        }

        displayCleaningSuggestions(data);

    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                Cleaning Analysis Error:<br>${escapeHtml(error.message)}
            </div>
        `;
    }
}

function displayCleaningSuggestions(data) {
    cleaningSuggestions = data.suggestions || [];

    const container = document.getElementById("cleaning-content");

    if (cleaningSuggestions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                Your dataset looks clean!
            </div>
        `;
        return;
    }

    container.innerHTML = "";

    cleaningSuggestions.forEach((suggestion, index) => {
        const card = document.createElement("div");
        card.className = "suggestion-card";

        card.innerHTML = `
            <h3>${escapeHtml(suggestion.issue.replaceAll("_", " "))}</h3>
            <pre>${escapeHtml(JSON.stringify(suggestion, null, 2))}</pre>
            <button class="primary-btn apply-single-btn"
                data-index="${index}">
                Apply This Fix
            </button>
        `;

        container.appendChild(card);
    });

    document.querySelectorAll(".apply-single-btn")
        .forEach(button => {
            button.addEventListener("click", () => {
                applySingleCleaning(
                    cleaningSuggestions[Number(button.dataset.index)]
                );
            });
        });
}

function suggestionToOperation(suggestion) {
    if (suggestion.issue === "missing_values") {
        return {
            type: "fill_missing",
            column: suggestion.column,
            strategy: suggestion.recommended_action
        };
    }

    if (suggestion.issue === "duplicate_rows") {
        return {
            type: "remove_duplicates"
        };
    }

    if (suggestion.issue === "potential_outliers") {
        return {
            type: "cap_outliers",
            column: suggestion.column
        };
    }

    return null;
}

async function applySingleCleaning(suggestion) {
    const operation = suggestionToOperation(suggestion);

    if (!operation) {
        alert("Unsupported cleaning operation.");
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/cleaning/apply/${datasetId}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    operations: [operation]
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Cleaning failed.");
        }

        displayCleaningResult(data);

    } catch (error) {
        alert("Cleaning Error: " + error.message);
    }
}

const applyAllCleaningButton = document.getElementById(
    "apply-all-cleaning-btn"
);

applyAllCleaningButton.addEventListener(
    "click",
    applyAllCleaning
);

async function applyAllCleaning() {
    if (!datasetId) {
        alert("Please upload or select a dataset first.");
        return;
    }

    applyAllCleaningButton.textContent = "Cleaning Dataset...";
    applyAllCleaningButton.disabled = true;

    try {
        const response = await fetch(
            `${API_URL}/cleaning/apply-recommended/${datasetId}`,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Cleaning failed.");
        }

        displayCleaningResult(data);

    } catch (error) {
        alert("Cleaning Error: " + error.message);
    } finally {
        applyAllCleaningButton.textContent =
            "Apply All Recommendations";
        applyAllCleaningButton.disabled = false;
    }
}

function displayCleaningResult(data) {
    cleanedDatasetId = data.cleaned_dataset_id;
    datasetId = cleanedDatasetId;

    loadDatasets();

    const container = document.getElementById("cleaning-content");

    container.innerHTML = `
        <div class="cleaning-result">
            <h2>Cleaning Completed Successfully</h2>

            <div class="before-after-grid">
                <div class="comparison-card">
                    <h3>Before Cleaning</h3>
                    <p>Rows: ${data.before.rows}</p>
                    <p>Columns: ${data.before.columns}</p>
                    <p>Missing Values: ${data.before.missing_values}</p>
                    <p>Duplicate Rows: ${data.before.duplicate_rows}</p>
                </div>

                <div class="comparison-card">
                    <h3>After Cleaning</h3>
                    <p>Rows: ${data.after.rows}</p>
                    <p>Columns: ${data.after.columns}</p>
                    <p>Missing Values: ${data.after.missing_values}</p>
                    <p>Duplicate Rows: ${data.after.duplicate_rows}</p>
                </div>
            </div>

            <a class="download-btn"
                href="${API_URL}/cleaning/download/${cleanedDatasetId}"
                target="_blank">
                Download Cleaned Dataset
            </a>
        </div>
    `;
}

document.getElementById(
    "generate-eda-btn"
).addEventListener("click", generateEDA);

async function generateEDA() {
    if (!datasetId) {
        alert("Please upload or select a dataset first.");
        return;
    }

    const contentContainer =
        document.getElementById("eda-content");

    const chartsContainer =
        document.getElementById("eda-charts-container");

    const insightsContainer =
        document.getElementById("eda-insights-container");

    contentContainer.innerHTML =
        `<div class="empty-state">Running automated EDA...</div>`;

    chartsContainer.innerHTML = "";
    insightsContainer.innerHTML = "";

    try {
        const response = await fetch(
            `${API_URL}/eda/${datasetId}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "EDA failed.");
        }

        renderVisualEDA(data.eda);

    } catch (error) {
        contentContainer.innerHTML = `
            <div class="empty-state">
                EDA Error:<br>${escapeHtml(error.message)}
            </div>
        `;
    }
}

function destroyCharts() {
    activeCharts.forEach(chart => chart.destroy());
    activeCharts = [];
}

function renderVisualEDA(eda) {
    destroyCharts();

    const contentContainer =
        document.getElementById("eda-content");

    const chartsContainer =
        document.getElementById("eda-charts-container");

    const insightsContainer =
        document.getElementById("eda-insights-container");

    contentContainer.innerHTML = `
        <div class="eda-overview-grid">
            <div class="eda-overview-card">
                <h2>${eda.rows}</h2>
                <p>Total Rows</p>
            </div>

            <div class="eda-overview-card">
                <h2>${eda.columns}</h2>
                <p>Total Columns</p>
            </div>

            <div class="eda-overview-card">
                <h2>${eda.missing_values}</h2>
                <p>Missing Values</p>
            </div>

            <div class="eda-overview-card">
                <h2>${eda.duplicate_rows}</h2>
                <p>Duplicate Rows</p>
            </div>
        </div>
    `;

    chartsContainer.innerHTML = "";
    insightsContainer.innerHTML = "";

    const chartGrid = document.createElement("div");
    chartGrid.className = "eda-chart-grid";
    chartsContainer.appendChild(chartGrid);

    Object.entries(eda.numeric_summary || {})
        .forEach(([column, stats]) => {
            createNumericChart(chartGrid, column, stats);
        });

    Object.entries(eda.categorical_summary || {})
        .forEach(([column, values]) => {
            createCategoricalChart(chartGrid, column, values);
        });

    createMissingValuesChart(
        chartGrid,
        eda.missing_by_column || {}
    );

    renderCorrelationTable(
        chartsContainer,
        eda.correlations || {}
    );

    generateInsights(eda, insightsContainer);
}

function createNumericChart(container, column, stats) {
    const card = document.createElement("div");
    card.className = "eda-chart-card";

    const canvas = document.createElement("canvas");

    card.innerHTML = `
        <h3>${escapeHtml(column)} Statistics</h3>
        <div class="chart-container"></div>
    `;

    card.querySelector(".chart-container")
        .appendChild(canvas);

    container.appendChild(card);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: ["Min", "Mean", "Median", "Max"],
            datasets: [{
                label: column,
                data: [
                    stats.min ?? 0,
                    stats.mean ?? 0,
                    stats.median ?? 0,
                    stats.max ?? 0
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    activeCharts.push(chart);
}

function createCategoricalChart(container, column, values) {
    const card = document.createElement("div");
    card.className = "eda-chart-card";

    const canvas = document.createElement("canvas");

    card.innerHTML = `
        <h3>${escapeHtml(column)} Distribution</h3>
        <div class="chart-container"></div>
    `;

    card.querySelector(".chart-container")
        .appendChild(canvas);

    container.appendChild(card);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: Object.keys(values),
            datasets: [{
                label: "Count",
                data: Object.values(values)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    activeCharts.push(chart);
}

function createMissingValuesChart(container, missingData) {
    const entries = Object.entries(missingData)
        .filter(([, value]) => value > 0);

    if (entries.length === 0) return;

    const card = document.createElement("div");
    card.className = "eda-chart-card";

    const canvas = document.createElement("canvas");

    card.innerHTML = `
        <h3>Missing Values</h3>
        <div class="chart-container"></div>
    `;

    card.querySelector(".chart-container")
        .appendChild(canvas);

    container.appendChild(card);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: entries.map(entry => entry[0]),
            datasets: [{
                label: "Missing Values",
                data: entries.map(entry => entry[1])
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    activeCharts.push(chart);
}

function renderCorrelationTable(container, correlations) {
    const columns = Object.keys(correlations);

    if (columns.length === 0) return;

    const card = document.createElement("div");
    card.className = "result-card";

    let html = `
        <h2>Correlation Matrix</h2>
        <div class="correlation-table-wrapper">
            <table class="correlation-table">
                <thead>
                    <tr>
                        <th>Column</th>
    `;

    columns.forEach(column => {
        html += `<th>${escapeHtml(column)}</th>`;
    });

    html += `</tr></thead><tbody>`;

    columns.forEach(rowColumn => {
        html += `<tr><th>${escapeHtml(rowColumn)}</th>`;

        columns.forEach(column => {
            const value =
                correlations[rowColumn]?.[column];

            html += `<td>${
                value === null || value === undefined
                    ? "-"
                    : Number(value).toFixed(2)
            }</td>`;
        });

        html += "</tr>";
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    card.innerHTML = html;
    container.appendChild(card);
}

function generateInsights(eda, container) {
    const insights = [];

    Object.entries(eda.missing_by_column || {})
        .forEach(([column, value]) => {
            if (value > 0) {
                insights.push(
                    `${column} contains ${value} missing values.`
                );
            }
        });

    if (eda.duplicate_rows > 0) {
        insights.push(
            `The dataset contains ${eda.duplicate_rows} duplicate rows.`
        );
    }

    const numericCount = Object.keys(
        eda.numeric_summary || {}
    ).length;

    const categoricalCount = Object.keys(
        eda.categorical_summary || {}
    ).length;

    if (numericCount > 0) {
        insights.push(
            `The dataset contains ${numericCount} numeric columns suitable for statistical analysis.`
        );
    }

    if (categoricalCount > 0) {
        insights.push(
            `The dataset contains ${categoricalCount} categorical columns that may reveal useful patterns.`
        );
    }

    if (insights.length === 0) {
        insights.push(
            "No major data quality issues were automatically detected."
        );
    }

    container.innerHTML = `
        <div class="insight-card">
            <h2>Smart Insights</h2>
            <ul class="insight-list">
                ${insights.map(insight =>
                    `<li>${escapeHtml(insight)}</li>`
                ).join("")}
            </ul>
        </div>
    `;
}

async function loadDatasets() {
    const container = document.getElementById(
        "datasets-container"
    );

    const activeInfo = document.getElementById(
        "active-dataset-info"
    );

    try {
        const response = await fetch(
            `${API_URL}/datasets/`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to load datasets."
            );
        }

        const datasets = data.datasets || [];
        const activeDatasetId = data.active_dataset;

        if (datasets.length === 0) {
            activeInfo.textContent =
                "No active dataset selected.";

            container.innerHTML = `
                <div class="empty-state">
                    Upload a dataset to start.
                </div>
            `;

            return;
        }

        const activeDataset = datasets.find(
            dataset =>
                dataset.dataset_id === activeDatasetId
        );

        if (activeDataset) {
            datasetId = activeDataset.dataset_id;

            activeInfo.innerHTML = `
                <strong>Active Dataset:</strong>
                ${escapeHtml(activeDataset.filename)}
                <span class="active-badge">ACTIVE</span>
            `;

            updateActiveDatasetUI(
                activeDataset.filename
            );
        }

        container.innerHTML = "";

        datasets.forEach(dataset => {
            const card = document.createElement("div");
            card.className = "dataset-card";

            const isActive =
                dataset.dataset_id === activeDatasetId;

            if (isActive) {
                card.classList.add("active");
            }

            const parentInfo = dataset.parent_dataset
                ? `
                    <p class="dataset-meta">
                        <strong>Parent Dataset:</strong>
                        ${escapeHtml(dataset.parent_dataset)}
                    </p>
                `
                : `
                    <p class="dataset-meta">
                        Original uploaded dataset.
                    </p>
                `;

            card.innerHTML = `
                <h3>${escapeHtml(dataset.filename)}</h3>

                <span class="dataset-type ${
                    escapeHtml(dataset.dataset_type || "original")
                }">
                    ${escapeHtml(
                        (dataset.dataset_type || "original")
                        .toUpperCase()
                    )}
                </span>

                <p class="dataset-meta">
                    <strong>Dataset ID:</strong>
                    ${escapeHtml(dataset.dataset_id)}
                </p>

                ${parentInfo}

                ${
                    isActive
                        ? `
                            <button class="primary-btn switch-dataset-btn"
                                disabled>
                                Currently Active
                            </button>
                        `
                        : `
                            <button class="primary-btn switch-dataset-btn"
                                data-dataset-id="${escapeHtml(dataset.dataset_id)}">
                                Use This Dataset
                            </button>
                        `
                }
            `;

            container.appendChild(card);
        });

        document.querySelectorAll(".switch-dataset-btn")
            .forEach(button => {
                if (button.disabled) return;

                button.addEventListener("click", () => {
                    switchDataset(button.dataset.datasetId);
                });
            });

    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                Failed to load datasets.<br>
                ${escapeHtml(error.message)}
            </div>
        `;
    }
}

async function switchDataset(selectedDatasetId) {
    try {
        const response = await fetch(
            `${API_URL}/datasets/active/${selectedDatasetId}`,
            { method: "PUT" }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Failed to switch dataset."
            );
        }

        datasetId = selectedDatasetId;

        updateActiveDatasetUI(
            data.active_dataset.filename
        );

        await loadDatasets();

        alert("Active dataset changed successfully!");

    } catch (error) {
        alert(
            "Dataset Switch Error: " + error.message
        );
    }
}

document.getElementById(
    "refresh-datasets-btn"
).addEventListener("click", loadDatasets);

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value;
    return div.innerHTML;
}

document.addEventListener(
    "DOMContentLoaded",
    loadDatasets
);

/* =====================================================
   DATA PILOT AI ASSISTANT
===================================================== */

const aiChatMessages = document.getElementById(
    "ai-chat-messages"
);

const aiQuestionInput = document.getElementById(
    "ai-question-input"
);

const aiSendButton = document.getElementById(
    "ai-send-btn"
);

const aiDatasetStatus = document.getElementById(
    "ai-dataset-status"
);


let aiConversationHistory = [];
let aiIsSending = false;


/* =====================================================
   UPDATE AI DATASET STATUS
===================================================== */

function updateAIDatasetStatus(filename) {

    if (!aiDatasetStatus) {
        return;
    }

    if (!datasetId) {

        aiDatasetStatus.textContent =
            "Select or upload a dataset to start analyzing.";

        return;
    }

    aiDatasetStatus.textContent =
        `Analyzing active dataset: ${filename}`;

}


/* =====================================================
   ADD CHAT MESSAGE
===================================================== */

function addAIMessage(text, role) {

    const message = document.createElement("div");

    message.className =
        `ai-message ${role}-message`;


    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent =
        role === "user"
            ? "YOU"
            : "AI";


    const bubble = document.createElement("div");

    bubble.className = "message-bubble";

    bubble.textContent = text;


    message.appendChild(avatar);

    message.appendChild(bubble);


    aiChatMessages.appendChild(message);


    scrollAIChatToBottom();
}


/* =====================================================
   SHOW TYPING INDICATOR
===================================================== */

function showAITypingIndicator() {

    const message = document.createElement("div");

    message.className =
        "ai-message assistant-message";

    message.id = "ai-typing-message";


    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    avatar.textContent = "AI";


    const bubble = document.createElement("div");

    bubble.className = "message-bubble";


    bubble.innerHTML = `
        <div class="typing-indicator">

            <span class="typing-dot"></span>

            <span class="typing-dot"></span>

            <span class="typing-dot"></span>

        </div>
    `;


    message.appendChild(avatar);

    message.appendChild(bubble);


    aiChatMessages.appendChild(message);


    scrollAIChatToBottom();
}


/* =====================================================
   REMOVE TYPING INDICATOR
===================================================== */

function removeAITypingIndicator() {

    const typingMessage = document.getElementById(
        "ai-typing-message"
    );

    if (typingMessage) {
        typingMessage.remove();
    }

}


/* =====================================================
   SCROLL CHAT
===================================================== */

function scrollAIChatToBottom() {

    if (!aiChatMessages) {
        return;
    }

    aiChatMessages.scrollTop =
        aiChatMessages.scrollHeight;

}


/* =====================================================
   SEND AI QUESTION
===================================================== */

async function sendAIQuestion(predefinedQuestion = null) {

    if (aiIsSending) {
        return;
    }


    if (!datasetId) {

        addAIMessage(
            "Please upload or select a dataset before asking me questions.",
            "assistant"
        );

        return;
    }


    const question =
        predefinedQuestion
            ? predefinedQuestion.trim()
            : aiQuestionInput.value.trim();


    if (!question) {
        return;
    }


    if (question.length > 5000) {

        addAIMessage(
            "Please keep your question under 5000 characters.",
            "assistant"
        );

        return;
    }


    addAIMessage(
        question,
        "user"
    );


    aiConversationHistory.push({
        role: "user",
        content: question
    });


    if (!predefinedQuestion) {

        aiQuestionInput.value = "";

        autoResizeAIInput();

    }


    aiIsSending = true;

    aiSendButton.disabled = true;

    aiQuestionInput.disabled = true;


    showAITypingIndicator();


    try {

        const response = await fetch(

            `${API_URL}/ai/chat/${datasetId}`,

            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })

            }

        );


        const responseText =
            await response.text();


        let data = {};


        try {

            if (responseText) {

                data =
                    JSON.parse(responseText);

            }

        } catch (parseError) {

            console.error(
                "AI API returned invalid JSON:",
                responseText
            );

            throw new Error(
                "The AI server returned an invalid response."
            );

        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "AI analysis failed."
            );

        }


        const answer =
            data.answer ||
            "I could not generate an answer for this question.";


        removeAITypingIndicator();


        addAIMessage(
            answer,
            "assistant"
        );


        aiConversationHistory.push({
            role: "assistant",
            content: answer
        });


        if (aiConversationHistory.length > 20) {

            aiConversationHistory =
                aiConversationHistory.slice(-20);

        }


    } catch (error) {

        removeAITypingIndicator();


        console.error(
            "AI Assistant Error:",
            error
        );


        addAIMessage(

            `AI Error: ${error.message}`,

            "assistant"

        );


    } finally {

        aiIsSending = false;

        aiSendButton.disabled = false;

        aiQuestionInput.disabled = false;

        aiQuestionInput.focus();

    }

}


/* =====================================================
   SEND BUTTON
===================================================== */

aiSendButton.addEventListener(

    "click",

    () => {

        sendAIQuestion();

    }

);


/* =====================================================
   ENTER TO SEND
===================================================== */

aiQuestionInput.addEventListener(

    "keydown",

    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendAIQuestion();

        }

    }

);


/* =====================================================
   AUTO RESIZE TEXTAREA
===================================================== */

aiQuestionInput.addEventListener(

    "input",

    autoResizeAIInput

);


function autoResizeAIInput() {

    aiQuestionInput.style.height =
        "auto";


    aiQuestionInput.style.height =
        Math.min(
            aiQuestionInput.scrollHeight,
            150
        ) + "px";

}


/* =====================================================
   QUICK QUESTION BUTTONS
===================================================== */

document
    .querySelectorAll(".ai-suggestion-btn")
    .forEach(button => {

        button.addEventListener(

            "click",

            () => {

                const question =
                    button.dataset.question;

                sendAIQuestion(
                    question
                );

            }

        );

    });


/* =====================================================
   DATAPILOT AI - THEME SYSTEM
===================================================== */

const themeToggle =
    document.getElementById("theme-toggle");

const themeIcon =
    document.getElementById("theme-icon");


function setTheme(theme) {

    if (theme === "dark") {

        document.body.classList.add(
            "dark-theme"
        );

        themeIcon.textContent = "☀";

    } else {

        document.body.classList.remove(
            "dark-theme"
        );

        themeIcon.textContent = "☾";

    }

    localStorage.setItem(
        "datapilot-theme",
        theme
    );

}


/* Load saved theme */

const savedTheme =
    localStorage.getItem(
        "datapilot-theme"
    );


if (savedTheme) {

    setTheme(
        savedTheme
    );

} else {

    /* Optional system preference */

    const prefersDark =
        window.matchMedia(
            "(prefers-color-scheme: dark)"
        ).matches;


    setTheme(
        prefersDark
            ? "dark"
            : "light"
    );

}


/* Toggle theme */

themeToggle.addEventListener(
    "click",
    () => {

        const isDark =
            document.body.classList.contains(
                "dark-theme"
            );


        setTheme(
            isDark
                ? "light"
                : "dark"
        );

    }
);

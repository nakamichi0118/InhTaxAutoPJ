// 相続税申告書類処理システム - Frontend JavaScript

const API_BASE_URL = typeof config !== 'undefined' ? config.API_BASE_URL : 'http://localhost:8000/api';

let selectedFiles = [];
let processedDocuments = [];

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const fileListContent = document.getElementById('fileListContent');
const processButton = document.getElementById('processButton');
const resultsSection = document.getElementById('resultsSection');
const resultTableBody = document.getElementById('resultTableBody');
const loadingIndicator = document.getElementById('loadingIndicator');
const exportCsvButton = document.getElementById('exportCsvButton');
const exportPdfButton = document.getElementById('exportPdfButton');

// Category counters
const landCount = document.getElementById('landCount');
const depositCount = document.getElementById('depositCount');
const stockCount = document.getElementById('stockCount');

// File Upload Handlers
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    selectedFiles = Array.from(files);
    displayFileList();
    processButton.disabled = selectedFiles.length === 0;
}

function displayFileList() {
    if (selectedFiles.length === 0) {
        fileList.classList.add('hidden');
        return;
    }

    fileList.classList.remove('hidden');
    fileListContent.innerHTML = selectedFiles.map((file, index) => `
        <div class="flex justify-between items-center py-2 border-b last:border-0">
            <span class="text-sm text-gray-700">${file.name}</span>
            <button onclick="removeFile(${index})" class="text-sm text-red-600 hover:text-red-700">
                削除
            </button>
        </div>
    `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFileList();
    processButton.disabled = selectedFiles.length === 0;
}

// Process Button Handler
processButton.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    loadingIndicator.classList.remove('hidden');
    processButton.disabled = true;

    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        formData.append('auto_classify', 'true');

        const response = await fetch(`${API_BASE_URL}/ocr/process-batch`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        processedDocuments = result.documents || [];
        
        displayResults();
        showNotification('処理が完了しました', 'success');

    } catch (error) {
        console.error('Processing error:', error);
        showNotification('処理中にエラーが発生しました', 'error');
    } finally {
        loadingIndicator.classList.add('hidden');
        processButton.disabled = false;
    }
});

// Display Results
function displayResults() {
    resultsSection.classList.remove('hidden');
    
    // Count categories
    const counts = {
        L: 0,  // Land/Building
        D: 0,  // Deposit
        S: 0   // Stock
    };

    processedDocuments.forEach(doc => {
        if (doc.category === 'L' || doc.category === 'LAND_BUILDING') counts.L++;
        if (doc.category === 'D' || doc.category === 'DEPOSIT') counts.D++;
        if (doc.category === 'S' || doc.category === 'LISTED_STOCK') counts.S++;
    });

    landCount.textContent = counts.L;
    depositCount.textContent = counts.D;
    stockCount.textContent = counts.S;

    // Display table
    resultTableBody.innerHTML = processedDocuments.map(doc => {
        const categoryName = getCategoryName(doc.category);
        const dataPreview = getDataPreview(doc.extracted_data);
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${categoryName}
                    </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">${doc.original_filename}</td>
                <td class="px-6 py-4 text-sm text-gray-600">
                    <div class="max-w-xs overflow-hidden text-ellipsis">
                        ${dataPreview}
                    </div>
                </td>
                <td class="px-6 py-4 text-sm">
                    <button onclick="editDocument('${doc.id}')" class="text-blue-600 hover:text-blue-700 mr-3">
                        編集
                    </button>
                    <button onclick="viewDocument('${doc.id}')" class="text-gray-600 hover:text-gray-700">
                        詳細
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function getCategoryName(category) {
    const names = {
        'L': '土地・建物',
        'LAND_BUILDING': '土地・建物',
        'S': '株式',
        'LISTED_STOCK': '株式',
        'D': '預貯金',
        'DEPOSIT': '預貯金',
        'T': '通帳',
        'PASSBOOK': '通帳',
        'I': '保険',
        'LIFE_INSURANCE': '保険',
        'C': '債務',
        'DEBT': '債務',
        'F': '葬式費用',
        'FUNERAL_EXPENSE': '葬式費用',
        'O': 'その他',
        'OTHER_PROPERTY': 'その他',
        'P': '手続き',
        'PROCEDURE_DOC': '手続き',
        'U': '不明',
        'UNKNOWN': '不明'
    };
    return names[category] || category;
}

function getDataPreview(data) {
    if (typeof data === 'string') {
        return data.substring(0, 50) + '...';
    }
    if (Array.isArray(data) && data.length > 0) {
        return `${data.length}件のデータ`;
    }
    if (typeof data === 'object' && data !== null) {
        const keys = Object.keys(data).slice(0, 3).join(', ');
        return keys + '...';
    }
    return 'データなし';
}

// Export Functions
exportCsvButton.addEventListener('click', async () => {
    if (processedDocuments.length === 0) {
        showNotification('エクスポートするデータがありません', 'warning');
        return;
    }

    try {
        const documentIds = processedDocuments.map(doc => doc.id);
        
        const response = await fetch(`${API_BASE_URL}/documents/export/csv`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_ids: documentIds,
                output_format: 'csv'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `inheritance_data_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showNotification('CSVファイルをダウンロードしました', 'success');

    } catch (error) {
        console.error('Export error:', error);
        showNotification('CSVエクスポート中にエラーが発生しました', 'error');
    }
});

// Document Edit/View Functions
function editDocument(docId) {
    const doc = processedDocuments.find(d => d.id === docId);
    if (!doc) return;

    // TODO: Implement edit modal
    console.log('Edit document:', doc);
    showNotification('編集機能は実装中です', 'info');
}

function viewDocument(docId) {
    const doc = processedDocuments.find(d => d.id === docId);
    if (!doc) return;

    // TODO: Implement view modal
    console.log('View document:', doc);
    alert(JSON.stringify(doc.extracted_data, null, 2));
}

// Notification Function
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg z-50 animate-pulse`;
    
    switch(type) {
        case 'success':
            notification.classList.add('bg-green-500', 'text-white');
            break;
        case 'error':
            notification.classList.add('bg-red-500', 'text-white');
            break;
        case 'warning':
            notification.classList.add('bg-yellow-500', 'text-white');
            break;
        default:
            notification.classList.add('bg-blue-500', 'text-white');
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('相続税申告書類処理システム - Frontend Ready');
    
    // Check API health
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .then(data => {
            console.log('API Health:', data);
        })
        .catch(error => {
            console.error('API connection failed:', error);
            showNotification('サーバーに接続できません', 'error');
        });
});
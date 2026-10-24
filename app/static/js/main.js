// Main JavaScript for AI Content Creator Marketplace (Synapse v2)

// ==========================================
// 1. Error Formatting Helper
// ==========================================
function formatErrorMessage(detail) {
    if (!detail) return 'An error occurred. Please try again.';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail.map(d => {
            if (typeof d === 'string') return d;
            if (d && typeof d === 'object') {
                if (d.msg) {
                    const field = Array.isArray(d.loc) ? d.loc.filter(x => x !== 'body').join(' ') : '';
                    return field ? `${field}: ${d.msg}` : d.msg;
                }
                return JSON.stringify(d);
            }
            return String(d);
        }).join('; ');
    }
    if (typeof detail === 'object') {
        if (detail.msg) return detail.msg;
        if (detail.message) return detail.message;
        if (detail.detail) return formatErrorMessage(detail.detail);
        return JSON.stringify(detail);
    }
    return String(detail);
}

// ==========================================
// 2. Auth Headers Helper
// ==========================================
function getAuthHeaders(extraHeaders = {}) {
    const headers = { ...extraHeaders };
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// ==========================================
// 3. Global Toast Notifications
// ==========================================
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;

    const formattedMessage = formatErrorMessage(message);
    const bgClass = type === 'success' ? 'text-bg-success' : (type === 'danger' ? 'text-bg-danger' : 'text-bg-primary');
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center ${bgClass} border-0 show mb-2 shadow`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fw-medium">${formattedMessage}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    setTimeout(() => {
        toastEl.remove();
    }, 5000);
}

// ==========================================
// 4. Currency Switcher (Primary INR ₹, Optional USD $)
// ==========================================
const USD_INR_RATE = 85.0;

function getActiveCurrency() {
    return localStorage.getItem('marketplace_currency') || 'INR';
}

function setGlobalCurrency(currency) {
    localStorage.setItem('marketplace_currency', currency);
    updateCurrencyDisplay();
}

function formatMoney(amountINR) {
    const currency = getActiveCurrency();
    const val = parseFloat(amountINR) || 0;
    if (currency === 'USD') {
        const usd = Math.round(val / USD_INR_RATE);
        return `$${usd.toLocaleString('en-US')}`;
    }
    return `₹${val.toLocaleString('en-IN')}`;
}

function updateCurrencyDisplay() {
    const currency = getActiveCurrency();
    document.querySelectorAll('[data-inr]').forEach(el => {
        const inr = parseFloat(el.getAttribute('data-inr')) || 0;
        const prefix = el.getAttribute('data-prefix') || '';
        const suffix = el.getAttribute('data-suffix') || '';
        el.textContent = `${prefix}${formatMoney(inr)}${suffix}`;
    });

    const inrBtn = document.getElementById('btnCurrencyINR');
    const usdBtn = document.getElementById('btnCurrencyUSD');
    if (inrBtn && usdBtn) {
        if (currency === 'USD') {
            usdBtn.classList.add('active', 'active-currency');
            usdBtn.classList.remove('btn-outline-light', 'btn-light');
            inrBtn.classList.remove('active', 'active-currency', 'btn-light');
            inrBtn.classList.remove('btn-outline-light');
        } else {
            inrBtn.classList.add('active', 'active-currency');
            inrBtn.classList.remove('btn-outline-light', 'btn-light');
            usdBtn.classList.remove('active', 'active-currency', 'btn-light');
            usdBtn.classList.remove('btn-outline-light');
        }
    }
}

// Initialize currency formatting on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    updateCurrencyDisplay();
});

// ==========================================
// 5. Pin / Unpin Best Work (Max 3)
// ==========================================
async function togglePinWork(itemId, shouldPin) {
    try {
        const res = await fetch(`/api/creators/portfolio/${itemId}/pin`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ is_pinned: shouldPin })
        });
        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Could not update pin status', 'danger');
            return;
        }
        showToast(shouldPin ? 'Pinned work to top of profile!' : 'Unpinned work.', 'success');
        setTimeout(() => window.location.reload(), 800);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ==========================================
// 6. Creator Connections (Mutual Networking)
// ==========================================
async function sendConnectionRequest(targetCreatorId) {
    try {
        const res = await fetch(`/api/creators/${targetCreatorId}/connect`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' })
        });
        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Could not send connection request', 'danger');
            return;
        }
        showToast('Connection request sent!', 'success');
        setTimeout(() => window.location.reload(), 1000);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function respondToConnection(connectionId, action) {
    try {
        const res = await fetch(`/api/connections/${connectionId}/status`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({ action: action })
        });
        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Could not update connection', 'danger');
            return;
        }
        showToast(`Connection request ${action}ed!`, 'success');
        setTimeout(() => window.location.reload(), 800);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ==========================================
// 7. Company Review Submission
// ==========================================
async function submitCompanyReview(creatorId, event) {
    if (event) event.preventDefault();
    const ratingInput = document.getElementById('reviewRatingInput');
    const titleInput = document.getElementById('reviewTitleInput');
    const commentInput = document.getElementById('reviewCommentInput');
    const toolsInput = document.getElementById('reviewToolsInput');
    const verifiedInput = document.getElementById('reviewVerifiedCheck');

    if (!ratingInput || !titleInput || !commentInput) return;

    const payload = {
        rating: parseInt(ratingInput.value) || 5,
        project_title: titleInput.value.trim(),
        comment: commentInput.value.trim(),
        tools_used: toolsInput ? toolsInput.value.trim() : null,
        is_verified_engagement: verifiedInput ? verifiedInput.checked : false
    };

    if (!payload.project_title || !payload.comment) {
        showToast('Please fill in both project title and review comments.', 'danger');
        return;
    }

    try {
        const res = await fetch(`/creators/${creatorId}/reviews`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) {
            showToast(data.detail || 'Failed to submit review.', 'danger');
            return;
        }
        showToast('Review submitted successfully!', 'success');
        const modalEl = document.getElementById('companyReviewModal');
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }
        setTimeout(() => window.location.reload(), 1000);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ==========================================
// 8. Media Preview Modal Handler
// ==========================================
function openMediaModal(title, filePath, contentType, description, format, aspectRatio, tools, skills) {
    const modalTitle = document.getElementById('mediaModalTitle');
    const modalBody = document.getElementById('mediaModalBody');
    const modalMeta = document.getElementById('mediaModalMeta');

    if (!modalTitle || !modalBody) return;

    modalTitle.textContent = title;

    let mediaHtml = '';
    const ext = filePath.split('.').pop().toLowerCase();

    if (['mp4', 'webm', 'mov'].includes(ext)) {
        mediaHtml = `<video controls autoplay class="w-100 rounded" style="max-height: 500px; background: #000;">
            <source src="${filePath}" type="video/${ext === 'mov' ? 'mp4' : ext}">
            Your browser does not support the video tag.
        </video>`;
    } else {
        mediaHtml = `<img src="${filePath}" alt="${title}" class="img-fluid rounded mx-auto d-block" style="max-height: 500px; object-fit: contain;">`;
    }

    modalBody.innerHTML = mediaHtml;

    if (modalMeta) {
        modalMeta.innerHTML = `
            <div class="mt-3 text-start">
                <p class="text-secondary small mb-2">${description || 'No description provided.'}</p>
                <div class="d-flex flex-wrap gap-2">
                    <span class="badge bg-primary">${contentType}</span>
                    ${aspectRatio ? `<span class="badge bg-secondary">${aspectRatio}</span>` : ''}
                    ${format ? `<span class="badge bg-light text-dark border">${format}</span>` : ''}
                </div>
                ${tools ? `<div class="mt-2"><strong class="small text-muted">Tools:</strong> <span class="small">${tools}</span></div>` : ''}
                ${skills ? `<div><strong class="small text-muted">Skills:</strong> <span class="small">${skills}</span></div>` : ''}
            </div>
        `;
    }

    const modal = new bootstrap.Modal(document.getElementById('mediaPreviewModal'));
    modal.show();
}

// ==========================================
// 9. Logout Handler
// ==========================================
async function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {}
    window.location.href = '/';
}

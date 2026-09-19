// API 基础配置
const API_BASE_URL = 'http://localhost:8080/api';

// 全局状态
let currentPage = 1;
let currentStatus = '';
let currentCandidateId = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeUpload();
    initializeFilters();
    initializePagination();
    initializeModals();

    // 加载初始数据
    loadStatistics();
    loadCandidates();
});

// ==================== 文件上传 ====================
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadResume(e.target.files[0]);
        }
    });

    // 拖拽上传
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragging');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragging');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragging');

        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf') {
                uploadResume(file);
            } else {
                showMessage('请上传 PDF 格式的文件', 'error');
            }
        }
    });
}

async function uploadResume(file) {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = '上传中...';

    const formData = new FormData();
    formData.append('file', file);

    try {
        // 模拟进度
        progressFill.style.width = '30%';

        const response = await fetch(`${API_BASE_URL}/candidates/upload`, {
            method: 'POST',
            body: formData
        });

        progressFill.style.width = '60%';
        progressText.textContent = 'AI 分析中...';

        const result = await response.json();

        progressFill.style.width = '100%';
        progressText.textContent = '完成！';

        if (result.code === 200) {
            showMessage('简历上传成功！', 'success');

            // 延迟后隐藏进度条并刷新列表
            setTimeout(() => {
                uploadProgress.style.display = 'none';
                progressFill.style.width = '0%';
                loadStatistics();
                loadCandidates();
            }, 1500);
        } else {
            throw new Error(result.message || '上传失败');
        }
    } catch (error) {
        console.error('上传错误:', error);
        progressFill.style.width = '0%';
        progressText.textContent = '上传失败';
        showMessage('上传失败: ' + error.message, 'error');

        setTimeout(() => {
            uploadProgress.style.display = 'none';
        }, 2000);
    }
}

// ==================== 统计数据 ====================
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/candidates/statistics`);
        const result = await response.json();

        if (result.code === 200) {
            const stats = result.data;
            document.getElementById('totalCount').textContent = stats.total || 0;
            document.getElementById('approvedCount').textContent = stats.approved || 0;
            document.getElementById('pendingCount').textContent = stats.pending || 0;
            document.getElementById('rejectedCount').textContent = stats.rejected || 0;
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// ==================== 候选人列表 ====================
function initializeFilters() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            currentStatus = tab.dataset.status;
            currentPage = 1;
            loadCandidates();
        });
    });
}

async function loadCandidates() {
    const candidatesList = document.getElementById('candidatesList');
    candidatesList.innerHTML = '<div class="empty-state"><p>加载中...</p></div>';

    try {
        let url = `${API_BASE_URL}/candidates/list?page=${currentPage}&size=10`;
        if (currentStatus) {
            url += `&status=${currentStatus}`;
        }

        const response = await fetch(url);
        const result = await response.json();

        if (result.code === 200) {
            let candidates = result.data.records || result.data;

            // 去重逻辑：姓名、邮箱、电话都相同的只保留最新的
            const uniqueCandidates = [];
            const seenKeys = new Set();

            candidates.forEach(candidate => {
                const key = `${candidate.name || ''}_${candidate.email || ''}_${candidate.phone || ''}`;
                if (!seenKeys.has(key)) {
                    seenKeys.add(key);
                    uniqueCandidates.push(candidate);
                }
            });

            if (uniqueCandidates.length === 0) {
                candidatesList.innerHTML = '<div class="empty-state"><p>暂无候选人数据</p></div>';
                return;
            }

            candidatesList.innerHTML = uniqueCandidates.map(candidate =>
                createCandidateCard(candidate)
            ).join('');

            // 绑定事件
            bindCandidateActions();
        }
    } catch (error) {
        console.error('加载候选人列表失败:', error);
        candidatesList.innerHTML = '<div class="empty-state"><p>加载失败，请稍后重试</p></div>';
    }
}

function createCandidateCard(candidate) {
    const statusMap = {
        'approved': { text: '已自动发送面试邀请', class: 'approved' },
        'pending': { text: '待审核', class: 'pending' },
        'rejected': { text: '已拒绝', class: 'rejected' }
    };

    const status = statusMap[candidate.status] || { text: candidate.status, class: 'pending' };

    // 评分样式
    let scoreClass = 'low';
    const score = candidate.evaluationScore || candidate.matchScore || 0;
    if (score >= 70) scoreClass = 'high';
    else if (score >= 30) scoreClass = 'medium';

    // 解析 parsedData
    let email = candidate.email || '';
    let phone = candidate.phone || '';
    if (candidate.parsedData) {
        const parsed = typeof candidate.parsedData === 'string'
            ? JSON.parse(candidate.parsedData)
            : candidate.parsedData;
        email = email || parsed.email || parsed.contact?.email || '';
        phone = phone || parsed.phone || parsed.contact?.phone || '';
    }

    return `
        <div class="candidate-card" data-id="${candidate.id}">
            <div class="candidate-header">
                <div class="candidate-info">
                    <h3>${candidate.name || '未知'}</h3>
                    <div class="candidate-meta">
                        ${email ? `<span>📧 ${email}</span>` : ''}
                        ${phone ? `<span>📱 ${phone}</span>` : ''}
                    </div>
                </div>
                <span class="status-badge ${status.class}">${status.text}</span>
            </div>

            <div class="candidate-details">
                ${candidate.evaluationScore ? `
                    <div class="detail-row">
                        <span class="detail-label">综合评分:</span>
                        <span class="detail-value">
                            <span class="score-display ${scoreClass}">${candidate.evaluationScore.toFixed(1)}</span>
                        </span>
                    </div>
                ` : ''}
                ${candidate.matchScore ? `
                    <div class="detail-row">
                        <span class="detail-label">匹配度:</span>
                        <span class="detail-value">
                            <span class="score-display ${scoreClass}">${candidate.matchScore.toFixed(1)}</span>
                        </span>
                    </div>
                ` : ''}
                ${candidate.createdAt ? `
                    <div class="detail-row">
                        <span class="detail-label">提交时间:</span>
                        <span class="detail-value">${formatDate(candidate.createdAt)}</span>
                    </div>
                ` : ''}
            </div>

            <div class="candidate-actions">
                <button class="btn btn-secondary btn-view-detail" data-id="${candidate.id}">
                    查看详情
                </button>
                ${candidate.status === 'pending' ? `
                    <button class="btn btn-primary btn-approve" data-id="${candidate.id}" data-decision="approved">
                        通过
                    </button>
                    <button class="btn btn-danger btn-approve" data-id="${candidate.id}" data-decision="rejected">
                        拒绝
                    </button>
                ` : ''}
                ${candidate.status === 'rejected' ? `
                    <button class="btn btn-rescue" data-id="${candidate.id}">
                        捞回
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

function bindCandidateActions() {
    // 查看详情
    document.querySelectorAll('.btn-view-detail').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            showCandidateDetail(id);
        });
    });

    // 通过按钮
    document.querySelectorAll('.btn-approve[data-decision="approved"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            approveCandidate(id, 'approved', '通过审核');
        });
    });

    // 拒绝按钮
    document.querySelectorAll('.btn-approve[data-decision="rejected"]').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            approveCandidate(id, 'rejected', '不符合要求');
        });
    });

    // 捞回按钮
    document.querySelectorAll('.btn-rescue').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            rescueCandidate(id);
        });
    });

    // 发送面试邀请按钮
    document.querySelectorAll('.btn-invite').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            showInviteModal(id);
        });
    });
}

// ==================== 分页 ====================
function initializePagination() {
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            updatePageInfo();
            loadCandidates();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        currentPage++;
        updatePageInfo();
        loadCandidates();
    });
}

function updatePageInfo() {
    document.getElementById('pageInfo').textContent = `第 ${currentPage} 页`;
    document.getElementById('prevPage').disabled = currentPage === 1;
}

// ==================== 候选人详情模态框 ====================
async function showCandidateDetail(id) {
    const modal = document.getElementById('detailModal');
    const detailContainer = document.getElementById('candidateDetail');

    detailContainer.innerHTML = '<p>加载中...</p>';
    modal.classList.add('show');

    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${id}`);
        const result = await response.json();

        if (result.code === 200) {
            const candidate = result.data;
            detailContainer.innerHTML = renderCandidateDetail(candidate);
        } else {
            detailContainer.innerHTML = '<p>加载失败</p>';
        }
    } catch (error) {
        console.error('加载候选人详情失败:', error);
        detailContainer.innerHTML = '<p>加载失败，请稍后重试</p>';
    }
}

function renderCandidateDetail(candidate) {
    let html = `
        <div class="detail-section">
            <h3>基本信息</h3>
            <div class="detail-item"><strong>姓名:</strong> <span>${candidate.name || '-'}</span></div>
            <div class="detail-item"><strong>状态:</strong> <span>${candidate.status || '-'}</span></div>
            <div class="detail-item"><strong>提交时间:</strong> <span>${formatDate(candidate.createdAt)}</span></div>
        </div>
    `;

    // 解析简历数据
    if (candidate.parsedData) {
        const parsed = typeof candidate.parsedData === 'string'
            ? JSON.parse(candidate.parsedData)
            : candidate.parsedData;

        html += `
            <div class="detail-section">
                <h3>简历信息</h3>
                ${parsed.contact ? `
                    <div class="detail-item"><strong>邮箱:</strong> <span>${parsed.contact.email || '-'}</span></div>
                    <div class="detail-item"><strong>电话:</strong> <span>${parsed.contact.phone || '-'}</span></div>
                ` : ''}
                ${parsed.education ? `
                    <div class="detail-item"><strong>学历:</strong> <span>${JSON.stringify(parsed.education)}</span></div>
                ` : ''}
                ${parsed.work_experience ? `
                    <div class="detail-item"><strong>工作经验:</strong> <span>${JSON.stringify(parsed.work_experience)}</span></div>
                ` : ''}
                ${parsed.skills ? `
                    <div class="detail-item"><strong>技能:</strong> <span>${Array.isArray(parsed.skills) ? parsed.skills.join(', ') : JSON.stringify(parsed.skills)}</span></div>
                ` : ''}
            </div>
        `;
    }

    // 评估结果
    if (candidate.evaluationScore || candidate.matchScore) {
        html += `
            <div class="detail-section">
                <h3>评估结果</h3>
                ${candidate.evaluationScore ? `
                    <div class="detail-item"><strong>综合评分:</strong> <span>${candidate.evaluationScore.toFixed(2)}</span></div>
                ` : ''}
                ${candidate.matchScore ? `
                    <div class="detail-item"><strong>匹配度:</strong> <span>${candidate.matchScore.toFixed(2)}</span></div>
                ` : ''}
            </div>
        `;
    }

    // 评估详情
    if (candidate.evaluationResult) {
        const evalResult = typeof candidate.evaluationResult === 'string'
            ? JSON.parse(candidate.evaluationResult)
            : candidate.evaluationResult;

        html += `
            <div class="detail-section">
                <h3>详细评估</h3>
                <div class="detail-item"><strong>技术深度:</strong> <span>${evalResult.tech_depth_score || '-'}</span></div>
                <div class="detail-item"><strong>学习能力:</strong> <span>${evalResult.learning_ability_score || '-'}</span></div>
                ${evalResult.strengths ? `
                    <div class="detail-item"><strong>优势:</strong> <span>${evalResult.strengths}</span></div>
                ` : ''}
                ${evalResult.concerns ? `
                    <div class="detail-item"><strong>关注点:</strong> <span>${evalResult.concerns}</span></div>
                ` : ''}
                ${evalResult.recommendation ? `
                    <div class="detail-item"><strong>建议:</strong> <span>${evalResult.recommendation}</span></div>
                ` : ''}
            </div>
        `;
    }

    return html;
}

// ==================== 审批模态框 ====================
function initializeModals() {
    // 关闭按钮
    document.getElementById('closeModal').addEventListener('click', () => {
        document.getElementById('detailModal').classList.remove('show');
    });

    document.getElementById('closeApproveModal').addEventListener('click', () => {
        document.getElementById('approveModal').classList.remove('show');
    });

    document.getElementById('closeInviteModal').addEventListener('click', () => {
        document.getElementById('inviteModal').classList.remove('show');
    });

    // 取消按钮
    document.getElementById('cancelApprove').addEventListener('click', () => {
        document.getElementById('approveModal').classList.remove('show');
    });

    document.getElementById('cancelInvite').addEventListener('click', () => {
        document.getElementById('inviteModal').classList.remove('show');
    });

    // 确认按钮
    document.getElementById('confirmApprove').addEventListener('click', submitApproval);
    document.getElementById('confirmInvite').addEventListener('click', submitInvite);

    // 点击背景关闭
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
}

function showApproveModal(id) {
    currentCandidateId = id;
    document.getElementById('approveDecision').value = 'approved';
    document.getElementById('approveReason').value = '';
    document.getElementById('approveModal').classList.add('show');
}

async function submitApproval() {
    const decision = document.getElementById('approveDecision').value;
    const reason = document.getElementById('approveReason').value.trim();

    if (!reason) {
        showMessage('请输入审批理由', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${currentCandidateId}/approve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ decision, reason })
        });

        const result = await response.json();

        if (result.code === 200) {
            showMessage('审批成功', 'success');
            document.getElementById('approveModal').classList.remove('show');
            loadStatistics();
            loadCandidates();
        } else {
            throw new Error(result.message || '审批失败');
        }
    } catch (error) {
        console.error('审批失败:', error);
        showMessage('审批失败: ' + error.message, 'error');
    }
}

// ==================== 面试邀请模态框 ====================
function showInviteModal(id, name, email) {
    currentCandidateId = id;
    document.getElementById('inviteName').value = name;
    document.getElementById('inviteEmail').value = email;
    document.getElementById('inviteTime').value = '';
    document.getElementById('inviteLocation').value = '';
    document.getElementById('inviteModal').classList.add('show');
}

async function submitInvite() {
    const time = document.getElementById('inviteTime').value;
    const location = document.getElementById('inviteLocation').value.trim();

    if (!time || !location) {
        showMessage('请填写完整的面试信息', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${currentCandidateId}/invite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                interviewTime: time,
                location: location
            })
        });

        const result = await response.json();

        if (result.code === 200) {
            showMessage('面试邀请已发送', 'success');
            document.getElementById('inviteModal').classList.remove('show');
            loadCandidates();
        } else {
            throw new Error(result.message || '发送失败');
        }
    } catch (error) {
        console.error('发送邀请失败:', error);
        showMessage('发送失败: ' + error.message, 'error');
    }
}

// ==================== 捞回候选人 ====================
async function rescueCandidate(id) {
    const reason = prompt('请输入捞回理由:');

    if (!reason || !reason.trim()) {
        showMessage('请输入捞回理由', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${id}/rescue`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ reason: reason.trim() })
        });

        const result = await response.json();

        if (result.code === 200) {
            showMessage('候选人已捞回', 'success');
            loadStatistics();
            loadCandidates();
        } else {
            throw new Error(result.message || '捞回失败');
        }
    } catch (error) {
        console.error('捞回失败:', error);
        showMessage('捞回失败: ' + error.message, 'error');
    }
}

// ==================== 审批候选人 ====================
async function approveCandidate(id, decision, reason) {
    try {
        const response = await fetch(`${API_BASE_URL}/candidates/${id}/approve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ decision, reason })
        });

        const result = await response.json();

        if (result.code === 200) {
            showMessage(`${decision === 'approved' ? '通过' : '拒绝'}成功`, 'success');
            loadStatistics();
            loadCandidates();
        } else {
            throw new Error(result.message || '审批失败');
        }
    } catch (error) {
        console.error('审批失败:', error);
        showMessage('审批失败: ' + error.message, 'error');
    }
}

// ==================== 工具函数 ====================
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showMessage(message, type = 'info') {
    // 简单的提示实现
    const alertClass = type === 'error' ? 'danger' : type;
    alert(message);
}

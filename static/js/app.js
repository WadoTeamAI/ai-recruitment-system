// AI採用支援システム - メインJavaScript

// グローバル変数
let currentAnalysisResult = null;

// DOM読み込み完了時の初期化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeTooltips();
});

// イベントリスナーの初期化
function initializeEventListeners() {
    // メイン分析フォーム
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', handleAnalysis);
    }

    // ダウンロードボタン
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadResults);
    }

    // デモ分析ボタン
    const demoAnalyzeButtons = document.querySelectorAll('.demo-analyze-btn');
    demoAnalyzeButtons.forEach(btn => {
        btn.addEventListener('click', handleDemoAnalysis);
    });

    // デモダウンロードボタン
    const demoDownloadBtn = document.getElementById('demoDownloadBtn');
    if (demoDownloadBtn) {
        demoDownloadBtn.addEventListener('click', downloadResults);
    }
}

// ツールチップの初期化
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// メイン分析処理
async function handleAnalysis(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // バリデーション
    if (!validateForm(formData)) {
        return;
    }
    
    // UI更新
    showLoading();
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'サーバーエラーが発生しました');
        }
        
        // 結果表示
        currentAnalysisResult = result;
        displayResults(result);
        hideLoading();
        
    } catch (error) {
        hideLoading();
        showError('分析中にエラーが発生しました: ' + error.message);
    }
}

// デモ分析処理
async function handleDemoAnalysis(event) {
    const btn = event.target.closest('.demo-analyze-btn');
    const filename = btn.dataset.filename;
    const candidateName = btn.dataset.name;
    
    // UI更新
    showDemoLoading(candidateName);
    
    try {
        const response = await fetch(`/demo_analyze/${filename}`);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'デモ分析中にエラーが発生しました');
        }
        
        // 結果表示
        currentAnalysisResult = result;
        displayDemoResults(result);
        hideDemoLoading();
        
    } catch (error) {
        hideDemoLoading();
        showError('デモ分析中にエラーが発生しました: ' + error.message);
    }
}

// フォームバリデーション
function validateForm(formData) {
    const file = formData.get('resume_file');
    const jobPosition = formData.get('job_position');
    
    if (!file || file.size === 0) {
        showError('履歴書ファイルを選択してください');
        return false;
    }
    
    if (!jobPosition) {
        showError('職種を選択してください');
        return false;
    }
    
    // ファイルサイズチェック (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('ファイルサイズは16MB以下にしてください');
        return false;
    }
    
    return true;
}

// 分析結果表示
function displayResults(result) {
    // 候補者情報表示
    displayCandidateInfo(result.candidate, 'candidateInfo');
    
    // 評価結果表示
    displayEvaluation(result.evaluation, 'evaluationResults');
    
    // 面接質問表示
    displayInterviewQuestions(result.interview_questions, 'interviewQuestions');
    
    // 結果セクション表示
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// デモ結果表示
function displayDemoResults(result) {
    // 候補者情報表示
    displayCandidateInfo(result.candidate, 'demoCandidateInfo');
    
    // 評価結果表示
    displayEvaluation(result.evaluation, 'demoEvaluationResults');
    
    // 面接質問表示
    displayInterviewQuestions(result.interview_questions, 'demoInterviewQuestions');
    
    // 特記事項表示
    displaySpecialNotes(result.special_notes, 'demoSpecialNotes');
    
    // 結果セクション表示
    document.getElementById('demoResultsSection').style.display = 'block';
    document.getElementById('demoResultsSection').scrollIntoView({ behavior: 'smooth' });
}

// 候補者情報表示
function displayCandidateInfo(candidate, containerId) {
    const container = document.getElementById(containerId);
    
    const html = `
        <div class="col-md-6 mb-3">
            <div class="card border-0 bg-light h-100">
                <div class="card-body">
                    <h6 class="text-primary mb-2">
                        <i class="fas fa-user me-2"></i>基本情報
                    </h6>
                    <p class="mb-1"><strong>氏名:</strong> ${candidate.name}</p>
                    <p class="mb-1"><strong>メール:</strong> ${candidate.email}</p>
                    <p class="mb-0"><strong>経験年数:</strong> ${candidate.experience_years}年</p>
                </div>
            </div>
        </div>
        <div class="col-md-6 mb-3">
            <div class="card border-0 bg-light h-100">
                <div class="card-body">
                    <h6 class="text-primary mb-2">
                        <i class="fas fa-graduation-cap me-2"></i>学歴・資格
                    </h6>
                    <p class="mb-1"><strong>学歴:</strong> ${candidate.education.join(', ') || '未記載'}</p>
                    <p class="mb-0"><strong>資格:</strong> ${candidate.certifications.join(', ') || '未記載'}</p>
                </div>
            </div>
        </div>
        <div class="col-12 mb-3">
            <div class="card border-0 bg-light">
                <div class="card-body">
                    <h6 class="text-primary mb-2">
                        <i class="fas fa-code me-2"></i>主要スキル
                    </h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${candidate.skills.map(skill => `
                            <span class="badge bg-secondary">${skill}</span>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    container.classList.add('fade-in-up');
}

// 評価結果表示
function displayEvaluation(evaluation, containerId) {
    const container = document.getElementById(containerId);
    
    // スコアレベル判定
    const scoreLevel = getScoreLevel(evaluation.overall_score);
    const recommendationText = getRecommendationText(evaluation.recommendation);
    
    const html = `
        <div class="row align-items-center mb-4">
            <div class="col-md-3 text-center">
                <div class="score-circle ${scoreLevel.class}">
                    ${evaluation.overall_score}点
                </div>
                <div class="mt-2">
                    <span class="badge ${recommendationText.badgeClass} fs-6">
                        ${recommendationText.icon} ${recommendationText.text}
                    </span>
                </div>
            </div>
            <div class="col-md-9">
                <div class="row">
                    <div class="col-sm-6 mb-3">
                        <label class="form-label fw-semibold">スキルマッチ</label>
                        <div class="progress mb-1">
                            <div class="progress-bar bg-info" role="progressbar" 
                                 style="width: ${evaluation.skill_match_score}%"
                                 aria-valuenow="${evaluation.skill_match_score}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">${evaluation.skill_match_score}点</small>
                    </div>
                    <div class="col-sm-6 mb-3">
                        <label class="form-label fw-semibold">経験マッチ</label>
                        <div class="progress mb-1">
                            <div class="progress-bar bg-success" role="progressbar" 
                                 style="width: ${evaluation.experience_match_score}%"
                                 aria-valuenow="${evaluation.experience_match_score}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">${evaluation.experience_match_score}点</small>
                    </div>
                    <div class="col-sm-6 mb-3">
                        <label class="form-label fw-semibold">文化適合性</label>
                        <div class="progress mb-1">
                            <div class="progress-bar bg-warning" role="progressbar" 
                                 style="width: ${evaluation.culture_fit_score}%"
                                 aria-valuenow="${evaluation.culture_fit_score}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">${evaluation.culture_fit_score}点</small>
                    </div>
                    <div class="col-sm-6 mb-3">
                        <label class="form-label fw-semibold">学歴マッチ</label>
                        <div class="progress mb-1">
                            <div class="progress-bar bg-primary" role="progressbar" 
                                 style="width: ${evaluation.education_match_score}%"
                                 aria-valuenow="${evaluation.education_match_score}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">${evaluation.education_match_score}点</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info">
            <h6 class="alert-heading">
                <i class="fas fa-bullseye me-2"></i>面接重点分野
            </h6>
            <ul class="mb-0">
                ${evaluation.interview_focus_areas.map(area => `<li>${area}</li>`).join('')}
            </ul>
        </div>
    `;
    
    container.innerHTML = html;
    container.classList.add('fade-in-up');
}

// 面接質問表示
function displayInterviewQuestions(questions, containerId) {
    const container = document.getElementById(containerId);
    
    const html = questions.map((question, index) => `
        <div class="interview-question p-3 rounded mb-3 slide-in">
            <div class="question-category">${question.category}</div>
            <h6 class="fw-bold mb-2">質問 ${index + 1}</h6>
            <p class="mb-3">${question.question}</p>
            
            ${question.time_limit_minutes ? `
                <p class="text-muted mb-2">
                    <i class="fas fa-clock me-1"></i>
                    回答時間目安: ${question.time_limit_minutes}分
                </p>
            ` : ''}
            
            <div class="row">
                <div class="col-md-6">
                    <h7 class="text-primary fw-semibold d-block mb-1">
                        <i class="fas fa-bullseye me-1"></i>評価ポイント
                    </h7>
                    <ul class="small mb-2">
                        ${question.evaluation_points.map(point => `<li>${point}</li>`).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h7 class="text-success fw-semibold d-block mb-1">
                        <i class="fas fa-check-circle me-1"></i>良い回答例
                    </h7>
                    <p class="small text-muted">${question.good_answer_example}</p>
                </div>
            </div>
            
            ${question.follow_up_questions && question.follow_up_questions.length > 0 ? `
                <div class="mt-2">
                    <h7 class="text-info fw-semibold d-block mb-1">
                        <i class="fas fa-plus-circle me-1"></i>追加質問例
                    </h7>
                    <ul class="small mb-0">
                        ${question.follow_up_questions.map(fq => `<li>${fq}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// 特記事項表示
function displaySpecialNotes(notes, containerId) {
    const container = document.getElementById(containerId);
    
    if (!notes || notes.length === 0) {
        container.innerHTML = '<p class="text-muted">特記事項はありません。</p>';
        return;
    }
    
    const html = notes.map(note => {
        const isWarning = note.includes('⚠️');
        return `
            <div class="special-note ${isWarning ? 'warning-note' : ''}">
                ${note}
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// スコアレベル判定
function getScoreLevel(score) {
    if (score >= 80) return { class: 'score-excellent', level: 'excellent' };
    if (score >= 70) return { class: 'score-good', level: 'good' };
    if (score >= 60) return { class: 'score-average', level: 'average' };
    return { class: 'score-poor', level: 'poor' };
}

// 推薦判定テキスト
function getRecommendationText(recommendation) {
    switch (recommendation) {
        case 'pass':
            return { 
                text: '合格推薦', 
                icon: '<i class="fas fa-check-circle"></i>',
                badgeClass: 'bg-success'
            };
        case 'interview':
            return { 
                text: '要面接', 
                icon: '<i class="fas fa-question-circle"></i>',
                badgeClass: 'bg-warning text-dark'
            };
        case 'reject':
            return { 
                text: '不合格', 
                icon: '<i class="fas fa-times-circle"></i>',
                badgeClass: 'bg-danger'
            };
        default:
            return { 
                text: '判定中', 
                icon: '<i class="fas fa-clock"></i>',
                badgeClass: 'bg-secondary'
            };
    }
}

// ローディング表示
function showLoading() {
    document.getElementById('analysisForm').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('analysisForm').style.display = 'block';
}

function showDemoLoading(candidateName) {
    document.getElementById('loadingCandidateName').textContent = candidateName;
    document.getElementById('demoLoadingSection').style.display = 'block';
    
    // スクロール
    document.getElementById('demoLoadingSection').scrollIntoView({ behavior: 'smooth' });
}

function hideDemoLoading() {
    document.getElementById('demoLoadingSection').style.display = 'none';
}

// エラー表示
function showError(message) {
    // Bootstrap Alert でエラー表示
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // メインコンテナの最初に挿入
    const container = document.querySelector('main.container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // 3秒後に自動で削除
    setTimeout(() => {
        const alert = container.querySelector('.alert-danger');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// 結果ダウンロード
async function downloadResults() {
    if (!currentAnalysisResult) {
        showError('ダウンロードする結果がありません');
        return;
    }
    
    try {
        const response = await fetch('/download_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentAnalysisResult)
        });
        
        if (!response.ok) {
            throw new Error('ダウンロードに失敗しました');
        }
        
        // ファイルダウンロード
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evaluation_result_${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        showError('ダウンロード中にエラーが発生しました: ' + error.message);
    }
}

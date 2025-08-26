#!/usr/bin/env python3
"""
AI採用支援システム - Webアプリケーション
ブラウザから履歴書をアップロードして評価・面接質問生成
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
import zipfile
from io import BytesIO

# srcディレクトリを追加
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.hr_recruitment_system import (
        ResumeAnalyzer, CandidateMatcher, CompanyProfile, JobRequirement
    )
    from src.interview_system import InterviewQuestionGenerator, InterviewStage
except ImportError:
    # Vercel環境での代替インポート
    import importlib.util
    import os
    
    # hr_recruitment_system
    spec1 = importlib.util.spec_from_file_location(
        "hr_recruitment_system", 
        os.path.join(os.path.dirname(__file__), "src", "hr_recruitment_system.py")
    )
    hr_module = importlib.util.module_from_spec(spec1)
    spec1.loader.exec_module(hr_module)
    
    # interview_system
    spec2 = importlib.util.spec_from_file_location(
        "interview_system", 
        os.path.join(os.path.dirname(__file__), "src", "interview_system.py")
    )
    iv_module = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(iv_module)
    
    # クラスをインポート
    ResumeAnalyzer = hr_module.ResumeAnalyzer
    CandidateMatcher = hr_module.CandidateMatcher
    CompanyProfile = hr_module.CompanyProfile
    JobRequirement = hr_module.JobRequirement
    InterviewQuestionGenerator = iv_module.InterviewQuestionGenerator
    InterviewStage = iv_module.InterviewStage

app = Flask(__name__)
app.secret_key = 'hr_system_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# デバッグ用エラーハンドリング
@app.errorhandler(500)
def internal_error(error):
    import traceback
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error),
        'traceback': traceback.format_exc()
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    return jsonify({
        'error': 'Unhandled Exception',
        'message': str(e),
        'traceback': traceback.format_exc()
    }), 500

# アップロード設定
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

# グローバル設定
company_profile = CompanyProfile(
    company_name="株式会社テックイノベーション",
    mission="テクノロジーで社会課題を解決し、持続可能な未来を創造する",
    vision="2030年までに、AIとデータサイエンスで日本の生産性を世界トップレベルに押し上げる",
    values=["革新性", "協調性", "社会貢献", "継続学習", "多様性尊重"],
    culture_keywords=["フラット", "自由度高", "成長志向", "グローバル", "データ駆動"],
    work_style=["完全リモートワーク", "フレックスタイム", "副業OK", "海外勤務可能"]
)

# 求人要件
job_requirements = {
    "シニアWebエンジニア": JobRequirement(
        position_title="シニアWebエンジニア",
        department="プロダクト開発部",
        required_skills=["Python", "JavaScript", "React", "SQL"],
        preferred_skills=["Docker", "AWS", "機械学習", "チーム管理"],
        experience_level="senior",
        required_years=5,
        education_level="大学",
        salary_range=(800, 1200),
        employment_type="full-time",
        remote_work=True,
        travel_required=False
    ),
    "Webエンジニア": JobRequirement(
        position_title="Webエンジニア",
        department="プロダクト開発部", 
        required_skills=["Python", "JavaScript", "React", "SQL"],
        preferred_skills=["Docker", "AWS", "機械学習", "チーム管理"],
        experience_level="mid",
        required_years=3,
        education_level="大学",
        salary_range=(500, 800),
        employment_type="full-time",
        remote_work=True,
        travel_required=False
    ),
    "ジュニアWebエンジニア": JobRequirement(
        position_title="ジュニアWebエンジニア",
        department="プロダクト開発部",
        required_skills=["HTML", "CSS", "JavaScript"],
        preferred_skills=["React", "Node.js", "Git", "レスポンシブデザイン"],
        experience_level="junior",
        required_years=1,
        education_level="専門学校",
        salary_range=(300, 500),
        employment_type="full-time",
        remote_work=False,
        travel_required=False
    ),
    "営業マネージャー": JobRequirement(
        position_title="営業マネージャー",
        department="営業部",
        required_skills=["営業", "顧客管理", "チーム管理", "提案"],
        preferred_skills=["SaaS営業", "データ分析", "マーケティング", "英語"],
        experience_level="senior",
        required_years=5,
        education_level="大学",
        salary_range=(700, 1200),
        employment_type="full-time",
        remote_work=True,
        travel_required=True
    )
}

# 分析エンジン初期化
analyzer = ResumeAnalyzer()
matcher = CandidateMatcher(company_profile)
question_generator = InterviewQuestionGenerator()

def allowed_file(filename):
    """アップロード可能なファイル形式かチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    """ファイルからテキストを抽出"""
    try:
        # シンプルなテキストファイルとして読み込み
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # UTF-8で読み込めない場合はShift_JISで試行
        try:
            with open(filepath, 'r', encoding='shift_jis') as f:
                return f.read()
        except:
            return "ファイル読み込みエラー: テキストファイル(.txt)をアップロードしてください"
    except Exception as e:
        return f"ファイル読み込みエラー: {str(e)}"

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html', job_positions=list(job_requirements.keys()))

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """履歴書分析API"""
    try:
        # ファイル取得
        if 'resume_file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '対応していないファイル形式です。テキストファイル(.txt)をアップロードしてください'}), 400
        
        # 職種取得
        job_position = request.form.get('job_position')
        if job_position not in job_requirements:
            return jsonify({'error': '無効な職種が選択されています'}), 400
        
        # ファイル保存
        filename = secure_filename(file.filename)
        temp_path = UPLOAD_FOLDER / filename
        file.save(temp_path)
        
        # テキスト抽出
        resume_text = extract_text_from_file(temp_path)
        
        # 履歴書分析
        candidate = analyzer.extract_candidate_profile(resume_text)
        
        # マッチング評価
        job_req = job_requirements[job_position]
        matching_result = matcher.calculate_match_score(candidate, job_req)
        
        # 面接計画生成（1次面接）
        interview_plan = question_generator.generate_interview_plan(
            candidate, job_req, matching_result, InterviewStage.FIRST
        )
        
        # 結果作成
        result = {
            'candidate': {
                'name': candidate.name,
                'email': candidate.email,
                'experience_years': candidate.experience_years,
                'skills': candidate.skills[:10],  # 上位10スキルのみ
                'education': candidate.education,
                'certifications': candidate.certifications,
                'languages': candidate.languages
            },
            'evaluation': {
                'overall_score': round(matching_result.overall_score, 1),
                'skill_match_score': round(matching_result.skill_match_score, 1),
                'experience_match_score': round(matching_result.experience_match_score, 1),
                'culture_fit_score': round(matching_result.culture_fit_score, 1),
                'education_match_score': round(matching_result.education_match_score, 1),
                'recommendation': matching_result.recommendation,
                'interview_focus_areas': matching_result.interview_focus_areas,
                'detailed_analysis': matching_result.detailed_analysis
            },
            'interview_questions': [
                {
                    'category': q.category.value,
                    'question': q.question,
                    'evaluation_points': q.evaluation_points,
                    'time_limit_minutes': q.time_limit_minutes,
                    'follow_up_questions': q.follow_up_questions,
                    'good_answer_example': q.good_answer_example,
                    'red_flags': q.red_flags
                }
                for q in interview_plan.questions
            ],
            'special_notes': interview_plan.special_notes,
            'job_position': job_position,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # 一時ファイル削除
        temp_path.unlink()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500

@app.route('/interview/<stage>')
def generate_interview(stage):
    """面接質問生成（2次面接・最終面接）"""
    # TODO: より詳細な面接質問生成実装
    return jsonify({'message': f'{stage}面接質問生成機能は開発中です'})

@app.route('/download_result', methods=['POST'])
def download_result():
    """評価結果をダウンロード"""
    try:
        result_data = request.json
        
        # JSON形式で保存
        filename = f"evaluation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # メモリ上でファイル作成
        json_str = json.dumps(result_data, ensure_ascii=False, indent=2)
        json_bytes = json_str.encode('utf-8')
        
        return send_file(
            BytesIO(json_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({'error': f'ダウンロード中にエラーが発生しました: {str(e)}'}), 500

@app.route('/demo')
def demo():
    """デモページ"""
    demo_candidates = [
        {
            'name': 'シニアエンジニア（田中太郎）',
            'filename': 'resume_senior_engineer.txt',
            'recommended_job': 'シニアWebエンジニア',
            'description': 'AWS資格、15名チーム管理、6年経験'
        },
        {
            'name': '中堅エンジニア（佐藤花子）',
            'filename': 'sample_resume.txt',
            'recommended_job': 'Webエンジニア',
            'description': 'フルスタック開発、4年経験'
        },
        {
            'name': 'ジュニアエンジニア（鈴木花子）',
            'filename': 'resume_junior_engineer.txt',
            'recommended_job': 'ジュニアWebエンジニア',
            'description': 'Web制作、専門学校卒、1年経験'
        },
        {
            'name': '営業マネージャー（山田健一）',
            'filename': 'resume_sales_manager.txt',
            'recommended_job': '営業マネージャー',
            'description': 'SaaS営業、8名チーム管理、10年経験'
        }
    ]
    
    return render_template('demo.html', demo_candidates=demo_candidates)

@app.route('/demo_analyze/<filename>')
def demo_analyze(filename):
    """デモ用履歴書分析"""
    try:
        # デモファイルパス
        demo_file_path = Path('examples') / filename
        
        if not demo_file_path.exists():
            return jsonify({'error': 'デモファイルが見つかりません'}), 404
        
        # おすすめ職種の判定
        job_mapping = {
            'resume_senior_engineer.txt': 'シニアWebエンジニア',
            'sample_resume.txt': 'Webエンジニア',
            'resume_junior_engineer.txt': 'ジュニアWebエンジニア',
            'resume_sales_manager.txt': '営業マネージャー'
        }
        
        job_position = job_mapping.get(filename, 'Webエンジニア')
        
        # ファイル読み込み・分析
        resume_text = extract_text_from_file(demo_file_path)
        candidate = analyzer.extract_candidate_profile(resume_text)
        
        # マッチング評価
        job_req = job_requirements[job_position]
        matching_result = matcher.calculate_match_score(candidate, job_req)
        
        # 面接計画生成
        interview_plan = question_generator.generate_interview_plan(
            candidate, job_req, matching_result, InterviewStage.FIRST
        )
        
        # 結果作成
        result = {
            'candidate': {
                'name': candidate.name,
                'email': candidate.email,
                'experience_years': candidate.experience_years,
                'skills': candidate.skills[:10],
                'education': candidate.education,
                'certifications': candidate.certifications,
                'languages': candidate.languages
            },
            'evaluation': {
                'overall_score': round(matching_result.overall_score, 1),
                'skill_match_score': round(matching_result.skill_match_score, 1),
                'experience_match_score': round(matching_result.experience_match_score, 1),
                'culture_fit_score': round(matching_result.culture_fit_score, 1),
                'education_match_score': round(matching_result.education_match_score, 1),
                'recommendation': matching_result.recommendation,
                'interview_focus_areas': matching_result.interview_focus_areas,
                'detailed_analysis': matching_result.detailed_analysis
            },
            'interview_questions': [
                {
                    'category': q.category.value,
                    'question': q.question,
                    'evaluation_points': q.evaluation_points,
                    'time_limit_minutes': q.time_limit_minutes,
                    'follow_up_questions': q.follow_up_questions,
                    'good_answer_example': q.good_answer_example,
                    'red_flags': q.red_flags
                }
                for q in interview_plan.questions
            ],
            'special_notes': interview_plan.special_notes,
            'job_position': job_position,
            'analysis_timestamp': datetime.now().isoformat(),
            'demo_mode': True
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'デモ分析中にエラーが発生しました: {str(e)}'}), 500

@app.route('/health')
def health():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system': 'AI採用支援システム',
        'version': '1.0.0'
    })

# Vercel用のアプリケーションエクスポート
# この行は Vercel がアプリケーションを認識するために必要
app = app

if __name__ == '__main__':
    # 開発環境での起動（ポート8000を使用）
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)

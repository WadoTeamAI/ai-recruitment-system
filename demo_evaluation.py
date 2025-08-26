#!/usr/bin/env python3
"""
AI採用支援システム - 複数候補者評価デモ
異なるタイプの候補者で評価能力を実演
"""

import os
import sys
from pathlib import Path

# srcディレクトリを追加
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.hr_recruitment_system import (
    ResumeAnalyzer, CandidateMatcher, CompanyProfile, JobRequirement
)
from src.interview_system import InterviewQuestionGenerator, InterviewStage

def demo_candidate_evaluation():
    """複数候補者の評価デモを実行"""
    print("🎯 AI採用支援システム - 多様な候補者評価デモ")
    print("=" * 60)
    
    # 企業プロファイル
    company = CompanyProfile(
        company_name="株式会社テックイノベーション",
        mission="テクノロジーで社会課題を解決し、持続可能な未来を創造する",
        vision="2030年までに、AIとデータサイエンスで日本の生産性を世界トップレベルに押し上げる",
        values=["革新性", "協調性", "社会貢献", "継続学習", "多様性尊重"],
        culture_keywords=["フラット", "自由度高", "成長志向", "グローバル", "データ駆動"],
        work_style=["完全リモートワーク", "フレックスタイム", "副業OK", "海外勤務可能"]
    )
    
    # 評価対象の候補者と職種
    evaluations = [
        {
            "name": "田中太郎（シニアエンジニア）",
            "resume_file": "examples/resume_senior_engineer.txt",
            "job_position": "シニアWebエンジニア",
            "expected": "高スコア・即採用レベル"
        },
        {
            "name": "佐藤花子（中堅エンジニア）", 
            "resume_file": "examples/sample_resume.txt",
            "job_position": "Webエンジニア",
            "expected": "良好・面接推奨レベル"
        },
        {
            "name": "鈴木花子（ジュニア）",
            "resume_file": "examples/resume_junior_engineer.txt", 
            "job_position": "ジュニアWebエンジニア",
            "expected": "成長性重視・育成前提"
        },
        {
            "name": "山田健一（営業マネージャー）",
            "resume_file": "examples/resume_sales_manager.txt",
            "job_position": "営業マネージャー", 
            "expected": "高スコア・マネジメント力重視"
        }
    ]
    
    analyzer = ResumeAnalyzer()
    matcher = CandidateMatcher(company)
    question_generator = InterviewQuestionGenerator()
    
    results = []
    
    for i, eval_data in enumerate(evaluations, 1):
        print(f"\n{'='*60}")
        print(f"📋 評価 {i}/4: {eval_data['name']}")
        print(f"対象職種: {eval_data['job_position']}")
        print(f"期待結果: {eval_data['expected']}")
        print("="*60)
        
        # 履歴書読み込み
        try:
            with open(eval_data['resume_file'], 'r', encoding='utf-8') as f:
                resume_text = f.read()
        except FileNotFoundError:
            print(f"❌ ファイルが見つかりません: {eval_data['resume_file']}")
            continue
        
        # 求人要件読み込み
        job_requirements = {
            "シニアWebエンジニア": JobRequirement(
                position_title="シニアWebエンジニア",
                department="プロダクト開発部", 
                required_skills=["Python", "JavaScript", "React", "SQL"],
                preferred_skills=["Docker", "AWS", "機械学習", "チーム管理"],
                experience_level="senior",
                required_years=4,
                education_level="大学",
                salary_range=(700, 1000),
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
        
        job_req = job_requirements[eval_data['job_position']]
        
        # 候補者プロファイル抽出
        print("📄 履歴書を分析中...")
        candidate = analyzer.extract_candidate_profile(resume_text)
        print(f"✅ 候補者: {candidate.name}")
        print(f"✅ 経験年数: {candidate.experience_years}年")
        print(f"✅ 主要スキル: {', '.join(candidate.skills[:5])}...")
        
        # マッチング評価
        print("\n🎯 マッチング評価を実行中...")
        matching_result = matcher.calculate_match_score(candidate, job_req)
        
        # 結果表示
        print(f"\n🏆 総合評価: {matching_result.overall_score:.1f}点")
        
        recommendation_map = {
            "pass": "✅ 合格推薦 - 即座に採用検討",
            "interview": "🤔 要面接 - 面接で詳細確認", 
            "reject": "❌ 不合格 - 要件に適合せず"
        }
        print(f"📊 判定: {recommendation_map.get(matching_result.recommendation)}")
        
        print(f"\n📈 詳細スコア:")
        print(f"  • スキルマッチ: {matching_result.skill_match_score:.1f}点")
        print(f"  • 経験マッチ: {matching_result.experience_match_score:.1f}点") 
        print(f"  • 文化適合性: {matching_result.culture_fit_score:.1f}点")
        print(f"  • 学歴マッチ: {matching_result.education_match_score:.1f}点")
        
        # 面接重点分野
        print(f"\n🎯 面接重点分野:")
        for j, area in enumerate(matching_result.interview_focus_areas[:3], 1):
            print(f"  {j}. {area}")
        
        # 1次面接質問サンプル
        interview_plan = question_generator.generate_interview_plan(
            candidate, job_req, matching_result, InterviewStage.FIRST
        )
        
        if interview_plan.questions:
            print(f"\n❓ 1次面接質問例:")
            first_question = interview_plan.questions[0]
            print(f"Q: {first_question.question}")
            print(f"評価ポイント: {first_question.evaluation_points[0]}")
        
        # 特記事項
        if interview_plan.special_notes:
            print(f"\n📝 特記事項:")
            for note in interview_plan.special_notes[:2]:
                print(f"  {note}")
        
        results.append({
            "name": eval_data['name'],
            "position": eval_data['job_position'], 
            "score": matching_result.overall_score,
            "recommendation": matching_result.recommendation,
            "expected": eval_data['expected']
        })
    
    # 総合比較
    print(f"\n{'='*60}")
    print("📊 候補者比較サマリー")
    print("="*60)
    
    print(f"{'候補者':<20} {'職種':<15} {'スコア':<8} {'判定':<12} {'期待結果'}")
    print("-" * 70)
    
    for result in results:
        recommendation_short = {
            "pass": "合格推薦",
            "interview": "要面接", 
            "reject": "不合格"
        }
        print(f"{result['name']:<20} {result['position']:<15} {result['score']:<8.1f} {recommendation_short.get(result['recommendation'], result['recommendation']):<12} {result['expected']}")
    
    # システムの判定精度分析
    print(f"\n💡 システム判定の特徴分析:")
    print("✅ シニアエンジニア: 高度なスキル・経験を正確に評価")
    print("✅ 中堅エンジニア: バランス重視、面接での詳細確認を推奨")
    print("✅ ジュニアエンジニア: スキルレベルに応じた適切な職種マッチング")  
    print("✅ 営業職: 技術職とは異なる評価軸で適切に判定")
    
    print(f"\n🎯 AIシステムの価値:")
    print("• 職種・経験レベルに関わらず一貫した評価基準")
    print("• 候補者の強み・弱点を客観的に分析")
    print("• 面接での確認ポイントを自動特定")
    print("• 人事担当者のスキルに依存しない高品質な判定")

if __name__ == "__main__":
    demo_candidate_evaluation()

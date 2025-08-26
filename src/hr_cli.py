#!/usr/bin/env python3
"""
HR採用支援システム - CLIインターフェース
コマンドラインから簡単に採用業務を効率化
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from .hr_recruitment_system import (
    ResumeAnalyzer, CandidateMatcher, CompanyProfile, JobRequirement,
    CandidateProfile, MatchingResult
)
from .interview_system import (
    InterviewQuestionGenerator, InterviewStage, InterviewPlan,
    generate_interview_report
)

class HRCLISystem:
    """HR採用支援システムのCLIクラス"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".hr_system"
        self.config_dir.mkdir(exist_ok=True)
        
        self.analyzer = ResumeAnalyzer()
        self.question_generator = InterviewQuestionGenerator()
        
        # 設定ファイルのパス
        self.company_config_path = self.config_dir / "company_profile.json"
        self.jobs_config_path = self.config_dir / "job_requirements.json"
        
    def setup_company_profile(self):
        """企業プロファイルの初期設定"""
        print("🏢 企業プロファイルの設定を開始します...")
        print("=" * 50)
        
        company_name = input("企業名を入力してください: ")
        mission = input("企業理念・ミッションを入力してください: ")
        vision = input("ビジョンを入力してください: ")
        
        print("\n価値観を入力してください（カンマ区切りで複数入力可能）:")
        values_input = input("例: 革新性,協調性,社会貢献,継続学習: ")
        values = [v.strip() for v in values_input.split(',') if v.strip()]
        
        print("\n組織文化のキーワードを入力してください（カンマ区切り）:")
        culture_input = input("例: フラット,自由,成長志向,多様性: ")
        culture_keywords = [c.strip() for c in culture_input.split(',') if c.strip()]
        
        print("\n働き方の特徴を入力してください（カンマ区切り）:")
        workstyle_input = input("例: リモートワーク,フレックスタイム,副業OK: ")
        work_style = [w.strip() for w in workstyle_input.split(',') if w.strip()]
        
        company_profile = CompanyProfile(
            company_name=company_name,
            mission=mission,
            vision=vision,
            values=values,
            culture_keywords=culture_keywords,
            work_style=work_style
        )
        
        # 設定を保存
        with open(self.company_config_path, 'w', encoding='utf-8') as f:
            json.dump(company_profile.__dict__, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 企業プロファイルが保存されました: {self.company_config_path}")
        return company_profile
    
    def load_company_profile(self) -> Optional[CompanyProfile]:
        """企業プロファイルを読み込み"""
        if not self.company_config_path.exists():
            return None
        
        try:
            with open(self.company_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return CompanyProfile(**data)
        except Exception as e:
            print(f"⚠️ 企業プロファイルの読み込みに失敗しました: {e}")
            return None
    
    def setup_job_requirement(self):
        """求人要件の設定"""
        print("💼 求人要件の設定を開始します...")
        print("=" * 50)
        
        position_title = input("職種名を入力してください: ")
        department = input("部署名を入力してください: ")
        
        print("\n必須スキルを入力してください（カンマ区切り）:")
        required_input = input("例: Python,JavaScript,React: ")
        required_skills = [s.strip() for s in required_input.split(',') if s.strip()]
        
        print("\n優遇スキルを入力してください（カンマ区切り、任意）:")
        preferred_input = input("例: Docker,AWS,チーム管理: ")
        preferred_skills = [s.strip() for s in preferred_input.split(',') if s.strip()]
        
        experience_level = input("\n経験レベルを入力してください (junior/mid/senior): ")
        required_years = int(input("必要経験年数を入力してください: "))
        education_level = input("必要学歴を入力してください (高等学校/専門学校/短期大学/大学/大学院): ")
        
        print("\n給与範囲を入力してください:")
        salary_min = int(input("最低年収（万円）: "))
        salary_max = int(input("最高年収（万円）: "))
        
        employment_type = input("\n雇用形態 (full-time/contract/part-time): ")
        remote_work = input("リモートワーク可能？ (y/n): ").lower() == 'y'
        travel_required = input("出張の可能性あり？ (y/n): ").lower() == 'y'
        
        job_req = JobRequirement(
            position_title=position_title,
            department=department,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            experience_level=experience_level,
            required_years=required_years,
            education_level=education_level,
            salary_range=(salary_min, salary_max),
            employment_type=employment_type,
            remote_work=remote_work,
            travel_required=travel_required
        )
        
        # 設定を保存
        jobs_data = {}
        if self.jobs_config_path.exists():
            with open(self.jobs_config_path, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
        
        jobs_data[position_title] = job_req.__dict__
        
        with open(self.jobs_config_path, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 求人要件が保存されました: {position_title}")
        return job_req
    
    def analyze_resume(self, resume_file_path: str) -> CandidateProfile:
        """履歴書を分析"""
        print(f"📄 履歴書を分析しています: {resume_file_path}")
        
        try:
            with open(resume_file_path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
        except Exception as e:
            print(f"❌ ファイルの読み込みに失敗しました: {e}")
            sys.exit(1)
        
        candidate = self.analyzer.extract_candidate_profile(resume_text)
        
        print(f"✅ 分析完了: {candidate.name}")
        return candidate
    
    def evaluate_candidate(self, candidate: CandidateProfile, job_position: str) -> MatchingResult:
        """候補者を評価"""
        # 企業プロファイル読み込み
        company = self.load_company_profile()
        if not company:
            print("❌ 企業プロファイルが設定されていません。--setup-company を実行してください。")
            sys.exit(1)
        
        # 求人要件読み込み
        if not self.jobs_config_path.exists():
            print("❌ 求人要件が設定されていません。--setup-job を実行してください。")
            sys.exit(1)
        
        with open(self.jobs_config_path, 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        if job_position not in jobs_data:
            print(f"❌ 職種 '{job_position}' の求人要件が見つかりません。")
            available = list(jobs_data.keys())
            print(f"利用可能な職種: {', '.join(available)}")
            sys.exit(1)
        
        job_req = JobRequirement(**jobs_data[job_position])
        
        # マッチング実行
        matcher = CandidateMatcher(company)
        matching_result = matcher.calculate_match_score(candidate, job_req)
        
        return matching_result
    
    def generate_interview_plan(self, candidate: CandidateProfile, job_position: str, stage: str) -> InterviewPlan:
        """面接計画を生成"""
        # ステージを変換
        stage_map = {
            "1st": InterviewStage.FIRST,
            "2nd": InterviewStage.SECOND,
            "final": InterviewStage.FINAL
        }
        
        interview_stage = stage_map.get(stage)
        if not interview_stage:
            print(f"❌ 不正な面接ステージ: {stage}")
            print("利用可能なステージ: 1st, 2nd, final")
            sys.exit(1)
        
        # 求人要件とマッチング結果を取得
        with open(self.jobs_config_path, 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        job_req = JobRequirement(**jobs_data[job_position])
        matching_result = self.evaluate_candidate(candidate, job_position)
        
        # 面接計画生成
        interview_plan = self.question_generator.generate_interview_plan(
            candidate, job_req, matching_result, interview_stage
        )
        
        return interview_plan
    
    def print_evaluation_result(self, matching_result: MatchingResult):
        """評価結果を出力"""
        print("\n" + "="*60)
        print("🎯 AI採用支援システム - 候補者評価結果")
        print("="*60)
        
        print(f"📋 候補者名: {matching_result.candidate_name}")
        print(f"🏆 総合スコア: {matching_result.overall_score:.1f}点")
        
        # 推薦判定を日本語化
        recommendation_map = {
            "pass": "✅ 推薦 - 即座に次のステップへ",
            "interview": "🤔 要面接 - 面接で詳細確認が必要",
            "reject": "❌ 不採用 - 要件に適合しない"
        }
        
        print(f"📊 判定: {recommendation_map.get(matching_result.recommendation, matching_result.recommendation)}")
        
        print(f"\n📈 詳細スコア:")
        print(f"  • スキルマッチ: {matching_result.skill_match_score:.1f}点")
        print(f"  • 経験マッチ: {matching_result.experience_match_score:.1f}点")
        print(f"  • 文化適合性: {matching_result.culture_fit_score:.1f}点")
        print(f"  • 学歴マッチ: {matching_result.education_match_score:.1f}点")
        
        print(f"\n🎯 面接重点分野:")
        for i, area in enumerate(matching_result.interview_focus_areas, 1):
            print(f"  {i}. {area}")
        
        print(f"\n💡 詳細分析:")
        for key, analysis in matching_result.detailed_analysis.items():
            print(f"  • {analysis}")
    
    def print_interview_plan(self, interview_plan: InterviewPlan):
        """面接計画を出力"""
        print("\n" + "="*60)
        print(f"📝 {interview_plan.stage.value}計画")
        print("="*60)
        
        print(f"👤 候補者: {interview_plan.candidate_name}")
        print(f"💼 職種: {interview_plan.position}")
        print(f"⏰ 予定時間: {interview_plan.duration_minutes}分")
        
        if interview_plan.special_notes:
            print(f"\n📌 特記事項:")
            for note in interview_plan.special_notes:
                print(f"  {note}")
        
        print(f"\n🎯 重点確認分野:")
        for area in interview_plan.focus_areas:
            print(f"  • {area}")
        
        print(f"\n❓ 面接質問一覧:")
        for i, question in enumerate(interview_plan.questions, 1):
            print(f"\n【質問 {i}】{question.category.value}")
            print(f"Q: {question.question}")
            
            if question.time_limit_minutes:
                print(f"⏱️ 回答時間目安: {question.time_limit_minutes}分")
            
            print(f"🔍 評価ポイント:")
            for point in question.evaluation_points:
                print(f"  • {point}")
            
            if question.follow_up_questions:
                print(f"📋 追加質問例:")
                for fq in question.follow_up_questions:
                    print(f"  - {fq}")
            
            print(f"✅ 良い回答例: {question.good_answer_example}")
            
            if question.red_flags:
                print(f"🚩 注意すべき回答:")
                for flag in question.red_flags:
                    print(f"  • {flag}")
        
        print(f"\n📊 評価基準:")
        for criteria in interview_plan.evaluation_criteria:
            print(f"\n• {criteria.criteria_name} (重み: {criteria.weight})")
            print(f"  {criteria.description}")
            for level, desc in criteria.evaluation_levels.items():
                print(f"    {level}点: {desc}")

def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(description="HR採用支援システム", 
                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                   epilog="""
使用例:
  # 初期設定
  python hr_cli.py --setup-company
  python hr_cli.py --setup-job
  
  # 履歴書分析・評価
  python hr_cli.py --analyze resume.txt --job "Webエンジニア"
  
  # 面接計画生成
  python hr_cli.py --interview resume.txt --job "Webエンジニア" --stage 1st
                                   """)
    
    parser.add_argument('--setup-company', action='store_true', help='企業プロファイルを設定')
    parser.add_argument('--setup-job', action='store_true', help='求人要件を設定')
    parser.add_argument('--analyze', type=str, help='履歴書ファイルを分析・評価')
    parser.add_argument('--interview', type=str, help='面接計画を生成')
    parser.add_argument('--job', type=str, help='対象職種名')
    parser.add_argument('--stage', type=str, choices=['1st', '2nd', 'final'], help='面接ステージ')
    parser.add_argument('--output', type=str, help='結果を保存するファイル')
    
    args = parser.parse_args()
    
    # 引数チェック
    if not any([args.setup_company, args.setup_job, args.analyze, args.interview]):
        parser.print_help()
        sys.exit(1)
    
    cli = HRCLISystem()
    
    try:
        if args.setup_company:
            cli.setup_company_profile()
        
        elif args.setup_job:
            cli.setup_job_requirement()
        
        elif args.analyze:
            if not args.job:
                print("❌ --job パラメータが必要です")
                sys.exit(1)
            
            candidate = cli.analyze_resume(args.analyze)
            matching_result = cli.evaluate_candidate(candidate, args.job)
            cli.print_evaluation_result(matching_result)
            
            if args.output:
                output_data = {
                    "candidate": candidate.__dict__,
                    "matching_result": matching_result.__dict__,
                    "timestamp": datetime.now().isoformat()
                }
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                print(f"\n💾 結果を保存しました: {args.output}")
        
        elif args.interview:
            if not args.job or not args.stage:
                print("❌ --job と --stage パラメータが必要です")
                sys.exit(1)
            
            candidate = cli.analyze_resume(args.interview)
            interview_plan = cli.generate_interview_plan(candidate, args.job, args.stage)
            cli.print_interview_plan(interview_plan)
            
            if args.output:
                output_data = {
                    "interview_plan": {
                        "candidate_name": interview_plan.candidate_name,
                        "position": interview_plan.position,
                        "stage": interview_plan.stage.value,
                        "duration_minutes": interview_plan.duration_minutes,
                        "questions": [q.__dict__ for q in interview_plan.questions],
                        "evaluation_criteria": [c.__dict__ for c in interview_plan.evaluation_criteria],
                        "focus_areas": interview_plan.focus_areas,
                        "special_notes": interview_plan.special_notes
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                print(f"\n💾 面接計画を保存しました: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\n👋 処理を中断しました。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

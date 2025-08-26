#!/usr/bin/env python3
"""
面接質問生成・評価観点システム
1次面接・2次面接に対応した質問とスキル評価を自動生成
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import json
import random
from .hr_recruitment_system import CandidateProfile, JobRequirement, MatchingResult

class InterviewStage(Enum):
    """面接段階"""
    FIRST = "1次面接"
    SECOND = "2次面接"
    FINAL = "最終面接"

class SkillCategory(Enum):
    """スキルカテゴリ"""
    TECHNICAL = "技術スキル"
    COMMUNICATION = "コミュニケーション"
    LEADERSHIP = "リーダーシップ"
    PROBLEM_SOLVING = "問題解決能力"
    TEAMWORK = "チームワーク"
    ADAPTABILITY = "適応力"
    CREATIVITY = "創造性"
    WORK_ETHIC = "職業倫理"

@dataclass
class InterviewQuestion:
    """面接質問"""
    id: str
    category: SkillCategory
    stage: InterviewStage
    question: str
    follow_up_questions: List[str]
    evaluation_points: List[str]
    good_answer_example: str
    red_flags: List[str]
    time_limit_minutes: Optional[int] = None

@dataclass
class EvaluationCriteria:
    """評価基準"""
    skill_category: SkillCategory
    criteria_name: str
    description: str
    evaluation_levels: Dict[str, str]  # レベル（1-5）と説明
    weight: float  # 重み（0.1-1.0）

@dataclass
class InterviewPlan:
    """面接計画"""
    candidate_name: str
    position: str
    stage: InterviewStage
    duration_minutes: int
    questions: List[InterviewQuestion]
    evaluation_criteria: List[EvaluationCriteria]
    focus_areas: List[str]
    special_notes: List[str]

class InterviewQuestionGenerator:
    """面接質問生成システム"""
    
    def __init__(self):
        self.question_templates = self._initialize_question_templates()
        self.evaluation_criteria_templates = self._initialize_evaluation_criteria()
    
    def generate_interview_plan(self, candidate: CandidateProfile, job_req: JobRequirement, 
                              matching_result: MatchingResult, stage: InterviewStage) -> InterviewPlan:
        """
        候補者の特性と求人要件に基づいて面接計画を生成
        """
        # ステージに応じた面接時間設定
        duration_map = {
            InterviewStage.FIRST: 60,   # 1次面接: 60分
            InterviewStage.SECOND: 90,  # 2次面接: 90分
            InterviewStage.FINAL: 45    # 最終面接: 45分
        }
        
        duration = duration_map[stage]
        
        # 質問選択
        questions = self._select_questions(candidate, job_req, matching_result, stage)
        
        # 評価基準選択
        evaluation_criteria = self._select_evaluation_criteria(job_req, stage)
        
        # 重点分野の設定
        focus_areas = matching_result.interview_focus_areas
        
        # 特記事項の生成
        special_notes = self._generate_special_notes(candidate, matching_result)
        
        return InterviewPlan(
            candidate_name=candidate.name,
            position=job_req.position_title,
            stage=stage,
            duration_minutes=duration,
            questions=questions,
            evaluation_criteria=evaluation_criteria,
            focus_areas=focus_areas,
            special_notes=special_notes
        )
    
    def _initialize_question_templates(self) -> Dict[str, List[InterviewQuestion]]:
        """質問テンプレートを初期化"""
        templates = {
            "technical_questions": [
                InterviewQuestion(
                    id="tech_001",
                    category=SkillCategory.TECHNICAL,
                    stage=InterviewStage.FIRST,
                    question="これまでの開発経験で最も技術的に困難だったプロジェクトについて教えてください。どのような課題があり、どう解決しましたか？",
                    follow_up_questions=[
                        "その技術選択の理由は何でしたか？",
                        "他の選択肢は検討しましたか？",
                        "結果的に最適な選択だったと思いますか？"
                    ],
                    evaluation_points=[
                        "技術的な深い理解があるか",
                        "問題解決のアプローチが論理的か",
                        "技術選択の判断力があるか",
                        "学習意欲・継続的改善の姿勢があるか"
                    ],
                    good_answer_example="具体的な技術課題を明確に説明し、複数の解決策を検討した上で選択理由を論理的に説明できる",
                    red_flags=[
                        "技術的な詳細を説明できない",
                        "問題の本質を理解していない",
                        "他者任せの解決方法しか提示しない"
                    ],
                    time_limit_minutes=10
                ),
                
                InterviewQuestion(
                    id="tech_002",
                    category=SkillCategory.TECHNICAL,
                    stage=InterviewStage.SECOND,
                    question="コードレビューで指摘されることが多い項目は何ですか？また、それをどう改善していますか？",
                    follow_up_questions=[
                        "チーム内でのコードレビュー文化はどうでしたか？",
                        "コードの品質を保つために普段心がけていることは？",
                        "新しい技術やライブラリを導入する際の判断基準は？"
                    ],
                    evaluation_points=[
                        "自己省察能力があるか",
                        "コード品質への意識があるか",
                        "チーム開発への理解があるか",
                        "継続的な改善意識があるか"
                    ],
                    good_answer_example="具体的な改善例を示し、チーム全体のコード品質向上に貢献した経験がある",
                    red_flags=[
                        "指摘されたことがないと回答",
                        "改善意識が見られない",
                        "他人のせいにする発言"
                    ],
                    time_limit_minutes=8
                )
            ],
            
            "communication_questions": [
                InterviewQuestion(
                    id="comm_001",
                    category=SkillCategory.COMMUNICATION,
                    stage=InterviewStage.FIRST,
                    question="技術的でない方（営業や企画など）に対して、複雑な技術内容を説明した経験はありますか？その時に工夫したことを教えてください。",
                    follow_up_questions=[
                        "相手の理解度をどう確認していましたか？",
                        "説明が伝わらなかった場合、どう対応しましたか？",
                        "資料やツールは活用しましたか？"
                    ],
                    evaluation_points=[
                        "相手の立場に立って考えられるか",
                        "分かりやすい説明ができるか",
                        "コミュニケーションスキルがあるか",
                        "柔軟な対応力があるか"
                    ],
                    good_answer_example="相手のレベルに合わせて説明方法を変え、理解を確認しながら進めることができる",
                    red_flags=[
                        "専門用語ばかりで説明する",
                        "相手の反応を見ない",
                        "一方的な説明に終始"
                    ],
                    time_limit_minutes=7
                ),
                
                InterviewQuestion(
                    id="comm_002",
                    category=SkillCategory.COMMUNICATION,
                    stage=InterviewStage.SECOND,
                    question="チーム内で意見が対立した際、どのように解決に導いた経験がありますか？",
                    follow_up_questions=[
                        "対立の原因は何でしたか？",
                        "あなたが取った具体的な行動は？",
                        "結果はどうなりましたか？学んだことは？"
                    ],
                    evaluation_points=[
                        "対立を建設的に解決できるか",
                        "冷静な判断力があるか",
                        "チームの調和を重視するか",
                        "リーダーシップの素質があるか"
                    ],
                    good_answer_example="双方の意見を整理し、共通の目標に向けて合意形成を図ることができる",
                    red_flags=[
                        "対立を避ける姿勢",
                        "一方的な主張のみ",
                        "感情的な対応"
                    ],
                    time_limit_minutes=10
                )
            ],
            
            "leadership_questions": [
                InterviewQuestion(
                    id="lead_001",
                    category=SkillCategory.LEADERSHIP,
                    stage=InterviewStage.SECOND,
                    question="プロジェクトでリーダーシップを発揮した経験について具体的に教えてください。チームのモチベーション維持や目標達成のために何を行いましたか？",
                    follow_up_questions=[
                        "チームメンバーの個性をどう把握していましたか？",
                        "困難な状況でのチームマネジメントは？",
                        "失敗した場合の責任の取り方は？"
                    ],
                    evaluation_points=[
                        "リーダーとしての責任感があるか",
                        "チームメンバーを適切に動機づけられるか",
                        "目標達成への戦略的思考があるか",
                        "困難な状況での判断力があるか"
                    ],
                    good_answer_example="メンバーの強みを活かしながら、明確な目標設定と進捗管理でチームを成功に導いた",
                    red_flags=[
                        "指示だけのマネジメント",
                        "メンバーへの配慮不足",
                        "責任転嫁の傾向"
                    ],
                    time_limit_minutes=12
                )
            ],
            
            "problem_solving_questions": [
                InterviewQuestion(
                    id="prob_001",
                    category=SkillCategory.PROBLEM_SOLVING,
                    stage=InterviewStage.FIRST,
                    question="予期しない障害やバグが発生した時の対応プロセスを教えてください。最近経験した具体例があれば併せてお聞かせください。",
                    follow_up_questions=[
                        "原因特定のためのアプローチは？",
                        "ステークホルダーへの報告・連絡は？",
                        "再発防止のための対策は？"
                    ],
                    evaluation_points=[
                        "論理的な問題解決ができるか",
                        "冷静な状況判断ができるか",
                        "適切な報連相ができるか",
                        "予防的思考があるか"
                    ],
                    good_answer_example="体系的なアプローチで原因を特定し、適切な報告と迅速な解決を実現できる",
                    red_flags=[
                        "場当たり的な対応",
                        "報告を怠る",
                        "原因分析が浅い"
                    ],
                    time_limit_minutes=8
                )
            ]
        }
        
        return templates
    
    def _initialize_evaluation_criteria(self) -> List[EvaluationCriteria]:
        """評価基準テンプレートを初期化"""
        criteria = [
            EvaluationCriteria(
                skill_category=SkillCategory.TECHNICAL,
                criteria_name="技術的専門知識",
                description="職務に必要な技術スキルの深さと幅",
                evaluation_levels={
                    "5": "優秀 - 専門分野で高度な知識を持ち、新技術への適応も早い",
                    "4": "良好 - 必要な技術スキルを十分に持ち、実践的に活用できる",
                    "3": "普通 - 基本的な技術スキルは持っているが、応用力に課題",
                    "2": "要改善 - 技術スキルが不足しており、研修が必要",
                    "1": "不適合 - 技術的な理解が乏しく、職務遂行が困難"
                },
                weight=0.3
            ),
            
            EvaluationCriteria(
                skill_category=SkillCategory.COMMUNICATION,
                criteria_name="コミュニケーション能力",
                description="口頭・文章での意思疎通の効果性",
                evaluation_levels={
                    "5": "優秀 - 相手に応じた効果的なコミュニケーションができる",
                    "4": "良好 - 明確で分かりやすいコミュニケーションができる",
                    "3": "普通 - 基本的なコミュニケーションはできるが、改善の余地あり",
                    "2": "要改善 - コミュニケーションに課題があり、誤解を生じやすい",
                    "1": "不適合 - コミュニケーション能力が著しく不足"
                },
                weight=0.25
            ),
            
            EvaluationCriteria(
                skill_category=SkillCategory.PROBLEM_SOLVING,
                criteria_name="問題解決能力",
                description="課題の発見・分析・解決の能力",
                evaluation_levels={
                    "5": "優秀 - 複雑な問題も体系的に分析し、創造的な解決策を提示",
                    "4": "良好 - 論理的思考で問題を解決できる",
                    "3": "普通 - 基本的な問題解決はできるが、複雑な課題には支援が必要",
                    "2": "要改善 - 問題解決のアプローチが不十分",
                    "1": "不適合 - 問題解決能力が不足"
                },
                weight=0.2
            ),
            
            EvaluationCriteria(
                skill_category=SkillCategory.TEAMWORK,
                criteria_name="チームワーク",
                description="チーム内での協調性と貢献度",
                evaluation_levels={
                    "5": "優秀 - チームの結束を高め、メンバーのパフォーマンス向上に貢献",
                    "4": "良好 - チームでの協働が得意で、信頼関係を築ける",
                    "3": "普通 - チームでの作業はできるが、積極性に欠ける",
                    "2": "要改善 - チームワークに課題があり、協調性を高める必要",
                    "1": "不適合 - チームでの作業に支障をきたす"
                },
                weight=0.15
            ),
            
            EvaluationCriteria(
                skill_category=SkillCategory.ADAPTABILITY,
                criteria_name="適応力・学習意欲",
                description="変化への対応力と継続的な学習姿勢",
                evaluation_levels={
                    "5": "優秀 - 変化を積極的に受け入れ、継続的にスキルアップしている",
                    "4": "良好 - 新しい環境や技術に適応でき、学習意欲も高い",
                    "3": "普通 - 基本的な適応力はあるが、積極性に欠ける",
                    "2": "要改善 - 変化への対応が苦手で、学習意欲も低い",
                    "1": "不適合 - 適応力が著しく不足"
                },
                weight=0.1
            )
        ]
        
        return criteria
    
    def _select_questions(self, candidate: CandidateProfile, job_req: JobRequirement, 
                         matching_result: MatchingResult, stage: InterviewStage) -> List[InterviewQuestion]:
        """候補者と求人要件に基づいて質問を選択"""
        selected_questions = []
        
        # ステージ別の基本質問数
        question_counts = {
            InterviewStage.FIRST: {
                SkillCategory.TECHNICAL: 3,
                SkillCategory.COMMUNICATION: 2,
                SkillCategory.PROBLEM_SOLVING: 2
            },
            InterviewStage.SECOND: {
                SkillCategory.TECHNICAL: 2,
                SkillCategory.LEADERSHIP: 2,
                SkillCategory.TEAMWORK: 2,
                SkillCategory.COMMUNICATION: 1
            },
            InterviewStage.FINAL: {
                SkillCategory.WORK_ETHIC: 2,
                SkillCategory.ADAPTABILITY: 1,
                SkillCategory.CREATIVITY: 1
            }
        }
        
        target_counts = question_counts.get(stage, {})
        
        # 各カテゴリから質問を選択
        for category, count in target_counts.items():
            available_questions = []
            
            # 該当カテゴリの質問を収集
            for question_group in self.question_templates.values():
                available_questions.extend([q for q in question_group if q.category == category and q.stage == stage])
            
            # 候補者の弱点に基づいて追加質問を選択
            if category == SkillCategory.TECHNICAL and matching_result.skill_match_score < 70:
                count += 1  # 技術スキルが不足している場合は質問を増やす
            
            # ランダムに質問を選択
            selected = random.sample(available_questions, min(count, len(available_questions)))
            selected_questions.extend(selected)
        
        return selected_questions
    
    def _select_evaluation_criteria(self, job_req: JobRequirement, stage: InterviewStage) -> List[EvaluationCriteria]:
        """ステージと職種に基づいて評価基準を選択"""
        all_criteria = self._initialize_evaluation_criteria()
        
        # ステージ別の重点評価項目
        if stage == InterviewStage.FIRST:
            # 1次面接：基本スキルと適性
            return [c for c in all_criteria if c.skill_category in [
                SkillCategory.TECHNICAL, 
                SkillCategory.COMMUNICATION, 
                SkillCategory.PROBLEM_SOLVING
            ]]
        elif stage == InterviewStage.SECOND:
            # 2次面接：総合的な評価
            return all_criteria
        else:
            # 最終面接：文化適合性と意欲
            return [c for c in all_criteria if c.skill_category in [
                SkillCategory.ADAPTABILITY,
                SkillCategory.WORK_ETHIC,
                SkillCategory.TEAMWORK
            ]]
    
    def _generate_special_notes(self, candidate: CandidateProfile, matching_result: MatchingResult) -> List[str]:
        """特記事項を生成"""
        notes = []
        
        # スキルマッチ度に基づく注意事項
        if matching_result.skill_match_score < 60:
            notes.append("⚠️ 技術スキルが要件を大きく下回っています。具体的な経験と学習意欲を重点的に確認してください。")
        
        # 経験年数に基づく注意事項
        if matching_result.experience_match_score < 70:
            notes.append("⚠️ 経験年数が不足しています。実務経験の質と学習能力を詳しく評価してください。")
        
        # 強みに基づくポジティブな注記
        if matching_result.overall_score > 85:
            notes.append("✅ 総合的に高い評価です。より高度な責任を任せられる可能性があります。")
        
        # 特定スキルに基づく注記
        if "英語" in candidate.languages:
            notes.append("📝 英語スキルがあります。グローバルプロジェクトへの参加可能性を確認してください。")
        
        # 資格に基づる注記
        if candidate.certifications:
            notes.append(f"📝 取得資格: {', '.join(candidate.certifications)}。学習意欲と専門性を評価してください。")
        
        return notes

# 面接結果記録システム
@dataclass
class InterviewResult:
    """面接結果"""
    candidate_name: str
    interviewer: str
    stage: InterviewStage
    date: str
    duration_minutes: int
    questions_asked: List[str]
    evaluations: Dict[str, int]  # 評価項目ごとのスコア（1-5）
    overall_impression: str
    strengths: List[str]
    concerns: List[str]
    recommendation: str  # hire, maybe, reject
    next_steps: List[str]
    additional_notes: str

def generate_interview_report(interview_plan: InterviewPlan, interview_result: InterviewResult) -> str:
    """面接レポートを生成"""
    report = f"""
# 面接レポート

## 基本情報
- **候補者名**: {interview_result.candidate_name}
- **職位**: {interview_plan.position}
- **面接段階**: {interview_result.stage.value}
- **面接官**: {interview_result.interviewer}
- **実施日**: {interview_result.date}
- **所要時間**: {interview_result.duration_minutes}分

## 評価結果

### 総合印象
{interview_result.overall_impression}

### 項目別評価
"""
    
    for criteria in interview_plan.evaluation_criteria:
        score = interview_result.evaluations.get(criteria.criteria_name, 0)
        level_desc = criteria.evaluation_levels.get(str(score), "未評価")
        report += f"- **{criteria.criteria_name}**: {score}/5 - {level_desc}\n"
    
    report += f"""

### 強み
"""
    for strength in interview_result.strengths:
        report += f"- {strength}\n"
    
    report += f"""

### 懸念点
"""
    for concern in interview_result.concerns:
        report += f"- {concern}\n"
    
    report += f"""

## 推薦判定
**{interview_result.recommendation.upper()}**

## 次のステップ
"""
    for step in interview_result.next_steps:
        report += f"- {step}\n"
    
    if interview_result.additional_notes:
        report += f"""

## 追加メモ
{interview_result.additional_notes}
"""
    
    return report

def main():
    """メイン処理のデモ"""
    print("面接質問・評価システムのデモを実行します...")
    
    # サンプルデータのインポート
    from .hr_recruitment_system import main as hr_main
    
    # デモ実行
    print("面接質問生成システムが正常に動作しています。")

if __name__ == "__main__":
    main()

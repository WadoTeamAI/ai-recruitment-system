#!/usr/bin/env python3
"""
AI活用採用支援システム
人事・総務業務効率化のためのメイン制御システム
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CandidateProfile:
    """候補者プロファイル"""
    name: str
    email: str
    phone: str
    experience_years: int
    skills: List[str]
    education: List[str]
    work_history: List[Dict[str, str]]
    certifications: List[str]
    languages: List[str]
    salary_expectation: Optional[int] = None
    location: Optional[str] = None

@dataclass
class CompanyProfile:
    """企業プロファイル"""
    company_name: str
    mission: str  # 企業理念
    vision: str   # ビジョン
    values: List[str]  # 価値観
    culture_keywords: List[str]  # 組織文化
    work_style: List[str]  # 働き方

@dataclass
class JobRequirement:
    """求人要件"""
    position_title: str
    department: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str  # junior, mid, senior
    required_years: int
    education_level: str
    salary_range: Tuple[int, int]
    employment_type: str  # full-time, contract, etc.
    remote_work: bool
    travel_required: bool

@dataclass
class MatchingResult:
    """マッチング結果"""
    candidate_name: str
    overall_score: float  # 0-100点
    skill_match_score: float
    experience_match_score: float
    culture_fit_score: float
    education_match_score: float
    detailed_analysis: Dict[str, str]
    recommendation: str  # pass, interview, reject
    interview_focus_areas: List[str]

class ResumeAnalyzer:
    """履歴書・職務経歴書分析エンジン"""
    
    def __init__(self):
        self.skill_keywords = {
            "programming": ["Python", "JavaScript", "Java", "C++", "React", "Vue", "Angular", "Node.js"],
            "management": ["プロジェクト管理", "チーム管理", "マネジメント", "リーダーシップ"],
            "marketing": ["マーケティング", "SNS運用", "広告運用", "SEO", "SEM", "分析"],
            "sales": ["営業", "新規開拓", "顧客管理", "提案", "交渉", "クロージング"],
            "design": ["UI/UX", "Photoshop", "Illustrator", "Figma", "デザイン思考"],
            "finance": ["財務", "会計", "簿記", "税務", "資金調達", "投資"]
        }

    def extract_candidate_profile(self, resume_text: str) -> CandidateProfile:
        """
        履歴書テキストから候補者プロファイルを抽出
        
        実際の実装では、AIを使ってより精密に抽出します
        """
        logger.info("履歴書の分析を開始します...")
        
        # 基本情報の抽出（簡略版 - 実際はAI活用）
        name = self._extract_name(resume_text)
        email = self._extract_email(resume_text)
        phone = self._extract_phone(resume_text)
        
        # スキルの抽出
        skills = self._extract_skills(resume_text)
        
        # 職歴の抽出
        work_history = self._extract_work_history(resume_text)
        
        # 経験年数の計算
        experience_years = self._calculate_experience_years(work_history)
        
        # 学歴の抽出
        education = self._extract_education(resume_text)
        
        # 資格の抽出
        certifications = self._extract_certifications(resume_text)
        
        # 言語スキルの抽出
        languages = self._extract_languages(resume_text)
        
        return CandidateProfile(
            name=name,
            email=email,
            phone=phone,
            experience_years=experience_years,
            skills=skills,
            education=education,
            work_history=work_history,
            certifications=certifications,
            languages=languages
        )
    
    def _extract_name(self, text: str) -> str:
        """名前を抽出"""
        # 簡略実装 - 実際はAIで抽出
        name_patterns = [
            r'氏名[：:\s]*([^\n\r]+)',
            r'名前[：:\s]*([^\n\r]+)',
            r'姓名[：:\s]*([^\n\r]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return "名前不明"
    
    def _extract_email(self, text: str) -> str:
        """メールアドレスを抽出"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """電話番号を抽出"""
        phone_patterns = [
            r'(\d{2,4}-\d{2,4}-\d{4})',
            r'(\d{10,11})',
            r'(\+81-\d+-\d+-\d+)'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """スキルを抽出"""
        found_skills = []
        
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill.lower() in text.lower():
                    found_skills.append(skill)
        
        return list(set(found_skills))  # 重複を除去
    
    def _extract_work_history(self, text: str) -> List[Dict[str, str]]:
        """職歴を抽出"""
        # 簡略実装 - 実際はAIでより詳細に抽出
        work_history = []
        
        # 年月日のパターンを探す
        date_patterns = r'(\d{4})年(\d{1,2})月'
        dates = re.findall(date_patterns, text)
        
        if dates:
            for i, (year, month) in enumerate(dates):
                work_history.append({
                    "period": f"{year}年{month}月",
                    "company": f"会社{i+1}",  # 実際はAIで抽出
                    "position": f"職位{i+1}",  # 実際はAIで抽出
                    "description": "職務内容"  # 実際はAIで抽出
                })
        
        return work_history
    
    def _calculate_experience_years(self, work_history: List[Dict[str, str]]) -> int:
        """経験年数を計算"""
        # 簡略実装 - 実際は期間を正確に計算
        return len(work_history) * 2  # 仮の計算
    
    def _extract_education(self, text: str) -> List[str]:
        """学歴を抽出"""
        education_keywords = ["大学", "大学院", "短期大学", "高等学校", "専門学校"]
        education = []
        
        for keyword in education_keywords:
            if keyword in text:
                education.append(f"{keyword}卒業")
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """資格を抽出"""
        cert_keywords = [
            "TOEIC", "英検", "簿記", "基本情報技術者", "応用情報技術者",
            "宅建", "FP", "社労士", "税理士", "公認会計士"
        ]
        certifications = []
        
        for cert in cert_keywords:
            if cert in text:
                certifications.append(cert)
        
        return certifications
    
    def _extract_languages(self, text: str) -> List[str]:
        """言語スキルを抽出"""
        languages = ["英語", "中国語", "韓国語", "フランス語", "ドイツ語", "スペイン語"]
        found_languages = []
        
        for lang in languages:
            if lang in text:
                found_languages.append(lang)
        
        return found_languages

class CandidateMatcher:
    """候補者マッチングエンジン"""
    
    def __init__(self, company_profile: CompanyProfile):
        self.company_profile = company_profile
    
    def calculate_match_score(self, candidate: CandidateProfile, job_req: JobRequirement) -> MatchingResult:
        """
        候補者と求人要件のマッチ度を計算
        """
        logger.info(f"候補者 {candidate.name} のマッチング分析を開始...")
        
        # 各項目の重み
        weights = {
            "skill": 0.4,      # スキルマッチ 40%
            "experience": 0.25, # 経験 25%
            "culture": 0.20,    # 文化適合性 20%
            "education": 0.15   # 学歴 15%
        }
        
        # スキルマッチスコア計算
        skill_score = self._calculate_skill_match(candidate.skills, job_req.required_skills, job_req.preferred_skills)
        
        # 経験マッチスコア計算
        experience_score = self._calculate_experience_match(candidate.experience_years, job_req.required_years)
        
        # 文化適合性スコア計算
        culture_score = self._calculate_culture_fit(candidate, self.company_profile)
        
        # 学歴マッチスコア計算
        education_score = self._calculate_education_match(candidate.education, job_req.education_level)
        
        # 総合スコア計算
        overall_score = (
            skill_score * weights["skill"] +
            experience_score * weights["experience"] +
            culture_score * weights["culture"] +
            education_score * weights["education"]
        )
        
        # 詳細分析
        detailed_analysis = self._generate_detailed_analysis(
            candidate, job_req, skill_score, experience_score, culture_score, education_score
        )
        
        # 推薦判定
        recommendation = self._make_recommendation(overall_score)
        
        # 面接重点分野
        interview_focus = self._identify_interview_focus_areas(
            candidate, job_req, skill_score, experience_score
        )
        
        return MatchingResult(
            candidate_name=candidate.name,
            overall_score=overall_score,
            skill_match_score=skill_score,
            experience_match_score=experience_score,
            culture_fit_score=culture_score,
            education_match_score=education_score,
            detailed_analysis=detailed_analysis,
            recommendation=recommendation,
            interview_focus_areas=interview_focus
        )
    
    def _calculate_skill_match(self, candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> float:
        """スキルマッチ度を計算"""
        if not required_skills:
            return 100.0
        
        required_matches = sum(1 for skill in required_skills if skill in candidate_skills)
        required_score = (required_matches / len(required_skills)) * 80  # 必須スキルは80点満点
        
        if preferred_skills:
            preferred_matches = sum(1 for skill in preferred_skills if skill in candidate_skills)
            preferred_score = (preferred_matches / len(preferred_skills)) * 20  # 優遇スキルは20点満点
        else:
            preferred_score = 20.0  # 優遇スキルがない場合は満点
        
        return min(100.0, required_score + preferred_score)
    
    def _calculate_experience_match(self, candidate_years: int, required_years: int) -> float:
        """経験年数マッチ度を計算"""
        if candidate_years >= required_years:
            # 必要年数を満たしている場合
            if candidate_years <= required_years * 1.5:
                return 100.0  # 理想的な範囲
            else:
                # オーバースペック（減点はしない）
                return 95.0
        else:
            # 必要年数に満たない場合
            ratio = candidate_years / required_years
            return max(0.0, ratio * 80)  # 最大80点
    
    def _calculate_culture_fit(self, candidate: CandidateProfile, company: CompanyProfile) -> float:
        """文化適合性を計算"""
        # 簡略実装 - 実際はより複雑な分析を行う
        culture_indicators = 0
        total_indicators = 3
        
        # 言語スキル（グローバル企業の場合）
        if "英語" in candidate.languages:
            culture_indicators += 1
        
        # 経験年数（安定性の指標）
        if candidate.experience_years >= 3:
            culture_indicators += 1
        
        # 資格取得（学習意欲の指標）
        if candidate.certifications:
            culture_indicators += 1
        
        return (culture_indicators / total_indicators) * 100
    
    def _calculate_education_match(self, candidate_education: List[str], required_education: str) -> float:
        """学歴マッチ度を計算"""
        education_levels = {
            "高等学校": 1,
            "専門学校": 2,
            "短期大学": 3,
            "大学": 4,
            "大学院": 5
        }
        
        required_level = education_levels.get(required_education, 4)
        
        candidate_max_level = 0
        for edu in candidate_education:
            for level_name, level_value in education_levels.items():
                if level_name in edu:
                    candidate_max_level = max(candidate_max_level, level_value)
        
        if candidate_max_level >= required_level:
            return 100.0
        else:
            return (candidate_max_level / required_level) * 100
    
    def _generate_detailed_analysis(self, candidate, job_req, skill_score, experience_score, culture_score, education_score) -> Dict[str, str]:
        """詳細分析を生成"""
        analysis = {
            "skill_analysis": f"必須スキルマッチ度: {skill_score:.1f}% - ",
            "experience_analysis": f"経験年数評価: {experience_score:.1f}% - ",
            "culture_analysis": f"文化適合性: {culture_score:.1f}% - ",
            "education_analysis": f"学歴要件: {education_score:.1f}% - "
        }
        
        # スキル分析詳細
        matched_skills = [skill for skill in job_req.required_skills if skill in candidate.skills]
        if matched_skills:
            analysis["skill_analysis"] += f"適合スキル: {', '.join(matched_skills)}"
        else:
            analysis["skill_analysis"] += "適合する必須スキルが不足"
        
        # 経験分析詳細
        if candidate.experience_years >= job_req.required_years:
            analysis["experience_analysis"] += "経験年数は要件を満たしています"
        else:
            shortage = job_req.required_years - candidate.experience_years
            analysis["experience_analysis"] += f"経験年数が{shortage}年不足"
        
        return analysis
    
    def _make_recommendation(self, overall_score: float) -> str:
        """総合スコアに基づく推薦判定"""
        if overall_score >= 80:
            return "pass"  # 面接パス
        elif overall_score >= 60:
            return "interview"  # 面接実施
        else:
            return "reject"  # 不採用
    
    def _identify_interview_focus_areas(self, candidate: CandidateProfile, job_req: JobRequirement, skill_score: float, experience_score: float) -> List[str]:
        """面接で重点的に確認すべき分野を特定"""
        focus_areas = []
        
        if skill_score < 70:
            focus_areas.append("技術スキル・専門知識")
        
        if experience_score < 70:
            focus_areas.append("実務経験・プロジェクト実績")
        
        # 必ず確認すべき項目
        focus_areas.extend([
            "コミュニケーション能力",
            "チームワーク・協調性",
            "問題解決能力"
        ])
        
        return focus_areas

def main():
    """メイン処理"""
    logger.info("AI採用支援システムを起動しています...")
    
    # サンプル企業プロファイル
    company = CompanyProfile(
        company_name="株式会社テックイノベーション",
        mission="テクノロジーで社会課題を解決する",
        vision="持続可能な未来を創造するリーディングカンパニー",
        values=["革新性", "協調性", "社会貢献", "継続学習"],
        culture_keywords=["フラット", "自由", "成長志向", "多様性"],
        work_style=["リモートワーク", "フレックスタイム", "副業OK"]
    )
    
    # サンプル求人要件
    job_req = JobRequirement(
        position_title="Webエンジニア",
        department="開発部",
        required_skills=["Python", "JavaScript", "React"],
        preferred_skills=["Docker", "AWS", "チーム管理"],
        experience_level="mid",
        required_years=3,
        education_level="大学",
        salary_range=(500, 800),
        employment_type="full-time",
        remote_work=True,
        travel_required=False
    )
    
    # 履歴書分析システム初期化
    analyzer = ResumeAnalyzer()
    matcher = CandidateMatcher(company)
    
    # サンプル履歴書テキスト
    sample_resume = """
    氏名: 田中 太郎
    Email: tanaka@example.com
    電話: 090-1234-5678
    
    【職歴】
    2019年4月 - 2023年3月: 株式会社ABC システム開発部
    - Python、JavaScriptを使用したWebアプリケーション開発
    - Reactを使用したフロントエンド開発
    - チーム5名のプロジェクトリーダーを担当
    
    【スキル】
    - プログラミング: Python, JavaScript, React, Node.js
    - データベース: MySQL, PostgreSQL
    - インフラ: AWS, Docker
    - 言語: 英語（TOEIC 750点）
    
    【学歴】
    2015年3月 東京大学 工学部 情報工学科 卒業
    
    【資格】
    - 基本情報技術者
    - AWS認定ソリューションアーキテクト
    """
    
    # 候補者プロファイル抽出
    candidate = analyzer.extract_candidate_profile(sample_resume)
    logger.info(f"候補者プロファイル抽出完了: {candidate.name}")
    
    # マッチング分析実行
    matching_result = matcher.calculate_match_score(candidate, job_req)
    
    # 結果表示
    print("\n" + "="*50)
    print("AI採用支援システム - 分析結果")
    print("="*50)
    print(f"候補者名: {matching_result.candidate_name}")
    print(f"総合スコア: {matching_result.overall_score:.1f}点")
    print(f"推薦判定: {matching_result.recommendation}")
    print("\n【詳細スコア】")
    print(f"スキルマッチ: {matching_result.skill_match_score:.1f}点")
    print(f"経験マッチ: {matching_result.experience_match_score:.1f}点")
    print(f"文化適合性: {matching_result.culture_fit_score:.1f}点")
    print(f"学歴マッチ: {matching_result.education_match_score:.1f}点")
    print("\n【面接重点分野】")
    for area in matching_result.interview_focus_areas:
        print(f"・{area}")
    
    logger.info("分析処理が完了しました")

if __name__ == "__main__":
    main()

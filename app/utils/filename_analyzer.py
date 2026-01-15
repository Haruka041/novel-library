"""
文件名模式分析器
用于分析书库中的文件命名模式，自动识别和建议解析规则
"""
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.utils.logger import log


class FilenameAnalyzer:
    """文件名模式分析器"""
    
    # 常见分隔符
    SEPARATORS = ['-', '_', '—', '–', ' - ', ' _ ']
    
    # 常见括号对
    BRACKETS = [
        ('(', ')'),
        ('[', ']'),
        ('【', '】'),
        ('《', '》'),
        ('{', '}'),
    ]
    
    def __init__(self):
        self.filenames: List[str] = []
        self.patterns: Dict[str, List[str]] = defaultdict(list)
        self.separator_stats: Counter = Counter()
        self.bracket_stats: Counter = Counter()
        
    def analyze_files(self, file_paths: List[Path]) -> Dict:
        """
        分析文件列表
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            分析结果字典
        """
        self.filenames = [fp.name for fp in file_paths if fp.suffix.lower() == '.txt']
        
        if not self.filenames:
            return {
                "total_files": 0,
                "error": "没有找到 TXT 文件"
            }
        
        log.info(f"开始分析 {len(self.filenames)} 个文件名")
        
        # 统计分隔符
        self._analyze_separators()
        
        # 统计括号
        self._analyze_brackets()
        
        # 检测模式
        self._detect_patterns()
        
        # 生成报告
        report = self._generate_report()
        
        log.info(f"文件名分析完成，识别出 {len(self.patterns)} 种模式")
        
        return report
    
    def _analyze_separators(self):
        """统计分隔符使用情况"""
        for filename in self.filenames:
            for sep in self.SEPARATORS:
                if sep in filename:
                    self.separator_stats[sep] += 1
    
    def _analyze_brackets(self):
        """统计括号使用情况"""
        for filename in self.filenames:
            for left, right in self.BRACKETS:
                if left in filename and right in filename:
                    self.bracket_stats[f"{left}{right}"] += 1
    
    def _detect_patterns(self):
        """检测文件名模式"""
        for filename in self.filenames:
            # 移除扩展名
            name_without_ext = filename.rsplit('.', 1)[0]
            
            # 检测各种模式
            patterns_found = []
            
            # 模式1: 作者-书名
            for sep in self.SEPARATORS:
                if sep in name_without_ext:
                    parts = name_without_ext.split(sep, 1)
                    if len(parts) == 2:
                        pattern_key = f"作者{sep}书名"
                        patterns_found.append(pattern_key)
                        self.patterns[pattern_key].append(filename)
                        break
            
            # 模式2: [作者]书名 或 【作者】书名
            for left, right in self.BRACKETS:
                pattern = f"\\{left}(.+?)\\{right}(.+)"
                if re.match(pattern, name_without_ext):
                    pattern_key = f"{left}作者{right}书名"
                    patterns_found.append(pattern_key)
                    self.patterns[pattern_key].append(filename)
                    break
            
            # 模式3: 作者《书名》
            if '《' in name_without_ext and '》' in name_without_ext:
                pattern_key = "作者《书名》"
                patterns_found.append(pattern_key)
                self.patterns[pattern_key].append(filename)
            
            # 模式4: 书名(作者)
            for left, right in [('(', ')'), ('（', '）')]:
                if left in name_without_ext and right in name_without_ext:
                    # 检查括号是否在末尾附近
                    if name_without_ext.rindex(right) > len(name_without_ext) * 0.6:
                        pattern_key = f"书名{left}作者{right}"
                        patterns_found.append(pattern_key)
                        self.patterns[pattern_key].append(filename)
                        break
            
            # 如果没有匹配任何已知模式，记录为未知
            if not patterns_found:
                self.patterns["未知模式"].append(filename)
    
    def _generate_report(self) -> Dict:
        """生成分析报告"""
        total_files = len(self.filenames)
        
        # 统计模式
        pattern_stats = []
        for pattern, examples in sorted(
            self.patterns.items(),
            key=lambda x: len(x[1]),
            reverse=True
        ):
            count = len(examples)
            percentage = (count / total_files) * 100
            
            # 生成建议的正则表达式
            suggested_regex = self._suggest_regex(pattern)
            
            pattern_stats.append({
                "pattern": pattern,
                "count": count,
                "percentage": round(percentage, 2),
                "examples": examples[:5],  # 只展示前5个例子
                "suggested_regex": suggested_regex
            })
        
        # 分隔符统计
        separator_stats = [
            {
                "separator": sep,
                "count": count,
                "percentage": round((count / total_files) * 100, 2)
            }
            for sep, count in self.separator_stats.most_common()
        ]
        
        # 括号统计
        bracket_stats = [
            {
                "bracket": bracket,
                "count": count,
                "percentage": round((count / total_files) * 100, 2)
            }
            for bracket, count in self.bracket_stats.most_common()
        ]
        
        return {
            "total_files": total_files,
            "patterns_detected": pattern_stats,
            "separator_usage": separator_stats,
            "bracket_usage": bracket_stats,
            "coverage": round(
                ((total_files - len(self.patterns.get("未知模式", []))) / total_files) * 100,
                2
            ) if total_files > 0 else 0
        }
    
    def analyze_filenames(self, filenames: List[str]) -> Dict:
        """
        分析文件名列表，返回分隔符和模式统计
        
        Args:
            filenames: 文件名字符串列表
            
        Returns:
            包含分析结果的字典
        """
        self.filenames = filenames
        
        # 统计分隔符
        self._analyze_separators()
        
        # 统计括号
        self._analyze_brackets()
        
        # 检测模式
        self._detect_patterns()
        
        # 准备返回结果
        total_files = len(filenames)
        
        # 分隔符统计
        separator_stats = {}
        for sep, count in self.separator_stats.most_common():
            percentage = (count / total_files) * 100 if total_files > 0 else 0
            separator_stats[sep] = {
                'count': count,
                'percentage': round(percentage, 2),
                'examples': [f for f in filenames if sep in f][:3]
            }
        
        # 括号统计
        bracket_stats = {}
        for bracket, count in self.bracket_stats.most_common():
            percentage = (count / total_files) * 100 if total_files > 0 else 0
            bracket_stats[bracket] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        # 模式统计
        pattern_stats = {}
        for pattern, examples in self.patterns.items():
            count = len(examples)
            percentage = (count / total_files) * 100 if total_files > 0 else 0
            pattern_stats[pattern] = {
                'count': count,
                'percentage': round(percentage, 2),
                'examples': examples[:3]
            }
        
        return {
            'total_files': total_files,
            'separators': separator_stats,
            'brackets': bracket_stats,
            'patterns': pattern_stats
        }
    
    def generate_pattern_suggestion(self, separator: str, stats: Dict) -> str:
        """
        基于分隔符和统计信息生成正则表达式建议
        
        Args:
            separator: 分隔符字符串
            stats: 统计信息字典
            
        Returns:
            建议的正则表达式
        """
        # 转义特殊字符
        escaped_sep = re.escape(separator)
        
        # 生成通用的模式
        return f"^(.+?){escaped_sep}(.+?)\\.(txt|epub|mobi)$"
    
    def _suggest_regex(self, pattern: str) -> Optional[str]:
        """
        根据模式建议正则表达式
        
        Args:
            pattern: 模式描述
            
        Returns:
            建议的正则表达式
        """
        # 映射模式到正则表达式
        regex_map = {
            "作者-书名": r"^(.+?)[-](.+?)\.txt$",
            "作者_书名": r"^(.+?)[_](.+?)\.txt$",
            "作者—书名": r"^(.+?)[—](.+?)\.txt$",
            "作者–书名": r"^(.+?)[–](.+?)\.txt$",
            "作者 - 书名": r"^(.+?) - (.+?)\.txt$",
            "作者 _ 书名": r"^(.+?) _ (.+?)\.txt$",
            "[作者]书名": r"^\[(.+?)\](.+?)\.txt$",
            "【作者】书名": r"^【(.+?)】(.+?)\.txt$",
            "作者《书名》": r"^(.+?)《(.+?)》\.txt$",
            "书名(作者)": r"^(.+?)\((.+?)\)\.txt$",
            "书名（作者）": r"^(.+?)（(.+?)）\.txt$",
            "(作者)书名": r"^\((.+?)\)(.+?)\.txt$",
            "（作者）书名": r"^（(.+?)）(.+?)\.txt$",
            "{作者}书名": r"^\{(.+?)\}(.+?)\.txt$",
        }
        
        return regex_map.get(pattern)
    
    def generate_parser_code(self, patterns: List[Dict]) -> str:
        """
        生成解析器代码
        
        Args:
            patterns: 模式列表
            
        Returns:
            Python 代码字符串
        """
        code_lines = [
            "# 自动生成的文件名解析规则",
            "# 基于文件名模式分析结果",
            "",
            "PATTERNS = ["
        ]
        
        for pattern_info in patterns:
            if pattern_info["pattern"] == "未知模式":
                continue
            
            regex = pattern_info["suggested_regex"]
            if not regex:
                continue
            
            # 判断作者和书名的位置
            if pattern_info["pattern"].startswith("书名"):
                # 书名在前，作者在后
                author_group = 2
                title_group = 1
            else:
                # 作者在前，书名在后
                author_group = 1
                title_group = 2
            
            comment = f"    # {pattern_info['pattern']} ({pattern_info['count']}个文件，{pattern_info['percentage']}%)"
            pattern_line = f"    (r'{regex}', {author_group}, {title_group}),"
            
            code_lines.append(comment)
            code_lines.append(pattern_line)
        
        code_lines.append("]")
        
        return "\n".join(code_lines)


def analyze_library_filenames(library_path: Path) -> Dict:
    """
    分析书库中的文件名模式
    
    Args:
        library_path: 书库路径
        
    Returns:
        分析报告字典
    """
    analyzer = FilenameAnalyzer()
    
    # 收集所有 TXT 文件
    txt_files = list(library_path.rglob("*.txt"))
    
    if not txt_files:
        log.warning(f"在 {library_path} 中没有找到 TXT 文件")
        return {
            "total_files": 0,
            "error": "没有找到 TXT 文件"
        }
    
    # 分析文件名
    report = analyzer.analyze_files(txt_files)
    
    return report


def generate_analysis_report(library_path: Path, output_path: Optional[Path] = None) -> str:
    """
    生成详细的分析报告
    
    Args:
        library_path: 书库路径
        output_path: 输出文件路径（可选）
        
    Returns:
        报告文本
    """
    report = analyze_library_filenames(library_path)
    
    # 生成文本报告
    lines = [
        "=" * 80,
        f"文件名模式分析报告",
        f"书库路径: {library_path}",
        "=" * 80,
        "",
        f"总文件数: {report.get('total_files', 0)}",
        f"模式覆盖率: {report.get('coverage', 0)}%",
        "",
        "=" * 80,
        "检测到的模式:",
        "=" * 80,
    ]
    
    for pattern in report.get('patterns_detected', []):
        lines.append("")
        lines.append(f"模式: {pattern['pattern']}")
        lines.append(f"  数量: {pattern['count']} ({pattern['percentage']}%)")
        lines.append(f"  正则: {pattern.get('suggested_regex', 'N/A')}")
        lines.append(f"  示例:")
        for example in pattern['examples']:
            lines.append(f"    - {example}")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("分隔符使用统计:")
    lines.append("=" * 80)
    
    for sep_stat in report.get('separator_usage', []):
        lines.append(f"  '{sep_stat['separator']}': {sep_stat['count']} ({sep_stat['percentage']}%)")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("括号使用统计:")
    lines.append("=" * 80)
    
    for bracket_stat in report.get('bracket_usage', []):
        lines.append(f"  {bracket_stat['bracket']}: {bracket_stat['count']} ({bracket_stat['percentage']}%)")
    
    report_text = "\n".join(lines)
    
    # 如果指定了输出路径，保存报告
    if output_path:
        output_path.write_text(report_text, encoding='utf-8')
        log.info(f"分析报告已保存到: {output_path}")
    
    return report_text

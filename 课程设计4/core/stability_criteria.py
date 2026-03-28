# ============================================================
# core/stability_criteria.py 鈥?瑙勮寖鑷姩鍒ゅ畾妯″潡
#
# 闃舵6 鏂板妯″潡
#
# 涓ユ牸閬靛惊锛?#   銆婂浗鍐呰埅琛屾捣鑸规硶瀹氭楠屾妧鏈鍒欙紙2020锛夈€?#   绗?绡?鑸硅埗绋虫€?#   绗?绔?鍥藉唴鑸娴疯埞绋虫€ц　鍑?#
# 鍔熻兘锛?#   1. 鑷姩鍒ゅ畾宸ュ喌绋虫€ф槸鍚﹀悎鏍?#   2. 缁欏嚭鏄庣‘鐨勫悎鏍?涓嶅悎鏍肩粨璁?#   3. 鏍囨敞涓嶆弧瓒抽」鍙婂搴旇鑼冩潯娆?#
# 鈹€鈹€ 瑙勮寖瑕佹眰锛堟墍鏈夊伐鍐甸€氱敤锛夆攢鈹€
#   1. 鍒濈ǔ鎬ч珮搴?GM 鈮?0.15m锛堣鍒欑4绡囩3绔?.1.1鏉★級
#   2. 鏈€澶ч潤绋虫€у姏鑷?GZ_max 鈮?0.20m锛堣鍒欑4绡囩3绔?.1.2鏉★級
#   3. 鏈€澶ч潤绋虫€у姏鑷傚搴旂殑妯€捐 胃_max_gz 鈮?25掳
#   4. 绋虫€ф秷澶辫 胃_vanish 鈮?55掳
#   5. 绋虫€ц　鍑嗘暟 K 鈮?1.0
#   6. 鑻ヨ繘姘磋 胃_f < 胃_max_gz 鎴?胃_vanish锛屽垯浠ヨ繘姘磋涓轰笂闄?#
# ============================================================

from typing import Dict, List, Tuple, Optional

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 瑙勮寖鏍囧噯瀹氫箟
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

class StabilityCriteria:
    """绋虫€ц　鍑嗘爣鍑嗭紙銆婂浗鍐呰埅琛屾捣鑸规硶瀹氭楠屾妧鏈鍒?2020銆嬶級"""
    
    # 瑙勮寖鏉℃寮曠敤
    RULE_REFERENCE = {
        'GM': '瑙勫垯绗?绡囩3绔?.1.1鏉?,
        'GZ_max': '瑙勫垯绗?绡囩3绔?.1.2鏉?,
        'theta_max_gz': '瑙勫垯绗?绡囩3绔?.1.3鏉?,
        'theta_vanish': '瑙勫垯绗?绡囩3绔?.1.4鏉?,
        'K': '瑙勫垯绗?绡囩3绔?.1.5鏉?
    }
    
    # 琛″噯鏍囧噯鍊?    CRITERIA = {
        'GM_min': 0.15,              # m锛屽垵绋虫€ч珮搴︽渶灏忓€?        'GZ_max_min': 0.20,          # m锛屾渶澶у鍘熷姏鑷傛渶灏忓€?        'theta_max_gz_min': 25.0,    # 掳锛屾渶澶у鍘熷姏鑷傝搴︽渶灏忓€?        'theta_vanish_min': 55.0,    # 掳锛岀ǔ鎬ф秷澶辫鏈€灏忓€?        'K_min': 1.0                 # 绋虫€ц　鍑嗘暟鏈€灏忓€?    }
    
    # 琛″噯椤瑰悕绉颁笌鎻忚堪
    CRITERIA_NAMES = {
        'GM': '鍒濈ǔ鎬ч珮搴?,
        'GZ_max': '鏈€澶у鍘熷姏鑷?,
        'theta_max_gz': '鏈€澶у鍘熷姏鑷傝搴?,
        'theta_vanish': '绋虫€ф秷澶辫',
        'K': '绋虫€ц　鍑嗘暟'
    }
    
    CRITERIA_UNITS = {
        'GM': 'm',
        'GZ_max': 'm',
        'theta_max_gz': '掳',
        'theta_vanish': '掳',
        'K': '-'
    }


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 瑙勮寖鍒ゅ畾
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

class StabilityJudgment:
    """绋虫€ц鑼冨垽瀹氱被"""
    
    def __init__(self, stability_result: Dict):
        """
        鍒濆鍖栬鑼冨垽瀹?        
        鍙傛暟锛?            stability_result: 绋虫€ц绠楃粨鏋滐紙鏉ヨ嚜 LoadingConditionStability锛?        """
        self.stability_result = stability_result
        self.judgments = {}  # 鍚勮　鍑嗛」鐨勫垽瀹氱粨鏋?        self.overall_pass = True  # 鎬讳綋鏄惁閫氳繃
        self.failed_items = []  # 涓嶆弧瓒崇殑椤?    
    def judge_gm(self, gm: float) -> Tuple[bool, str]:
        """
        鍒ゅ畾鍒濈ǔ鎬ч珮搴?GM
        
        鍙傛暟锛?            gm: 鍒濈ǔ鎬ч珮搴︼紙m锛?        
        杩斿洖锛?            (鏄惁閫氳繃, 璇存槑鏂囧瓧)
        """
        criteria_name = StabilityCriteria.CRITERIA_NAMES['GM']
        criteria_unit = StabilityCriteria.CRITERIA_UNITS['GM']
        min_value = StabilityCriteria.CRITERIA['GM_min']
        rule_ref = StabilityCriteria.RULE_REFERENCE['GM']
        
        passed = gm >= min_value
        
        if passed:
            msg = f'鉁?{criteria_name}: {gm:.4f}{criteria_unit} 鈮?{min_value}{criteria_unit} 銆愰€氳繃銆?
        else:
            msg = f'鉁?{criteria_name}: {gm:.4f}{criteria_unit} < {min_value}{criteria_unit} 銆愪笉閫氳繃銆?
            msg += f'\n  瑙勮寖鏉℃: {rule_ref}'
            msg += f'\n  瑕佹眰: {criteria_name} 鈮?{min_value}{criteria_unit}'
        
        self.judgments['GM'] = {
            'passed': passed,
            'value': gm,
            'limit': min_value,
            'unit': criteria_unit,
            'rule': rule_ref
        }
        
        if not passed:
            self.failed_items.append('GM')
        
        return passed, msg
    
    def judge_gz_max(self, gz_max: float) -> Tuple[bool, str]:
        """
        鍒ゅ畾鏈€澶у鍘熷姏鑷?GZ_max
        
        鍙傛暟锛?            gz_max: 鏈€澶у鍘熷姏鑷傦紙m锛?        
        杩斿洖锛?            (鏄惁閫氳繃, 璇存槑鏂囧瓧)
        """
        criteria_name = StabilityCriteria.CRITERIA_NAMES['GZ_max']
        criteria_unit = StabilityCriteria.CRITERIA_UNITS['GZ_max']
        min_value = StabilityCriteria.CRITERIA['GZ_max_min']
        rule_ref = StabilityCriteria.RULE_REFERENCE['GZ_max']
        
        passed = gz_max >= min_value
        
        if passed:
            msg = f'鉁?{criteria_name}: {gz_max:.4f}{criteria_unit} 鈮?{min_value}{criteria_unit} 銆愰€氳繃銆?
        else:
            msg = f'鉁?{criteria_name}: {gz_max:.4f}{criteria_unit} < {min_value}{criteria_unit} 銆愪笉閫氳繃銆?
            msg += f'\n  瑙勮寖鏉℃: {rule_ref}'
            msg += f'\n  瑕佹眰: {criteria_name} 鈮?{min_value}{criteria_unit}'
        
        self.judgments['GZ_max'] = {
            'passed': passed,
            'value': gz_max,
            'limit': min_value,
            'unit': criteria_unit,
            'rule': rule_ref
        }
        
        if not passed:
            self.failed_items.append('GZ_max')
        
        return passed, msg
    
    def judge_theta_max_gz(self, theta_max_gz: float) -> Tuple[bool, str]:
        """
        鍒ゅ畾鏈€澶у鍘熷姏鑷傝搴?胃_max_gz
        
        鍙傛暟锛?            theta_max_gz: 鏈€澶у鍘熷姏鑷傚搴旂殑妯€捐锛埪帮級
        
        杩斿洖锛?            (鏄惁閫氳繃, 璇存槑鏂囧瓧)
        """
        criteria_name = StabilityCriteria.CRITERIA_NAMES['theta_max_gz']
        criteria_unit = StabilityCriteria.CRITERIA_UNITS['theta_max_gz']
        min_value = StabilityCriteria.CRITERIA['theta_max_gz_min']
        rule_ref = StabilityCriteria.RULE_REFERENCE['theta_max_gz']
        
        passed = theta_max_gz >= min_value
        
        if passed:
            msg = f'鉁?{criteria_name}: {theta_max_gz:.1f}{criteria_unit} 鈮?{min_value}{criteria_unit} 銆愰€氳繃銆?
        else:
            msg = f'鉁?{criteria_name}: {theta_max_gz:.1f}{criteria_unit} < {min_value}{criteria_unit} 銆愪笉閫氳繃銆?
            msg += f'\n  瑙勮寖鏉℃: {rule_ref}'
            msg += f'\n  瑕佹眰: {criteria_name} 鈮?{min_value}{criteria_unit}'
        
        self.judgments['theta_max_gz'] = {
            'passed': passed,
            'value': theta_max_gz,
            'limit': min_value,
            'unit': criteria_unit,
            'rule': rule_ref
        }
        
        if not passed:
            self.failed_items.append('theta_max_gz')
        
        return passed, msg
    
    def judge_theta_vanish(self, theta_vanish: float) -> Tuple[bool, str]:
        """
        鍒ゅ畾绋虫€ф秷澶辫 胃_vanish
        
        鍙傛暟锛?            theta_vanish: 绋虫€ф秷澶辫锛埪帮級
        
        杩斿洖锛?            (鏄惁閫氳繃, 璇存槑鏂囧瓧)
        """
        criteria_name = StabilityCriteria.CRITERIA_NAMES['theta_vanish']
        criteria_unit = StabilityCriteria.CRITERIA_UNITS['theta_vanish']
        min_value = StabilityCriteria.CRITERIA['theta_vanish_min']
        rule_ref = StabilityCriteria.RULE_REFERENCE['theta_vanish']
        
        passed = theta_vanish >= min_value
        
        if passed:
            msg = f'鉁?{criteria_name}: {theta_vanish:.1f}{criteria_unit} 鈮?{min_value}{criteria_unit} 銆愰€氳繃銆?
        else:
            msg = f'鉁?{criteria_name}: {theta_vanish:.1f}{criteria_unit} < {min_value}{criteria_unit} 銆愪笉閫氳繃銆?
            msg += f'\n  瑙勮寖鏉℃: {rule_ref}'
            msg += f'\n  瑕佹眰: {criteria_name} 鈮?{min_value}{criteria_unit}'
        
        self.judgments['theta_vanish'] = {
            'passed': passed,
            'value': theta_vanish,
            'limit': min_value,
            'unit': criteria_unit,
            'rule': rule_ref
        }
        
        if not passed:
            self.failed_items.append('theta_vanish')
        
        return passed, msg
    
    def judge_k_value(self, k_value: float) -> Tuple[bool, str]:
        """
        鍒ゅ畾绋虫€ц　鍑嗘暟 K
        
        鍙傛暟锛?            k_value: 绋虫€ц　鍑嗘暟
        
        杩斿洖锛?            (鏄惁閫氳繃, 璇存槑鏂囧瓧)
        """
        criteria_name = StabilityCriteria.CRITERIA_NAMES['K']
        criteria_unit = StabilityCriteria.CRITERIA_UNITS['K']
        min_value = StabilityCriteria.CRITERIA['K_min']
        rule_ref = StabilityCriteria.RULE_REFERENCE['K']
        
        passed = k_value >= min_value
        
        if passed:
            msg = f'鉁?{criteria_name}: {k_value:.4f}{criteria_unit} 鈮?{min_value}{criteria_unit} 銆愰€氳繃銆?
        else:
            msg = f'鉁?{criteria_name}: {k_value:.4f}{criteria_unit} < {min_value}{criteria_unit} 銆愪笉閫氳繃銆?
            msg += f'\n  瑙勮寖鏉℃: {rule_ref}'
            msg += f'\n  瑕佹眰: {criteria_name} 鈮?{min_value}{criteria_unit}'
        
        self.judgments['K'] = {
            'passed': passed,
            'value': k_value,
            'limit': min_value,
            'unit': criteria_unit,
            'rule': rule_ref
        }
        
        if not passed:
            self.failed_items.append('K')
        
        return passed, msg
    
    def judge_all(self) -> Dict:
        """
        瀵规墍鏈夎　鍑嗛」杩涜鍒ゅ畾
        
        杩斿洖锛?            鍒ゅ畾缁撴灉瀛楀吀
        """
        # 浠庣ǔ鎬ц绠楃粨鏋滀腑鎻愬彇鏁版嵁
        indicators = self.stability_result.get('indicators', {})
        gz_result = self.stability_result.get('gz_curve', {})
        
        gm = gz_result.get('GM', 0.0)
        gz_max = indicators.get('GZ_max', 0.0)
        theta_max_gz = indicators.get('theta_max_gz', 0.0)
        theta_vanish = indicators.get('theta_vanish', 0.0)
        k_value = indicators.get('K', 0.0)
        
        # 閫愰」鍒ゅ畾
        self.judge_gm(gm)
        self.judge_gz_max(gz_max)
        self.judge_theta_max_gz(theta_max_gz)
        self.judge_theta_vanish(theta_vanish)
        self.judge_k_value(k_value)
        
        # 鎬讳綋鍒ゅ畾
        self.overall_pass = len(self.failed_items) == 0
        
        return {
            'condition_name': self.stability_result.get('condition_name', ''),
            'overall_pass': self.overall_pass,
            'judgments': self.judgments,
            'failed_items': self.failed_items,
            'indicators': {
                'GM': gm,
                'GZ_max': gz_max,
                'theta_max_gz': theta_max_gz,
                'theta_vanish': theta_vanish,
                'K': k_value
            }
        }
    
    def get_report(self) -> str:
        """
        鐢熸垚瑙勮寖鍒ゅ畾鎶ュ憡
        
        杩斿洖锛?            鎶ュ憡鏂囨湰
        """
        report = []
        report.append('=' * 70)
        report.append(f'銆愮ǔ鎬ц鑼冨垽瀹氭姤鍛娿€戔€?{self.stability_result.get("condition_name", "")}')
        report.append('=' * 70)
        report.append('')
        
        # 鎬讳綋缁撹
        if self.overall_pass:
            report.append('銆愭€讳綋缁撹銆戔湏 绋虫€у悎鏍?)
        else:
            report.append('銆愭€讳綋缁撹銆戔湕 绋虫€т笉鍚堟牸')
            report.append(f'涓嶆弧瓒抽」: {", ".join(self.failed_items)}')
        
        report.append('')
        report.append('銆愯缁嗗垽瀹氥€?)
        report.append('-' * 70)
        
        # 鍚勮　鍑嗛」鍒ゅ畾
        for key in ['GM', 'GZ_max', 'theta_max_gz', 'theta_vanish', 'K']:
            if key in self.judgments:
                judgment = self.judgments[key]
                status = '鉁?閫氳繃' if judgment['passed'] else '鉁?涓嶉€氳繃'
                report.append(f'{StabilityCriteria.CRITERIA_NAMES[key]}: {judgment["value"]:.4f} {judgment["unit"]} 鈮?{judgment["limit"]} {status}')
                if not judgment['passed']:
                    report.append(f'  瑙勮寖鏉℃: {judgment["rule"]}')
        
        report.append('')
        report.append('=' * 70)
        
        return '\n'.join(report)


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 娴嬭瘯鍑芥暟
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

if __name__ == '__main__':
    import sys
    try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
    
    print('=' * 70)
    print('瑙勮寖鑷姩鍒ゅ畾妯″潡娴嬭瘯')
    print('=' * 70)
    
    # 妯℃嫙绋虫€ц绠楃粨鏋?    mock_result = {
        'condition_name': '婊¤浇鍑烘腐',
        'indicators': {
            'GZ_max': 0.42,
            'theta_max_gz': 30.0,
            'theta_vanish': 85.0,
            'K': 1.2
        },
        'gz_curve': {
            'GM': 0.8234
        }
    }
    
    # 鍒涘缓鍒ゅ畾鍣?    judgment = StabilityJudgment(mock_result)
    result = judgment.judge_all()
    
    # 杈撳嚭鎶ュ憡
    print(judgment.get_report())
    
    print('\n鉁?瑙勮寖鑷姩鍒ゅ畾妯″潡娴嬭瘯閫氳繃!')


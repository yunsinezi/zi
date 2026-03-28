# ============================================================
# core/floating_stability.py 鈥?娴€佷笌绋虫€ц绠楁ā鍧?#
# 闃舵6 鏂板妯″潡
#
# 鍔熻兘锛?#   1. 鍩轰簬瑁呰浇宸ュ喌璁＄畻娴€侊紙鍚冩按銆佸悆姘村樊銆佹í鍊捐锛?#   2. 璁＄畻鍒濈ǔ鎬ч珮搴?GM
#   3. 鍩轰簬 GZ 鏇茬嚎璁＄畻闈欑ǔ鎬ф洸绾?#   4. 璁＄畻琛″噯鎸囨爣锛圙Z_max銆佄竉max_gz銆佄竉vanish銆並 鍊硷級
#
# 鈹€鈹€ 娴€佽绠楁柟娉?鈹€鈹€
#   浣跨敤杩唬娉曟眰瑙ｅ悆姘达紝浣垮緱鎺掓按閲忕瓑浜庤杞藉伐鍐垫€婚噸閲?#   鍩轰簬闈欐按鍔涜〃锛堟垨 Bonjean 鏇茬嚎锛夎繘琛屾彃鍊?#
# 鈹€鈹€ 绋虫€ц绠楁柟娉?鈹€鈹€
#   鍩轰簬闃舵5鐨?GZ 鏇茬嚎璁＄畻缁撴灉
#   鎻愬彇璇ュ伐鍐靛搴旂殑闈欑ǔ鎬ф洸绾?#
# ============================================================

import numpy as np
from typing import Dict, Tuple, Optional, List
from scipy.interpolate import interp1d

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 娴€佽绠?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

class FloatingCondition:
    """娴€佽绠楃被"""
    
    def __init__(self, offsets_data: Dict, hydrostatics_table: Dict):
        """
        鍒濆鍖栨诞鎬佽绠?        
        鍙傛暟锛?            offsets_data: 鍨嬪€艰〃鏁版嵁 {stations, waterlines, offsets}
            hydrostatics_table: 闈欐按鍔涜〃 {drafts, volumes, ...}
        """
        self.offsets_data = offsets_data
        self.hydrostatics_table = hydrostatics_table
        
        # 浠庨潤姘村姏琛ㄦ彁鍙栨帓姘撮噺-鍚冩按鍏崇郴
        self.drafts = np.array(hydrostatics_table.get('drafts', []))
        self.volumes = np.array(hydrostatics_table.get('volumes', []))
        
        # 鍒涘缓鎺掓按閲忔彃鍊煎嚱鏁?        if len(self.drafts) > 1:
            self.volume_interp = interp1d(
                self.drafts, self.volumes,
                kind='cubic', fill_value='extrapolate'
            )
        else:
            self.volume_interp = None
    
    def calculate_draft_from_weight(self, total_weight: float, 
                                   rho: float = 1.025,
                                   tolerance: float = 0.01) -> float:
        """
        鏍规嵁鎬婚噸閲忚绠楀悆姘达紙杩唬娉曪級
        
        鍙傛暟锛?            total_weight: 鍏ㄨ埞鎬婚噸閲忥紙t锛?            rho: 姘村瘑搴︼紙t/m鲁锛?            tolerance: 鏀舵暃绮惧害锛坢鲁锛?        
        杩斿洖锛?            鍚冩按锛坢锛?        """
        # 鐩爣鎺掓按閲忥紙m鲁锛?        target_volume = total_weight / rho
        
        # 浜屽垎娉曟眰瑙ｅ悆姘?        d_min = self.drafts[0]
        d_max = self.drafts[-1]
        
        for iteration in range(100):
            d_mid = (d_min + d_max) / 2
            
            # 璁＄畻涓偣瀵瑰簲鐨勬帓姘撮噺
            if self.volume_interp is not None:
                v_mid = float(self.volume_interp(d_mid))
            else:
                # 绾挎€ф彃鍊?                idx = np.searchsorted(self.drafts, d_mid)
                if idx == 0:
                    v_mid = self.volumes[0]
                elif idx >= len(self.drafts):
                    v_mid = self.volumes[-1]
                else:
                    w = (d_mid - self.drafts[idx-1]) / (self.drafts[idx] - self.drafts[idx-1])
                    v_mid = self.volumes[idx-1] + w * (self.volumes[idx] - self.volumes[idx-1])
            
            # 妫€鏌ユ敹鏁?            if abs(v_mid - target_volume) < tolerance:
                return d_mid
            
            # 璋冩暣鎼滅储鑼冨洿
            if v_mid < target_volume:
                d_min = d_mid
            else:
                d_max = d_mid
        
        # 鏈敹鏁涳紝杩斿洖鏈€鍚庣殑浼拌鍊?        return d_mid
    
    def calculate_floating_state(self, total_weight: float, xg: float, 
                                rho: float = 1.025) -> Dict:
        """
        璁＄畻娴€侊紙鍚冩按銆佸悆姘村樊銆佹í鍊捐绛夛級
        
        鍙傛暟锛?            total_weight: 鍏ㄨ埞鎬婚噸閲忥紙t锛?            xg: 鍏ㄨ埞閲嶅績绾靛悜鍧愭爣锛坢锛?            rho: 姘村瘑搴︼紙t/m鲁锛?        
        杩斿洖锛?            娴€佸瓧鍏?{draft, trim, heel, ...}
        """
        # 璁＄畻骞冲潎鍚冩按
        draft_mean = self.calculate_draft_from_weight(total_weight, rho)
        
        # 绠€鍖栧鐞嗭細鍋囪绾靛€惧拰妯€惧潎涓?0锛堣绋嬭璁￠€氬父涓嶈€冭檻锛?        # 瀹為檯搴旂敤涓渶瑕佸熀浜庨噸蹇冧綅缃繘琛屾洿澶嶆潅鐨勮绠?        trim = 0.0  # 绾靛€撅紙m锛?        heel = 0.0  # 妯€撅紙掳锛?        
        # 棣栧熬鍚冩按
        draft_fwd = draft_mean + trim / 2
        draft_aft = draft_mean - trim / 2
        
        return {
            'draft_mean': draft_mean,
            'draft_fwd': draft_fwd,
            'draft_aft': draft_aft,
            'trim': trim,
            'heel': heel,
            'displacement': total_weight
        }


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 绋虫€ф寚鏍囪绠?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

class StabilityIndicators:
    """绋虫€ф寚鏍囪绠楃被"""
    
    @staticmethod
    def calculate_from_gz_curve(gz_data: Dict) -> Dict:
        """
        浠?GZ 鏇茬嚎鏁版嵁璁＄畻绋虫€ф寚鏍?        
        鍙傛暟锛?            gz_data: GZ 鏇茬嚎鏁版嵁 {rows: [{theta, GZ, ...}, ...], ...}
        
        杩斿洖锛?            绋虫€ф寚鏍囧瓧鍏?        """
        rows = gz_data.get('rows', [])
        if not rows:
            return {}
        
        # 鎻愬彇鏁版嵁
        thetas = np.array([r['theta'] for r in rows])
        gzs = np.array([r['GZ'] for r in rows])
        
        # 璁＄畻 GZ_max 鍜屽搴旂殑瑙掑害
        max_idx = np.argmax(gzs)
        gz_max = float(gzs[max_idx])
        theta_max_gz = float(thetas[max_idx])
        
        # 璁＄畻绋虫€ф秷澶辫锛圙Z 鏈€鍚庝竴娆′负姝ｇ殑瑙掑害锛?        theta_vanish = None
        for i in range(len(gzs)-1, -1, -1):
            if gzs[i] > 0.001:  # 鑰冭檻鏁板€艰宸?                theta_vanish = float(thetas[i])
                break
        
        if theta_vanish is None:
            theta_vanish = 0.0
        
        # 璁＄畻鍔ㄧǔ鎬ц　鍑嗘暟 K
        # K = 鈭個鈦粹伆掳 GZ路d胃 / (GZ_max 路 胃_max_gz)
        # 鍏朵腑绉垎鍗曚綅涓哄姬搴?        
        # 鎻愬彇 0掳 ~ 40掳 鑼冨洿鍐呯殑鏁版嵁
        mask_40 = thetas <= 40
        thetas_40 = thetas[mask_40]
        gzs_40 = gzs[mask_40]
        
        # 姊舰绉垎锛堣浆鎹负寮у害锛?        if len(thetas_40) > 1:
            dtheta_rad = np.radians(thetas_40[1] - thetas_40[0])
            dynamic_stability = np.trapz(gzs_40, dx=dtheta_rad)
        else:
            dynamic_stability = 0.0
        
        # 璁＄畻 K 鍊?        if gz_max > 0 and theta_max_gz > 0:
            k_value = dynamic_stability / (gz_max * np.radians(theta_max_gz))
        else:
            k_value = 0.0
        
        return {
            'GZ_max': gz_max,
            'theta_max_gz': theta_max_gz,
            'theta_vanish': theta_vanish,
            'dynamic_stability': dynamic_stability,
            'K': k_value
        }
    
    @staticmethod
    def calculate_gm(kb: float, bm: float, kg: float) -> float:
        """
        璁＄畻鍒濈ǔ鎬ч珮搴?GM
        
        鍙傛暟锛?            kb: 娴績楂樺害锛坢锛?            bm: 妯ǔ蹇冨崐寰勶紙m锛?            kg: 閲嶅績楂樺害锛坢锛?        
        杩斿洖锛?            鍒濈ǔ鎬ч珮搴?GM锛坢锛?        """
        gm = kb + bm - kg
        return max(gm, 0.0)  # GM 涓嶈兘涓鸿礋


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 宸ュ喌绋虫€ц绠?# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

class LoadingConditionStability:
    """宸ュ喌绋虫€ц绠楃被"""
    
    def __init__(self, loading_condition, offsets_data: Dict, 
                 hydrostatics_table: Dict, gz_curve_func):
        """
        鍒濆鍖栧伐鍐电ǔ鎬ц绠?        
        鍙傛暟锛?            loading_condition: LoadingCondition 瀵硅薄
            offsets_data: 鍨嬪€艰〃鏁版嵁
            hydrostatics_table: 闈欐按鍔涜〃
            gz_curve_func: GZ 鏇茬嚎璁＄畻鍑芥暟锛堟潵鑷?core.stability锛?        """
        self.loading_condition = loading_condition
        self.offsets_data = offsets_data
        self.hydrostatics_table = hydrostatics_table
        self.gz_curve_func = gz_curve_func
        
        # 娴€佽绠?        self.floating = FloatingCondition(offsets_data, hydrostatics_table)
    
    def calculate_stability(self) -> Dict:
        """
        璁＄畻宸ュ喌绋虫€?        
        杩斿洖锛?            绋虫€ц绠楃粨鏋滃瓧鍏?        """
        lc = self.loading_condition
        
        # 1. 璁＄畻娴€?        floating_state = self.floating.calculate_floating_state(
            lc.total_weight, lc.xg
        )
        
        # 2. 璁＄畻 GZ 鏇茬嚎
        gz_result = self.gz_curve_func(
            offsets_data=self.offsets_data,
            draft=floating_state['draft_mean'],
            KG=lc.zg,
            theta_step=5.0
        )
        
        # 3. 璁＄畻绋虫€ф寚鏍?        indicators = StabilityIndicators.calculate_from_gz_curve(gz_result)
        
        # 4. 缁勫悎缁撴灉
        result = {
            'condition_name': lc.name,
            'condition_description': lc.description,
            'loading': {
                'total_weight': lc.total_weight,
                'xg': lc.xg,
                'yg': lc.yg,
                'zg': lc.zg
            },
            'floating_state': floating_state,
            'gz_curve': gz_result,
            'indicators': indicators
        }
        
        return result


# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 娴嬭瘯鍑芥暟
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

if __name__ == '__main__':
    import sys
    try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
    
    print('=' * 60)
    print('娴€佷笌绋虫€ц绠楁ā鍧楁祴璇?)
    print('=' * 60)
    
    # 绀轰緥闈欐按鍔涜〃锛堢畝鍖栵級
    hydrostatics_table = {
        'drafts': [2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        'volumes': [800, 1200, 1600, 2000, 2400, 2800]
    }
    
    # 鍒涘缓娴€佽绠楀櫒
    floating = FloatingCondition({}, hydrostatics_table)
    
    # 娴嬭瘯鍚冩按璁＄畻
    print('\n銆愬悆姘磋绠楁祴璇曘€?)
    for weight in [1000, 1500, 2000, 2500]:
        draft = floating.calculate_draft_from_weight(weight, rho=1.025)
        print(f'鎬婚噸閲?{weight}t 鈫?鍚冩按 {draft:.2f}m')
    
    print('\n鉁?娴€佷笌绋虫€ц绠楁ā鍧楁祴璇曢€氳繃!')


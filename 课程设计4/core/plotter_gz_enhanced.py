# ============================================================
# core/plotter_gz_enhanced.py 鈥?澧炲己鐨?GZ 鏇茬嚎缁樺埗妯″潡
#
# 闃舵6 绗簩浼樺厛绾?#
# 鍔熻兘锛?#   1. 缁樺埗楂樿川閲忕殑闈欑ǔ鎬ф洸绾?#   2. 鏍囨敞瑙勮寖瑕佹眰鐨勫叧閿壒寰佺偣
#   3. 鏀寔澶氱瀵煎嚭鏍煎紡锛圥NG銆丼VG锛?#   4. 绗﹀悎璇剧▼璁捐瑕佹眰
#
# ============================================================

import numpy as np
import matplotlib
matplotlib.use('Agg')
 as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle
import io
import base64
from typing import Dict, Tuple, Optional

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲
# 澧炲己鐨?GZ 鏇茬嚎缁樺埗
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲

class EnhancedGzPlotter:
    """澧炲己鐨?GZ 鏇茬嚎缁樺埗绫?""
    
    def __init__(self, figsize: Tuple[float, float] = (12, 8), dpi: int = 300):
        """
        鍒濆鍖栫粯鍥惧櫒
        
        鍙傛暟锛?            figsize: 鍥惧箙澶у皬锛堣嫳瀵革級
            dpi: 鍒嗚鲸鐜囷紙鐐?鑻卞锛?        """
        self.figsize = figsize
        self.dpi = dpi
        
        # 璁剧疆涓枃瀛椾綋
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_gz_curve_with_annotations(self, gz_data: Dict, 
                                      condition_name: str = '',
                                      theta_f: Optional[float] = None) -> Tuple:
        """
        缁樺埗甯︽爣娉ㄧ殑 GZ 鏇茬嚎
        
        鍙傛暟锛?            gz_data: GZ 鏇茬嚎鏁版嵁
            condition_name: 宸ュ喌鍚嶇О
            theta_f: 杩涙按瑙掞紙鍙€夛級
        
        杩斿洖锛?            (fig, ax) 鍥惧舰瀵硅薄
        """
        # 鍒涘缓鍥惧舰
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # 鎻愬彇鏁版嵁
        rows = gz_data.get('rows', [])
        if not rows:
            return fig, ax
        
        thetas = np.array([r['theta'] for r in rows])
        gzs = np.array([r['GZ'] for r in rows])
        
        # 缁樺埗 GZ 鏇茬嚎
        ax.plot(thetas, gzs, 'b-', linewidth=2.5, label='GZ 鏇茬嚎锛堢簿纭€硷級', zorder=3)
        
        # 缁樺埗缃戞牸
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # 鏍囨敞鍏抽敭鐐?        self._annotate_key_points(ax, gz_data, thetas, gzs, theta_f)
        
        # 鏍囨敞瑙勮寖瑕佹眰鐨勮　鍑嗙嚎
        self._annotate_criteria_lines(ax, gz_data)
        
        # 璁剧疆鍧愭爣杞?        ax.set_xlabel('妯€捐 胃 (掳)', fontsize=12, fontweight='bold')
        ax.set_ylabel('澶嶅師鍔涜噦 GZ (m)', fontsize=12, fontweight='bold')
        ax.set_title(f'闈欑ǔ鎬ф洸绾?鈥?{condition_name}', fontsize=14, fontweight='bold', pad=20)
        
        # 璁剧疆鍧愭爣杞磋寖鍥?        ax.set_xlim(0, 90)
        ax.set_ylim(min(0, np.min(gzs) - 0.05), np.max(gzs) + 0.1)
        
        # 娣诲姞鍥句緥
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95)
        
        # 娣诲姞瑙勮寖淇℃伅鏂囨湰妗?        self._add_criteria_textbox(ax, gz_data)
        
        # 璋冩暣甯冨眬
        fig.tight_layout()
        
        return fig, ax
    
    def _annotate_key_points(self, ax, gz_data: Dict, thetas: np.ndarray, 
                            gzs: np.ndarray, theta_f: Optional[float] = None):
        """鏍囨敞鍏抽敭鐗瑰緛鐐?""
        
        # 1. GZ_max 鐐?        gz_max = gz_data.get('GZ_max', 0)
        theta_max_gz = gz_data.get('theta_max_gz', 0)
        
        if gz_max > 0:
            ax.plot(theta_max_gz, gz_max, 'ro', markersize=10, zorder=5, label='GZ_max')
            ax.annotate(
                f'GZ_max = {gz_max:.3f}m\n胃 = {theta_max_gz:.1f}掳',
                xy=(theta_max_gz, gz_max),
                xytext=(theta_max_gz + 10, gz_max + 0.05),
                fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='red', lw=1.5)
            )
        
        # 2. 绋虫€ф秷澶辫 胃_vanish
        theta_vanish = gz_data.get('theta_vanish', 0)
        
        if theta_vanish > 0 and theta_vanish <= 90:
            # 鎵惧埌 胃_vanish 瀵瑰簲鐨?GZ 鍊硷紙搴旇鎺ヨ繎 0锛?            idx_vanish = np.argmin(np.abs(thetas - theta_vanish))
            gz_vanish = gzs[idx_vanish]
            
            ax.plot(theta_vanish, gz_vanish, 'gs', markersize=10, zorder=5, label='胃_vanish')
            ax.annotate(
                f'胃_vanish = {theta_vanish:.1f}掳',
                xy=(theta_vanish, gz_vanish),
                xytext=(theta_vanish - 15, gz_vanish + 0.05),
                fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='green', lw=1.5)
            )
        
        # 3. 杩涙按瑙?胃_f锛堝鏋滄湁锛?        if theta_f is not None and theta_f > 0:
            ax.axvline(x=theta_f, color='purple', linestyle='--', linewidth=2, alpha=0.7, label=f'杩涙按瑙?胃_f = {theta_f:.1f}掳')
    
    def _annotate_criteria_lines(self, ax, gz_data: Dict):
        """鏍囨敞瑙勮寖瑕佹眰鐨勮　鍑嗙嚎"""
        
        # GZ_max 鏈€灏忓€艰　鍑嗙嚎
        gz_max_min = 0.20
        ax.axhline(y=gz_max_min, color='orange', linestyle=':', linewidth=1.5, alpha=0.6)
        ax.text(2, gz_max_min + 0.01, f'GZ_max 鈮?{gz_max_min}m锛堣鑼冭姹傦級', 
               fontsize=9, color='orange', fontweight='bold')
    
    def _add_criteria_textbox(self, ax, gz_data: Dict):
        """娣诲姞瑙勮寖琛″噯淇℃伅鏂囨湰妗?""
        
        gm = gz_data.get('GM', 0)
        gz_max = gz_data.get('GZ_max', 0)
        theta_max_gz = gz_data.get('theta_max_gz', 0)
        theta_vanish = gz_data.get('theta_vanish', 0)
        k_value = gz_data.get('K', 0)
        
        # 鍒ゅ畾缁撴灉
        criteria = gz_data.get('criteria', {})
        overall = criteria.get('overall', '鏈垽瀹?)
        
        textstr = f'''绋虫€ф寚鏍囷細
GM = {gm:.4f}m
GZ_max = {gz_max:.4f}m
胃_max_gz = {theta_max_gz:.1f}掳
胃_vanish = {theta_vanish:.1f}掳
K = {k_value:.4f}

瑙勮寖鍒ゅ畾锛歿overall}'''
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=props, family='monospace')
    
    def plot_multiple_conditions(self, conditions_data: Dict, 
                                output_path: Optional[str] = None) -> Tuple:
        """
        缁樺埗澶氬伐鍐靛姣斿浘
        
        鍙傛暟锛?            conditions_data: {宸ュ喌鍚? gz_data}
            output_path: 杈撳嚭璺緞锛堝彲閫夛級
        
        杩斿洖锛?            (fig, axes) 鍥惧舰瀵硅薄
        """
        n_conditions = len(conditions_data)
        n_cols = 2
        n_rows = (n_conditions + 1) // 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4*n_rows), dpi=self.dpi)
        
        if n_conditions == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        for idx, (condition_name, gz_data) in enumerate(conditions_data.items()):
            ax = axes[idx]
            
            rows = gz_data.get('rows', [])
            if not rows:
                continue
            
            thetas = np.array([r['theta'] for r in rows])
            gzs = np.array([r['GZ'] for r in rows])
            
            # 缁樺埗鏇茬嚎
            ax.plot(thetas, gzs, 'b-', linewidth=2.5)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('妯€捐 胃 (掳)', fontsize=11)
            ax.set_ylabel('澶嶅師鍔涜噦 GZ (m)', fontsize=11)
            ax.set_title(f'{condition_name}', fontsize=12, fontweight='bold')
            ax.set_xlim(0, 90)
            
            # 鏍囨敞鍏抽敭鐐?            gz_max = gz_data.get('GZ_max', 0)
            theta_max_gz = gz_data.get('theta_max_gz', 0)
            
            if gz_max > 0:
                ax.plot(theta_max_gz, gz_max, 'ro', markersize=8)
                ax.annotate(f'GZ_max={gz_max:.3f}m', 
                           xy=(theta_max_gz, gz_max),
                           xytext=(theta_max_gz + 5, gz_max + 0.03),
                           fontsize=9)
        
        # 闅愯棌澶氫綑鐨勫瓙鍥?        for idx in range(n_conditions, len(axes)):
            axes[idx].set_visible(False)
        
        fig.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        
        return fig, axes
    
    def export_to_png(self, fig, output_path: str, dpi: int = 300):
        """瀵煎嚭涓?PNG"""
        fig.savefig(output_path, dpi=dpi, bbox_inches='tight', format='png')
    
    def export_to_svg(self, fig, output_path: str):
        """瀵煎嚭涓?SVG"""
        fig.savefig(output_path, bbox_inches='tight', format='svg')
    
    def export_to_base64(self, fig) -> str:
        """瀵煎嚭涓?Base64锛堢敤浜庣綉椤垫樉绀猴級"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return image_base64


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
    print('澧炲己鐨?GZ 鏇茬嚎缁樺埗妯″潡娴嬭瘯')
    print('=' * 70)
    
    # 妯℃嫙 GZ 鏁版嵁
    thetas = np.arange(0, 91, 5)
    gzs = 0.42 * np.sin(np.radians(thetas))
    
    mock_gz_data = {
        'GM': 0.8234,
        'GZ_max': 0.42,
        'theta_max_gz': 30.0,
        'theta_vanish': 85.0,
        'K': 1.2,
        'rows': [
            {'theta': float(t), 'GZ': float(gz)}
            for t, gz in zip(thetas, gzs)
        ],
        'criteria': {'overall': '鍏ㄩ儴閫氳繃'}
    }
    
    # 鍒涘缓缁樺浘鍣?    plotter = EnhancedGzPlotter()
    
    # 缁樺埗鍗曞伐鍐?    print('\n銆愮粯鍒跺崟宸ュ喌 GZ 鏇茬嚎銆?)
    fig, ax = plotter.plot_gz_curve_with_annotations(mock_gz_data, '婊¤浇鍑烘腐')
    print('鉁?鍗曞伐鍐?GZ 鏇茬嚎缁樺埗瀹屾垚')
    
    # 瀵煎嚭涓?Base64
    print('\n銆愬鍑轰负 Base64銆?)
    b64 = plotter.export_to_base64(fig)
    print(f'鉁?Base64 闀垮害: {len(b64)} 瀛楃')
    
    print('\n鉁?澧炲己鐨?GZ 鏇茬嚎缁樺埗妯″潡娴嬭瘯閫氳繃!')


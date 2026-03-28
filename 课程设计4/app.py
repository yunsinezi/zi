# ============================================================
# app.py — Flask 主入口（全链路修复版）
# 船舶静力学课程设计自动计算系统
# 武汉理工大学 船舶与海洋工程学院
# ============================================================
# 修复清单：
# 1. CORS跨域全场景兼容（POST/JSON/OPTIONS预检）
# 2. 统一响应格式 success/msg/result
# 3. 全局异常捕获兜底
# 4. Railway动态端口 + 本地固定端口双适配
# ============================================================

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import traceback
import zipfile
import logging
from datetime import datetime

# ============================================================
# 日志配置（适配 Railway 日志面板）
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ship-hydrostatics")

# ============================================================
# Railway 部署修复：确保 core 模块可被导入
# ============================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ============================================================
# 导入所有核心模块（带错误处理）
# ============================================================
_import_errors = []

try:
    from core import calculator as calculator_module
    from core import exporter as exporter_module
    from core import excel_parser as excel_parser_module
    from core import template_generator as template_generator_module
    from core import hydrostatics_full as hydrostatics_full_module
    from core import exporter_full as exporter_full_module
    from core import bonjean as bonjean_module
    from core import plotter as plotter_module
    from core import stability as stability_module
    from core import plotter_gz as plotter_gz_module
    from core import loading_condition as loading_condition_module
    from core import floating_stability as floating_stability_module
    from core import stability_criteria as stability_criteria_module
    from core import loading_stability_analysis as loading_stability_analysis_module
    from core import export_stability_report as export_stability_report_module
    from core import word_report_generator as word_report_generator_module
    logger.info("所有核心模块导入成功")
except ImportError as e:
    _import_errors.append(f"模块导入错误: {str(e)}")
    logger.error(f"模块导入失败: {e}")
    traceback.print_exc()

# ============================================================
# 创建 Flask 应用
# ============================================================
app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# CORS 跨域全场景兼容配置（关键修复！）
# ─────────────────────────────────────────────────────────────
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    expose_headers=["Content-Disposition"],
    supports_credentials=False,
    max_age=3600,
)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
app.config["JSON_AS_ASCII"] = False

PORT = int(os.getenv("PORT", 5000))
HOST = "0.0.0.0"


def _safe_filename(filename):
    if not filename:
        return None
    base = os.path.basename(filename)
    if base != filename or ".." in base or "/" in base or "\\" in base:
        return None
    return base


# ============================================================
# 全局错误处理
# ============================================================
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"success": False, "msg": f"请求错误: {str(e.description)}"}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "msg": "资源不存在"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "msg": "方法不允许"}), 405

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"success": False, "msg": "上传文件过大，最大允许 50MB"}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500错误: {e}")
    return jsonify({"success": False, "msg": f"服务器内部错误: {str(e)}"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(f"未捕获异常: {e}")
    return jsonify({"success": False, "msg": f"服务器异常: {str(e)}"}), 500


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
TEMPLATE_PATH = os.path.join(OUTPUT_DIR, "型值表模板.xlsx")


# ============================================================
# 健康检查接口
# ============================================================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ship-hydrostatics",
        "import_errors": _import_errors if _import_errors else None
    }), 200


@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# 阶段1：单吃水计算
# ============================================================
@app.route("/calculate", methods=["POST", "OPTIONS"])
def calculate():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            return jsonify({"success": False, "msg": "请求体必须为JSON格式"}), 400
        
        draft = data.get("draft")
        stations = data.get("stations")
        half_breadths = data.get("half_breadths")
        
        if draft is None:
            return jsonify({"success": False, "msg": "缺少必填参数: draft"}), 400
        if not stations:
            return jsonify({"success": False, "msg": "缺少参数: stations"}), 400
        if not half_breadths:
            return jsonify({"success": False, "msg": "缺少参数: half_breadths"}), 400
        
        draft = float(draft)
        stations = [float(x) for x in stations]
        half_breadths = [float(y) for y in half_breadths]
        
        result = calculator_module.calculate_hydrostatics(stations, half_breadths, draft)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.exception("calculate 异常")
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/export_excel", methods=["POST", "OPTIONS"])
def export_excel():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        calc_data = data.get("data") or data.get("result")
        stations = data.get("stations")
        half_breadths = data.get("half_breadths")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"静水力计算_{timestamp}.xlsx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        exporter_module.export_to_excel(calc_data, stations, half_breadths, full_path)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/download_excel/<filename>")
def download_excel(filename):
    safe = _safe_filename(filename)
    if not safe:
        return jsonify({"success": False, "msg": "非法文件名"}), 400
    file_path = os.path.join(OUTPUT_DIR, safe)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"success": False, "msg": "文件不存在"}), 404


# ============================================================
# 阶段2：型值表上传
# ============================================================
@app.route("/download_template")
def download_template():
    try:
        template_generator_module.generate_template(TEMPLATE_PATH, example=True)
        return send_file(TEMPLATE_PATH, as_attachment=True, download_name="型值表模板.xlsx")
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/download_template_blank")
def download_template_blank():
    blank_path = os.path.join(OUTPUT_DIR, "型值表模板_空白.xlsx")
    try:
        template_generator_module.generate_template(blank_path, example=False)
        return send_file(blank_path, as_attachment=True, download_name="型值表模板_空白.xlsx")
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/upload_offsets", methods=["POST", "OPTIONS"])
def upload_offsets():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "msg": "未上传文件"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "msg": "文件名为空"}), 400
        upload_path = os.path.join(UPLOAD_DIR, "offsets_upload.xlsx")
        file.save(upload_path)
        parsed_data = excel_parser_module.parse_offsets_excel(upload_path)
        return jsonify({"success": True, "data": parsed_data})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


# ============================================================
# 阶段3：多吃水全参数计算
# ============================================================
@app.route("/calc_table", methods=["POST", "OPTIONS"])
def calc_table():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        start_draft = float(data.get("start_draft", 0))
        end_draft = float(data.get("end_draft", 10))
        step = float(data.get("step", 0.5))
        offsets_data = data.get("data") or data.get("offsets_data")
        hydrostatics_table = hydrostatics_full_module.calc_hydrostatics_table(
            offsets_data["stations"], offsets_data["waterlines"],
            offsets_data["offsets_matrix"], start_draft, end_draft, step
        )
        return jsonify({"success": True, "table": hydrostatics_table})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/export_table", methods=["POST", "OPTIONS"])
def export_table():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        hydrostatics_table = data.get("table") or data.get("data")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"全参数计算_{timestamp}.xlsx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        exporter_full_module.export_hydrostatics_excel(hydrostatics_table, full_path)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


# ============================================================
# 阶段4：邦戎曲线
# ============================================================
@app.route("/calc_bonjean", methods=["POST", "OPTIONS"])
def calc_bonjean():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        offsets_data = data.get("data") or data.get("offsets_data")
        start_draft = float(data.get("start_draft", 2.0))
        end_draft = float(data.get("end_draft", 6.0))
        step = float(data.get("step", 0.5))
        bonjean_table = bonjean_module.calc_bonjean_table(
            offsets_data["stations"], offsets_data["waterlines"],
            offsets_data["offsets_matrix"], start_draft, end_draft, step
        )
        return jsonify({"success": True, "bonjean": bonjean_table})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/plot_hydrostatics", methods=["POST", "OPTIONS"])
def plot_hydrostatics_endpoint():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        hydrostatics_table = data.get("data") or data.get("table")
        plotter_module.plot_hydrostatics(hydrostatics_table, OUTPUT_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return jsonify({"success": True, "filename": f"静水力曲线_{timestamp}.png"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/plot_bonjean", methods=["POST", "OPTIONS"])
def plot_bonjean_endpoint():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        bonjean_table = data.get("data") or data.get("bonjean")
        plotter_module.plot_bonjean(bonjean_table, OUTPUT_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return jsonify({"success": True, "filename": f"邦戎曲线_{timestamp}.png"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/preview_hydrostatics", methods=["POST", "OPTIONS"])
def preview_hydrostatics():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        hydrostatics_table = data.get("data") or data.get("table")
        preview_base64 = plotter_module.plot_hydrostatics_preview(hydrostatics_table)
        return jsonify({"success": True, "image": preview_base64})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/preview_bonjean", methods=["POST", "OPTIONS"])
def preview_bonjean():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        bonjean_table = data.get("data") or data.get("bonjean")
        preview_base64 = plotter_module.plot_bonjean_preview(bonjean_table)
        return jsonify({"success": True, "image": preview_base64})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/download_plot/<filename>")
def download_plot(filename):
    safe = _safe_filename(filename)
    if not safe:
        return jsonify({"success": False, "msg": "非法文件名"}), 400
    file_path = os.path.join(OUTPUT_DIR, safe)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"success": False, "msg": "文件不存在"}), 404


# ============================================================
# 阶段5：GZ曲线
# ============================================================
@app.route("/calc_gz", methods=["POST", "OPTIONS"])
def calc_gz():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        draft = float(data.get("draft", 5.0))
        step = float(data.get("step", 5.0))
        offsets_data = data.get("offsets_data")
        KG = float(data.get("KG", 5.0))
        gz_curve = stability_module.calc_gz_curve(offsets_data, draft, KG, theta_step=step)
        return jsonify({"success": True, "data": gz_curve})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/plot_gz", methods=["POST", "OPTIONS"])
def plot_gz():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        gz_result = data.get("gz_result") or data.get("data")
        plotter_gz_module.plot_gz_curve(gz_result, OUTPUT_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return jsonify({"success": True, "filename": f"GZ曲线_{timestamp}.png"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/preview_gz", methods=["POST", "OPTIONS"])
def preview_gz():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        gz_result = data.get("gz_result") or data.get("data")
        preview_base64 = plotter_gz_module.plot_gz_preview(gz_result)
        return jsonify({"success": True, "image": preview_base64})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


# ============================================================
# 阶段6：装载工况稳性校核
# ============================================================
@app.route("/loading_conditions", methods=["GET"])
def get_loading_conditions():
    try:
        manager = loading_condition_module.LoadingConditionManager()
        conditions = manager.export_conditions()
        return jsonify({"success": True, "data": conditions})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/analyze_stability", methods=["POST", "OPTIONS"])
def analyze_stability():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        offsets_data = data.get("offsets_data")
        hydrostatics_table = data.get("hydrostatics_table")
        KG = float(data.get("KG", 5.0))
        analysis = loading_stability_analysis_module.LoadingStabilityAnalysis(
            offsets_data, hydrostatics_table, stability_module.calc_gz_curve
        )
        results = analysis.analyze_all_standard_conditions()
        summary = analysis.get_judgment_summary()
        return jsonify({"success": True, "data": {"results": results, "summary": summary}})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/list_loading_conditions", methods=["GET"])
def list_loading_conditions():
    try:
        manager = loading_condition_module.LoadingConditionManager()
        conditions = manager.export_conditions()
        return jsonify({"success": True, "conditions": conditions})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/get_loading_condition", methods=["POST", "OPTIONS"])
def get_loading_condition():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        condition_name = data.get("condition_name")
        manager = loading_condition_module.LoadingConditionManager()
        condition = manager.get_condition(condition_name)
        if condition is None:
            return jsonify({"success": False, "msg": f"未找到工况: {condition_name}"}), 404
        return jsonify({"success": True, "condition": condition.to_dict()})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/analyze_loading_condition", methods=["POST", "OPTIONS"])
def analyze_loading_condition():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        offsets_data = data.get("offsets_data")
        hydrostatics_table = data.get("hydrostatics_table")
        condition_name = data.get("condition_name")
        analysis = loading_stability_analysis_module.LoadingStabilityAnalysis(
            offsets_data, hydrostatics_table, stability_module.calc_gz_curve
        )
        analysis_result = analysis.analyze_condition(condition_name)
        judgment_result = analysis.judgment_results.get(condition_name, {})
        return jsonify({"success": True, "analysis": analysis_result, "judgment": judgment_result})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/analyze_all_loading_conditions", methods=["POST", "OPTIONS"])
def analyze_all_loading_conditions():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        offsets_data = data.get("offsets_data")
        hydrostatics_table = data.get("hydrostatics_table")
        analysis = loading_stability_analysis_module.LoadingStabilityAnalysis(
            offsets_data, hydrostatics_table, stability_module.calc_gz_curve
        )
        analysis.analyze_all_standard_conditions()
        results = {}
        for condition_name in ['满载出港', '满载到港', '压载出港', '压载到港']:
            results[condition_name] = {
                'analysis': analysis.analysis_results.get(condition_name, {}),
                'judgment': analysis.judgment_results.get(condition_name, {})
            }
        summary = analysis.get_judgment_summary()
        return jsonify({"success": True, "results": results, "summary": summary})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/export_stability_report", methods=["POST", "OPTIONS"])
def export_stability_report():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        condition_name = data.get("condition_name", "unknown")
        analysis = data.get("analysis", {})
        judgment = data.get("judgment", {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"稳性校核_{condition_name}_{timestamp}.xlsx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        exporter = export_stability_report_module.StabilityReportExporter()
        exporter.create_single_condition_report(condition_name, analysis, judgment, full_path)
        return jsonify({"success": True, "filename": filename, "download_url": f"/download_report/{filename}"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/export_all_conditions_report", methods=["POST", "OPTIONS"])
def export_all_conditions_report():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        results = data.get("results", {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"全工况稳性校核报告_{timestamp}.xlsx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        exporter = export_stability_report_module.StabilityReportExporter()
        exporter.create_all_conditions_report(results, full_path)
        return jsonify({"success": True, "filename": filename, "download_url": f"/download_report/{filename}"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


# ============================================================
# 阶段4 补充路由
# ============================================================
@app.route("/export_hydrostatics", methods=["POST", "OPTIONS"])
def export_hydrostatics():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        hydrostatics_table = data.get("table") or data.get("data")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"全参数计算_{timestamp}.xlsx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        exporter_full_module.export_hydrostatics_excel(hydrostatics_table, full_path)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/export_plots", methods=["POST", "OPTIONS"])
def export_plots():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        table = data.get("table")
        bonjean = data.get("bonjean")
        formats = data.get("formats", ["png"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"曲线图_{timestamp}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_filename)
        if table:
            try:
                plotter_module.plot_hydrostatics(table, OUTPUT_DIR)
            except Exception:
                pass
        if bonjean:
            try:
                plotter_module.plot_bonjean(bonjean, OUTPUT_DIR)
            except Exception:
                pass
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fmt in formats:
                for pattern, label in [("静水力曲线", "静水力曲线"), ("邦戎曲线", "邦戎曲线")]:
                    for ext in ["png", "svg"] if "svg" in formats else ["png"]:
                        src = os.path.join(OUTPUT_DIR, f"{pattern}_{timestamp}.{ext}")
                        if os.path.exists(src):
                            zf.write(src, f"{label}.{ext}")
            if len(zf.namelist()) == 0:
                zf.writestr("说明.txt", "曲线图生成失败，请检查数据是否完整。")
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


# ============================================================
# 阶段7：Word报告
# ============================================================
@app.route("/generate_report", methods=["POST", "OPTIONS"])
def generate_report():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        report_data = data.get("report_data", {})
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"课程设计报告_{timestamp}.docx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        generator = word_report_generator_module.CourseDesignReportGenerator()
        generator.generate(report_data, full_path)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/generate_word_report", methods=["POST", "OPTIONS"])
def generate_word_report():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json(force=True, silent=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"课程设计报告_{timestamp}.docx"
        full_path = os.path.join(OUTPUT_DIR, filename)
        report_data = {
            "user_info": data.get("user_info", {}),
            "ship_data": data.get("ship_data", {}),
            "hydrostatics_result": data.get("hydrostatics_result", {}),
            "bonjean_result": data.get("bonjean_result", {}),
            "stability_results": data.get("stability_results", {}),
        }
        generator = word_report_generator_module.CourseDesignReportGenerator()
        generator.generate(report_data, full_path)
        return jsonify({"success": True, "filename": filename, "download_url": f"/download_report/{filename}"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)}), 500


@app.route("/download_report/<filename>")
def download_report(filename):
    safe = _safe_filename(filename)
    if not safe:
        return jsonify({"success": False, "msg": "非法文件名"}), 400
    file_path = os.path.join(OUTPUT_DIR, safe)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"success": False, "msg": "文件不存在"}), 404


# ============================================================
# 启动入口
# ============================================================
if __name__ == "__main__":
    logger.info(f"启动船舶静力学课程设计系统 on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)

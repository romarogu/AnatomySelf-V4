# AnatomySelf - Personal Life Lab V5.5

AnatomySelf 是一款专业级、具有医学严谨性和艺术审美感的个人生命实验室。V5.5 版本从原型工具全面升级，引入了深空暗黑美学、Bento Grid 布局、SVG 人体剪影、五模块解耦架构以及基于大语言模型的生命洞察引擎。

## 🌟 核心特性 (V5.5)

1. **视觉与审美标准 (Aesthetic Overhaul)**
   - **Deep Dark Mode (深空暗黑模式)**: 主色调为 `#0E1117`，辅助色为医疗蓝、极光绿和暗金。
   - **达芬奇手稿水印**: 在背景中融入达芬奇风格的解剖线描图，提升整体格调。
   - **Bento Grid 布局**: 采用 Apple Health 风格的极简卡片布局，精密感十足。
   - **专业组件库**: 采用 Lucide 极简线条图标，所有图表使用 Plotly 进行专业科学定制。
   - **SVG 人体剪影**: 废除方块人，采用极简、半透明的 SVG 矢量人体剪影，支持正面/背面切换。

2. **系统架构解耦 (Structural Decoupling)**
   - **全景健康中枢 (Precision Health Hub)**: 首页看板，展示当前激活用户的画像、六维健康评分、可编辑的“过敏/慢性病史”标签云。
   - **数据中心 (Data Center)**: 纯粹的录入模块，支持图片/PDF 的 OCR 智能导入和结构化手动录入，采用 Upsert 逻辑避免重复。
   - **生理审计实验室 (Physiological Audit Lab)**: 专业数据分析模块，支持多指标对比、雷达图、箱线图等高级可视化。
   - **生命律动周报 (V-Life Weekly Report)**: 自动生成每周健康总结与趋势分析。
   - **生命洞察引擎 (Life Insight Engine)**: 深度集成 AI 与八字命理算法。

3. **命理内核升级 (Bazi & AI Integration)**
   - **三位一体计算**: 支持 [本命原局] + [当前大运] + [流年] 的完整八字逻辑。
   - **AI 命理医学专家**: 接入大语言模型（如 DeepSeek），扮演精通子平八字与现代病理学的跨界医学专家。
   - **持久化对话**: 提供持久化的 AI 对话界面，对话记录保存在服务器，下次登录可继续查看。

4. **数据与稳定性增强**
   - **CASCADE DELETE**: 支持级联删除，彻底清理冗余数据。
   - **全方位异常处理**: 增加鲁棒的 `try-except` 异常处理，为缺失指标提供合理的默认生理值，彻底解决 `NoneType` 错误。

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.9+。

```bash
# 克隆仓库
git clone https://github.com/romarogu/AnatomySelf-V4.git
cd AnatomySelf-V4

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 AI 与环境变量

系统支持通过 `.env` 文件或 Streamlit 的 `secrets.toml` 进行配置。

**方式一：使用 `.env` 文件（推荐本地开发）**
复制示例配置文件并填入您的 API Key：
```bash
cp .env.example .env
```
编辑 `.env` 文件，填入您的 `LLM_API_KEY`。

**方式二：使用 Streamlit Secrets（推荐部署）**
创建 `.streamlit/secrets.toml` 文件：
```toml
LLM_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"
DEFAULT_CITY = "Beijing"
```

### 3. OCR 依赖（可选）

如果您需要使用体检报告的 OCR 智能导入功能，请安装额外的系统依赖：

**macOS:**
```bash
brew install tesseract tesseract-lang
pip install pdfplumber pytesseract Pillow
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
pip install pdfplumber pytesseract Pillow
```

### 4. 启动服务

```bash
streamlit run app.py
```
服务启动后，浏览器将自动打开 `http://localhost:8501`。

## 演示账号

- 用户名: `ruogu`
- 密码: `demo123`

## 许可证

MIT License

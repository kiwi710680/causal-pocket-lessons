# AGENTS.md — 因果口袋講義（Causal Pocket Lessons）

> 給 AI 的員工手冊。每次開工前先讀完這份文件，再讀 `NOTES.md`（現在進度）與 `log.md`（過去的決定）。
> Claude Code 會透過 `CLAUDE.md` 自動載入這份文件；其他工具（Codex、Gemini CLI 等）直接讀這份。

---

## 1. 這個專案在做什麼

- **目的**：把因果推論與藥物流行病學的觀念，做成「一次 10 分鐘、翻頁就能讀完」的中文網頁講義，給剛入門的研究生與臨床人員。
- **成品**：一個 GitHub Pages 網站。首頁是講義目錄；每份講義是一個獨立資料夾裡的翻頁式 `index.html`。
- **讀者**：懂一點統計、但沒學過因果推論的人。**直覺先於符號**：先講故事或例子，再給公式。
- **每份講義只講一個觀念**。一個觀念講不完，就拆成兩份，不要塞。

## 2. 資料夾結構

```text
causal-pocket/
├── AGENTS.md            ← 本文件（規則的唯一來源）
├── CLAUDE.md            ← 只有一行 @AGENTS.md，讓 Claude Code 自動載入
├── README.md            ← 給人看的專案介紹
├── NOTES.md             ← 目前進度白板（每次工作結束更新）
├── log.md               ← 決策紀錄（只增不刪）
├── lessons.json         ← 講義登錄表：首頁卡片的唯一資料來源
├── index.html           ← 首頁（卡片區由 tools/build_index.py 產生，勿手改）
├── .nojekyll
├── shared/
│   ├── style.css        ← 全站唯一樣式表（色票、字體、元件）
│   └── deck.js          ← 翻頁、頁碼、測驗、揭曉等共用行為
├── notes/
│   └── <slug>.md        ← 講義文字稿（內容先行，見 §4）
├── lessons/
│   ├── _template/       ← 新講義的起點，複製它，不要改它
│   │   └── index.html
│   └── <slug>/
│       ├── index.html
│       └── assets/      ← （選用）這份講義專用的圖片
└── tools/
    ├── new_lesson.py    ← 建立新講義骨架
    ├── build_index.py   ← 依 lessons.json 重建首頁卡片
    └── check.py         ← 驗收：所有規則的自動檢查
```

## 3. 命名規則

| 東西 | 規則 | 例子 |
|---|---|---|
| slug | 英文小寫＋連字號，描述觀念本身 | `immortal-time-bias` |
| 講義資料夾 | `lessons/<slug>/` | `lessons/confounding-dag/` |
| 文字稿 | `notes/<slug>.md`，**slug 必須與資料夾相同** | `notes/confounding-dag.md` |
| 講義編號 `code` | `CP-` 加兩位數，依上架順序遞增，不重用 | `CP-03` |
| 圖片 | `lessons/<slug>/assets/<英文小寫-連字號>.svg/png` | `assets/timeline.svg` |

`lessons.json` 每筆格式（四個欄位都必填）：

```json
{ "slug": "confounding-dag", "code": "CP-02", "title": "干擾與 DAG：到底該調整誰？",
  "summary": "一句話說明這份講義讓讀者帶走什麼（40 字內）", "minutes": 10, "level": "入門" }
```

`level` 只能是 `入門`、`進階`、`實務` 三者之一。

## 4. 工作流程：內容先行（鐵則）

新增或大改一份講義時，**依序**做：

1. **寫文字稿** `notes/<slug>.md`：每一頁用 `## Sxx 頁面類型｜標題` 開頭（例：`## S03 concept｜因果推論的根本問題`），下面寫該頁的最終文字。頁數必須和 HTML 相同。
2. **給使用者看文字稿**，確認後才產生 HTML。使用者說「直接做」時可以跳過等待，但文字稿仍然要先寫。
3. **建骨架**：`python tools/new_lesson.py <slug> <CP-xx> "<標題>"`（會複製 `_template`、建立文字稿、加進 `lessons.json`）。
4. **把文字稿做成 HTML**：只放文字稿上有的內容，不臨時加段落。
5. **重建首頁**：`python tools/build_index.py`。
6. **驗收**：`python tools/check.py` 必須顯示 `ALL CHECKS PASSED`，並在瀏覽器實際翻過每一頁。
7. **收尾**：更新 `NOTES.md`；若有影響之後檔案的決定，追加到 `log.md`。

修改既有講義的文字時，**先改 `notes/<slug>.md`，再改 HTML**，兩邊保持一致。

## 5. 講義頁面的結構

每份講義是一個 `<main class="deck">`，裡面每一頁是一個 `<section class="slide" data-type="類型">`。
頁面類型一律寫在 `data-type`，**不要寫成 class**（`quiz`、`formula` 同時是元件 class，寫成 class 會讓元件行為套到整頁）。

### 5.1 必備規則

- 總頁數 **6–12 頁**。
- **第 1 頁**必須是 `cover`；**最後一頁**必須是 `summary`。
- **至少 1 頁 `quiz`**（讀者要動手，不只是看）。
- `<body>` 必須有 `data-code="CP-xx"` 與 `data-title="講義標題"`；頁尾的編號、標題、頁碼由 `deck.js` 自動產生，**不要手寫頁尾**。
- 只引用 `../../shared/style.css` 和 `../../shared/deck.js`；外部資源只允許 Google Fonts。不得引入其他 CDN、框架或追蹤碼。

### 5.2 頁面類型（class）

| `data-type` | 用途 | 內容規範 |
|---|---|---|
| `cover` | 封面 | `.kicker`（編號＋程度）、`h1` 標題、`.hook` 一句用問題開場的引子 |
| `concept` | 講一個觀念 | `.kicker` 小標、`h2`、正文 ≤ 120 字；可加一個 `.callout` |
| `figure` | 圖或表為主 | 一張 inline SVG 或 `.table`，配 ≤ 60 字說明 |
| `cards` | 並列 2–4 個要點 | `.card-row` 內放 `.card`，每張卡 ≤ 50 字 |
| `formula` | 公式 | `.formula` 區塊；公式下**一定**要有一行白話翻譯 `.plain` |
| `lab` | 互動小實驗 | 該講義專屬的 JS 寫在檔案底部的 `<script>`；要有「先猜再動」的提示 |
| `quiz` | 小測驗 | 見 §5.3 |
| `summary` | 帶走三句話 | `.takeaways` 清單，**剛好 3 條**；最後附 `.next` 指向下一份講義或延伸閱讀 |

### 5.3 共用元件

```html
<!-- 測驗：data-answer 填正確選項的 data-opt；每個選項都要有 data-why 解釋 -->
<div class="quiz" data-answer="b">
  <p class="q">問題文字</p>
  <button data-opt="a" data-why="為什麼錯">選項 A</button>
  <button data-opt="b" data-why="為什麼對">選項 B</button>
  <p class="quiz-why" aria-live="polite"></p>
</div>

<!-- 揭曉：點按鈕後才顯示 .reveal-body -->
<div class="reveal">
  <button class="reveal-btn">按鈕文字</button>
  <div class="reveal-body">被藏起來的內容</div>
</div>

<!-- 提示框：note（補充）、warn（常見錯誤） -->
<div class="callout note">…</div>
<div class="callout warn">…</div>
```

## 6. 視覺風格：「白紙實驗筆記」

- **感覺**：像一本乾淨的研究筆記。白底、細線、留白多；不要漸層、不要陰影堆疊、不要 emoji 當裝飾、不要 AI 感的大圓角卡片牆。
- **色票**（只能用 `shared/style.css` 裡的 CSS 變數，HTML 裡不得寫死色碼）：

| 變數 | 色碼 | 用途 |
|---|---|---|
| `--paper` | `#FFFFFF` | 頁面底色 |
| `--desk` | `#F1EFEA` | 頁面外的桌面色 |
| `--ink` | `#1F2A33` | 正文、線條 |
| `--muted` | `#6B7681` | 次要文字、頁尾 |
| `--rule` | `#D8D4CB` | 分隔線、表格線 |
| `--accent` | `#B8432B` | 朱紅：重點、處置 A、錯誤答案 |
| `--teal` | `#2D6E73` | 青綠：結果 Y、正確答案 |
| `--gold` | `#B88A1E` | 土黃：干擾因子、警告 |
| `--wash` | `#F7F4EC` | 淡底：提示框、公式框 |

- **在圖裡的固定配色**：處置 A＝`--accent`、結果 Y＝`--teal`、干擾／其他變數＝`--gold` 或 `--ink`。所有講義一致，讀者看顏色就知道角色。
- **字體**：標題 `Noto Serif TC`；正文 `Noto Sans TC`；編號、變數、程式 `IBM Plex Mono`。
- **標點**：中文用全形標點（，。：「」）；中英文之間空一格（例：「用 DAG 判斷」）。
- **用語**：處置（treatment）、結果（outcome）、干擾因子（confounder）、碰撞因子（collider）、中介因子（mediator）、潛在結果（potential outcome）。第一次出現的術語附英文。
- **手機**：寬度 ≤ 760px 時自動改成直向捲動（由 `style.css` 處理）。不要另寫手機版。

## 7. 內容正確性規則

- 數字範例必須**自己算得出來**：表格、模擬的數字要能互相對上，在文字稿附上計算過程。
- 互動實驗用的是**玩具模型**時，頁面上要寫明「這是簡化的示意模型」。
- 引用文獻或課本時寫在 `.next` 或文字稿最後的「參考」段；不要編造出處。
- 不放真實病人資料。範例一律是虛構的。

## 8. AI 修改時的權限

| 可以直接做 | 要先問使用者 |
|---|---|
| 新增講義、修改講義文字與互動 | 修改 `shared/style.css` 的色票或字體 |
| 修 bug、修錯字 | 修改 `shared/deck.js` 的既有行為（新增元件可以，但要寫進 §5.3） |
| 重建首頁、跑 `check.py` | 刪除或改名已上架的講義（網址會壞） |
| 更新 `NOTES.md`、追加 `log.md` | `git commit`／`git push`（上架等於公開） |

- 不要手改 `index.html` 的卡片區（`<!-- LESSONS:START -->` 到 `<!-- LESSONS:END -->`），一律改 `lessons.json` 再跑 `build_index.py`。
- 不要改 `lessons/_template/` 來做某一份講義；它只能因為規則改變而更新，並同步更新本文件。
- 規則本身要改時：先改 `AGENTS.md`，在 `log.md` 記一筆，再改程式。

## 9. 「做完」的定義（驗收清單）

- [ ] `notes/<slug>.md` 與 HTML 頁數、頁面類型一致
- [ ] `python tools/check.py` 顯示 `ALL CHECKS PASSED`
- [ ] 本機瀏覽器開啟，鍵盤 ← → 可翻完每一頁，測驗與互動都能操作，Console 沒有錯誤
- [ ] 手機寬度（375px）下可正常捲動閱讀
- [ ] 首頁出現新卡片，點得進去
- [ ] `NOTES.md` 已更新

## 10. 本機預覽與上架

```bash
python -m http.server 8000      # 在專案根目錄執行，開 http://localhost:8000
```

上架：使用者同意後 `git push` 到 `main`，GitHub Pages 由 `main` 分支根目錄發布。
網址格式：`https://kiwi710680.github.io/causal-pocket-lessons/lessons/<slug>/`

# 因果口袋講義（Causal Pocket Lessons）

一次 10 分鐘、翻頁就讀完的因果推論與藥物流行病學中文講義。

- 網站：https://kiwi710680.github.io/causal-pocket-lessons/
- 規則：[`AGENTS.md`](AGENTS.md)（`CLAUDE.md` 只是匯入它）

## 目前的講義

| 編號 | 講義 | 程度 |
|---|---|---|
| CP-01 | [潛在結果：因果到底是什麼？](https://kiwi710680.github.io/causal-pocket-lessons/lessons/potential-outcomes/) | 入門 |
| CP-02 | [干擾與 DAG：到底該調整誰？](https://kiwi710680.github.io/causal-pocket-lessons/lessons/confounding-dag/) | 入門 |
| CP-03 | [不朽時間偏誤：時間零點放錯會怎樣？](https://kiwi710680.github.io/causal-pocket-lessons/lessons/immortal-time-bias/) | 實務 |

## 新增一份講義（給 AI 也給人）

```bash
python tools/new_lesson.py selection-bias CP-04 "選擇偏誤：誰被留在研究裡？"
# 1. 寫 notes/selection-bias.md（內容先行）
# 2. 依文字稿改 lessons/selection-bias/index.html
python tools/build_index.py
python tools/check.py        # 要看到 ALL CHECKS PASSED
python -m http.server 8000   # 本機預覽
```

純 HTML／CSS／JavaScript，沒有建置步驟；工具只用 Python 標準函式庫。

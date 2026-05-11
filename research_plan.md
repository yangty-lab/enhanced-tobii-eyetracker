# 研究計畫：建築空間動態視覺感知的計算模型

> 作者：Ting-Yu Yang（楊庭宇） · 指導教授：June-Hao Hou（侯君昊）
> 機構：National Yang Ming Chiao Tung University, Graduate Institute of Architecture
> 整理日期：2026-05-11

---

## 1. 研究背景與核心議題

### 學科缺口
建築領域的視覺感知量化長期依賴**靜態圖像分析**（如 3M VAS）與**局部低階特徵**（邊緣、色彩對比、幾何複雜度）。然而：
- 現代建築強調**整體性**與**空間敘事**：尺度漂移、透視轉換、occlusion release、轉角預期。
- 環境感知理論（Environmental Perception Theory）主張：空間理解不源自單點凝視，而是在**連續導航**中由視覺—空間介面互動所建構。
- 因此既有 VA 工具無法捕捉「步行者真實體驗」，造成**理論與工具之間的雙重斷裂**。

### 研究問題
> 如何將「時序連續性」與「FPV 真實導航」納入建築 visual attention 預測模型，使其反映 ecological validity？

### 長期目標（碩論主幹）
建立一個動態視覺顯著性模型 → 作為下一階段「現代建築動態美學評估框架」的計算基礎，最終整合主觀情緒／認知資料，產出設計決策的 data-driven 方法論。

---

## 2. 理論定位（已蒐集的文獻群可對應到三層）

| 層次 | 對應文獻群 | 在本研究中的角色 |
|---|---|---|
| **神經美學／環境認知** | Brielmann（Walk Down the Street）、Form Follows Function、neuroaesthetics of architectural spaces、Fractal Architecture、Spatial perception of ceiling height | 提供「為何要動態」「為何要 ecological」的理論正當性 |
| **建築感知工具化** | Salingaros（Biophilic, Fractal）、3M VAS validation、harmony-seeking-computations、Architectural Beauty 客觀量表 | 既有工具的能力上限與盲點 → 切入點 |
| **計算視覺基礎** | Itti–Koch 系列、Lee 2005 mesh saliency、Lavoue 2018（2D→3D 視線投射）、SAL3D、ACLNet、ViNet、Revisiting Video Saliency Prediction | 兩條技術路線的方法支柱 |

---

## 3. 兩條技術路線（也是兩篇投稿）

### Route A — 2D Video Pipeline ✦ Sigradi 2026（**較成熟**）

```
FPV 校園建築導航影片 ─► 受試者眼動 ─► KDE 連續 heatmap (GT)
                                              │
                                              ▼
                  3M VAS 靜態 baseline ◄── 比較 ──► ACLNet (CNN-LSTM) fine-tune
                                              │
                                       NSS / CC / KL 評估
```

- **已具量化結果**：KL ↓ 20%、NSS = 1.7、CC = 0.4。
- **價值**：證明 fine-tune 可校準 ACLNet 從 object-oriented → spatial-oriented。
- **題目**：Predicting Dynamic Visual Perception in Architectural Spaces: A Spatiotemporal Deep Learning Approach

### Route B — 3D Mesh Pipeline ✦ eCAADe 2026

```
VR + 整合 eye tracker ─► 受試者繞行公共建築（多路徑）─► GT
                                              │
                                              ▼
                 SAL3D（static）+ time-series camera pose
                                  （速度、視角方向）─► dynamic prediction module
                                              │
                                       軌跡感知 saliency
```

- **特殊性**：可評估**相同幾何在不同觀看方向下顯著性是否變化** → 直接服務設計決策。
- **挑戰**：高擬真場景細節、FoV 校準 in-situ 比對。
- **題目**：A 3D Visual Attention Analysis Model for Architectural Space: Integrating Saliency Maps with Dynamic Movement

### 兩條路線關係
- A 路線：快速產出 + 學術能見度（會議）。
- B 路線：碩論主幹 + ecological validity 最高。
- 共同骨幹：**動態 GT 蒐集 → KDE → 與靜態 baseline 對比 → 標準 saliency metrics 評估**。

---

## 4. 基礎設施與已完成項目

| 項目 | 狀態 | 位置 |
|---|---|---|
| Tobii Eye Tracker 5 資料蒐集系統（C++/Python, UDP, 連續錄製） | ✅ 已可用 | `C:\enhanced-tobii-eyetracker\` |
| Sigradi pipeline（ACLNet fine-tune + KDE） | ✅ 已有結果 | 分支 `fixtation_renew` 近期改 KDE / 圖框尺寸 |
| 眼動座標校準測試（9 點 pygame） | ✅ 已寫好 | `python/coordinate_test.py` |
| VAS 比對素材（OpenCV saliency + FineGrained 兩版） | ✅ 已產出 | `vas picture/opencv_result*` |
| VAS Rhino / Grasshopper 試驗（亞歷山大圖、VAS 色彩） | ✅ 已存檔 | `.gh / .3dm` |
| eCAADe 投稿 | 🟡 已提交摘要／submission docx | `ecaade2026/` |
| Sigradi 投稿 | 🟡 摘要修訂中（最新 04/16） | `Sigradi2026/` |
| 3D mesh pipeline 程式碼 | ❌ 待建 | — |
| VR + 眼動 GT 蒐集 protocol | ❌ 待設計 | — |

---

## 5. 後續關鍵任務（建議優先序）

### 短期（投稿 + 收尾 Sigradi 路線）
1. **Sigradi 摘要定稿**：修訂 `sigradi abstract20260416.docx`（最新版仍夾雜中英、有編輯註記要清）。
2. **Sigradi full paper**：補上資料數量、受試者數、影片長度、訓練配置等具體實驗細節 — 摘要目前僅有最終指標。
3. **可重現性整理**：把 KDE / ACLNet fine-tune / 評估 metric 的 Python pipeline 從個人腳本整理成可被審稿人複現的形式。

### 中期（碩論第一塊主幹）
4. **eCAADe 全文撰寫**：以 SAL3D + camera pose 模組的明確網路結構圖、loss function 為核心。
5. **3D pipeline 原型**：實作 time-series camera pose 注入 SAL3D 的 PoC，先在你的眼動系統 + 1–2 棟建築上跑通。
6. **VR + 眼動 GT 蒐集方案**：選 headset（內建 eye tracker 機型）、設計繞行路徑、IRB／受試者同意書。

### 長期（碩論完成）
7. **整合 A / B 兩路線**：定位「2D video 用於量產評估」與「3D mesh 用於設計細部回饋」的應用邊界。
8. **加入主觀面**：在動態 saliency 模型之上疊加情緒／美感主觀評分，建構美學評估框架。
9. **設計回饋實證**：找一個實際設計案例，展示模型輸出如何指引調整 → 完成「工具 → 方法論」的閉環。

---

## 6. 立即可決定的幾個分叉點

- **Sigradi 篇是否擴成 journal**？目前指標已亮眼，是否考慮投 *Buildings* 或 *Automation in Construction*？
- **VR 硬體選型**：HTC Vive Pro Eye、Meta Quest Pro、Varjo XR-4 中哪一台？決定 eCAADe 全文的方法可行性。
- **建築個案**：是否在 Sigradi 與 eCAADe 兩篇之間共用相同的校園建築？這會強化敘事連續性。
- **碩論論文題目**：是否定為「**現代建築動態視覺感知的時空計算模型**」之類的傘狀題，把兩條 pipeline 都收進來？

---

## 7. 主要參考文獻（已蒐集）

### 視覺顯著性／深度學習
- Itti, L., & Koch, C. (2001). Computational modelling of visual attention. *Nature Reviews Neuroscience*, 2(3), 194–203.
- Wang, W., Shen, J., Xie, J., Cheng, M.-M., Ling, H., & Borji, A. (2021). Revisiting Video Saliency Prediction in the Deep Learning Era. *IEEE TPAMI*, 43(1), 220–237.
- SAL3D — A Model for Saliency Prediction in 3D Meshes.
- ACLNet (Attentive CNN-LSTM Network)、ViNet、OFF-ViNet。
- Lavoue (2018) — 2D→3D 視線投射技術。
- Lee (2005) — 高斯加權平均曲率 mesh saliency。

### 建築神經美學與感知
- Brielmann, A. A., Buras, N. H., Salingaros, N. A., & Taylor, R. P. (2022). What Happens in Your Brain When You Walk Down the Street? *Urban Science*, 6(1), 3.
- Buildings, Beauty, and the Brain: A Neuroscience of Architectural Experience.
- The Neuroaesthetics of Architectural Spaces.
- Form Follows Function: Bridging Neuroscience and Architecture.
- Spatial perception of ceiling height and type variation in immersive virtual environments.
- The emotional influence of different geometries in virtual spaces: A neurocognitive examination.

### 親生物與碎形
- Reduction of Physiological Stress Using Fractal Art and Architecture.
- Architectural Lessons From Environmental Psychology: The Case of Biophilic Architecture.
- The Fractal Nature of the Architectural Orders (2004).
- Fractal Geometry in Architecture and Design (1996).

### VAS 工具與相關
- 3M VAS Validation Study.
- Eye Tracking Emulation Software: A Promising Urban Design Tool.
- Architectural Beauty: Developing a Measurable and Objective Scale.

### 同期建築眼動回顧
- Luo, J., Liu, L., Abo, D., & Wang, X. (2026). Eye Movements in Architecture and Environmental Design: A Review. *Buildings*, 16(6), 1231.
- Chien, C.-Y., & Kuo, P.-C. (2025). Incorporating eye-tracking signals into multimodal deep visual models for predicting user aesthetic experience in residential interiors. *arXiv*.

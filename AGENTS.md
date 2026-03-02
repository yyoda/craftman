# エージェント構成とワークフロー (Craftman 2.0)

本プロジェクトは、3つの役割（ロール）による「レシピ駆動」のバケツリレー方式で進行します。

## 1. Input Watcher (分析・設計)
**「何を作るか決め、レシピを書く」**
- **Trigger**: `inbox/` にデータファイル（`.json`, `.csv`, `.md` 等）、またはユーザーからの生成指示が投入された時
- **Task**: 
  - データのバリデーション（形式、欠損値の確認）
  - 生成要件（フォーマット、デザイン、ターゲット読者）の定義
  - **重要**: Python レシピ (`inbox/recipe_xxx.py`) の生成
    - 必須要件: `def generate(output_dir):` 関数を持つこと
    - 依存ライブラリやデータパスを正しく設定すること
- **Output**: `inbox/recipe_[name].py`

## 2. Document Architect (構築・実行)
**「レシピを実行し、形にする」**
- **Trigger**: `inbox/` に Python レシピ (`recipe_*.py`) が生成された時
- **Task**: 
  - レシピのサンドボックス実行 (`python recipe_xxx.py` 相当)
  - 実行エラー時のデバッグと修正
  - 生成物 (`drafts/`) の確認
- **Output**: `drafts/` 内の生成物（`.pptx`, `.docx`, `.pdf` 等）

## 3. Delivery Manager (品質・納品)
**「整えて片付ける」**
- **Trigger**: `drafts/` の生成物に対し、人間によるレビュー完了（OK）が出た時
- **Task**: 
  - ファイル名の正規化（`v1` などのサフィックス除去）
  - `drafts/` から `outputs/` への移動（納品）
  - 使用済みレシピとデータの `inbox/` から `archive/` (または `examples/`) への移動
- **Output**: `outputs/` 内の最終成果物

---

## 補足: スキルの利用方針

`.agents/skills/` ディレクトリのスキルは、Input Watcher がレシピコードを書く際の「コーディング規約・デザインガイド」として機能します。

- **推奨スキル**:
  - `pptx` / `docx`: 各フォーマット生成時のコード実装パターンとして参照
  - `theme-factory` / `brand-guidelines`: 配色やフォント指定のルールとして参照
  - `internal-comms`: 文章構成やトーン＆マナーの指針として参照

- **非推奨スキル**:
  - `mcp-builder`, `webapp-testing` など、ドキュメント生成に直接関与しないもの。


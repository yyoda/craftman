# エージェント構成とワークフロー

本プロジェクトは、3つの役割（ロール）によるバケツリレー方式で進行します。

## 1. Input Watcher (分析・計画)
**「何を作るか決める」**
- **Trigger**: `inbox/` にファイルが置かれた時
- **Task**: 
  - データのバリデーション（形式、欠損値の確認）
  - 生成ドキュメントの構成案（Plan）の作成
- **Output**: `drafts/plan_[filename].md`
  - 必須項目: `Target Audience`, `Key Messages`, `Proposed Structure`


## 2. Document Architect (設計・構築)
**「実際に形にする」**
- **Trigger**: `drafts/` の構成案が承認された時、または `inbox/` のデータを直接処理する時
- **Task**: 
  - テンプレートの適用（指定がない場合は `docx`/`pptx` スキルのデフォルトを使用）
  - **重要**: カスタムテンプレートを使用する場合は、必ず `references/` 内のパスを指示に含めること
  - コンテンツ生成
- **Output**: `drafts/` 内の `.docx`, `.pptx` ファイル（v1, v2...）

## 3. Delivery Manager (品質・納品)
**「整えて片付ける」**
- **Trigger**: 人間によるレビュー完了後
- **Task**: 
  - ファイル名の正規化（`v1` などのサフィックス除去）
  - `drafts/` から `outputs/` への移動
  - 使用済み入力データの `inbox/` から `archive/` への移動
- **Output**: `outputs/` 内の最終成果物

---

## 補足: スキルの利用制限

`.agents/skills/` ディレクトリには多数の汎用スキルが含まれていますが、本プロジェクトでは以下を**非推奨**とします（ドキュメント生成に関係がないため）。
AIは指示がない限り、これらを使用しないでください。

- `mcp-builder`: システム開発用
- `webapp-testing`: Webアプリケーションテスト用
- `web-artifacts-builder`: Webアプリ構築用 (HTMLドキュメント生成には `frontend-design` を使用可)


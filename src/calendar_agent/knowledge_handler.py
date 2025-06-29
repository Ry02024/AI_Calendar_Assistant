import os

def load_knowledge_texts(knowledge_dir=None):
    """
    knowledgeディレクトリ内のテキスト/ドキュメント系ファイルを読み込み、
    {ファイル名: 内容} のdictで返す。
    対応拡張子: .txt, .md, .csv, .json, .doc, .docx
    """
    if knowledge_dir is None:
        knowledge_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'knowledge')
        knowledge_dir = os.path.abspath(knowledge_dir)
    knowledge = {}
    if not os.path.exists(knowledge_dir):
        return knowledge
    allowed_exts = ('.txt', '.md', '.csv', '.json', '.doc', '.docx')
    for fname in os.listdir(knowledge_dir):
        if fname.endswith(allowed_exts):
            path = os.path.join(knowledge_dir, fname)
            try:
                with open(path, encoding='utf-8') as f:
                    knowledge[fname] = f.read()
            except Exception:
                pass
    return knowledge

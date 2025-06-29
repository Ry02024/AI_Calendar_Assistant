import os

def load_knowledge_texts(knowledge_dir=None):
    """
    knowledgeディレクトリ内の全テキストファイルを読み込み、
    {ファイル名: 内容} のdictで返す。
    """
    if knowledge_dir is None:
        knowledge_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'knowledge')
        knowledge_dir = os.path.abspath(knowledge_dir)
    knowledge = {}
    if not os.path.exists(knowledge_dir):
        return knowledge
    for fname in os.listdir(knowledge_dir):
        if fname.endswith('.txt'):
            path = os.path.join(knowledge_dir, fname)
            try:
                with open(path, encoding='utf-8') as f:
                    knowledge[fname] = f.read()
            except Exception:
                pass
    return knowledge

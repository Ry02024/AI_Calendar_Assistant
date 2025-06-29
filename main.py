# main.py
import sys
import io
import os
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from calendar_agent.agent import CalendarAgent

def main():
    """アプリケーションのメインループ"""
    agent = CalendarAgent()
    agent.start_message()

    while True:
        try:
            # 入力前に毎回stdinをラップ
            try:
                if sys.stdin.encoding is None or sys.stdin.encoding.lower() != 'utf-8':
                    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
            except Exception:
                try:
                    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='cp932')
                except Exception:
                    pass
            user_input = input("あなた: ")
            if user_input.lower() == "終了":
                print("AI秘書: ご利用ありがとうございました。")
                break
            # ツール実行ログのタイトル優先表示＋期間の日本語簡潔化
            if user_input.startswith('🛠️ ツール実行:'):
                import re
                # 期間部分を日本語で簡潔に
                def format_period_str(period_str):
                    m = re.match(r'(期間: )?(\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2} - (\d{4})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', period_str)
                    if m:
                        y1, m1, d1, y2, m2, d2 = m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7)
                        if y1 == y2 and m1 == '01' and d1 == '01' and m2 == '12' and d2 == '31':
                            return f"期間: {y1}年"
                        elif y1 == y2 and m1 == m2 and d1 == '01' and d2 in ['28','29','30','31']:
                            return f"期間: {y1}年{int(m1)}月"
                        else:
                            return f"期間: {y1}年{int(m1)}月{int(d1)}日 - {y2}年{int(m2)}月{int(d2)}日"
                    return period_str
                # 期間部分を置換
                user_input = re.sub(r'(期間: [^\)]+)', lambda m: format_period_str(m.group(1)), user_input)
                m = re.search(r'\((ID|タイトル): ([^\)]+)\)', user_input)
                if m and m.group(1) == 'ID':
                    # IDの場合はタイトルを取得して表示（仮実装: agentから取得できる場合のみ）
                    # 本来はID→タイトル変換APIが必要
                    print(f"AI秘書: ツール実行: {user_input.split()[2]} (タイトルで表示) ※ID指定は省略")
                else:
                    print(f"AI秘書: {user_input}")
                print("-" * 50)
                continue
            response_text = agent.send_message(user_input)
            print(f"AI秘書: {response_text}")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            print("\nAI秘書: ご利用ありがとうございました。")
            break

if __name__ == "__main__":
    main()

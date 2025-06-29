# src/chat_agent/agent.py

import google.genai as genai
import config
from src.calendar_agent import tools
from datetime import datetime, timedelta
import json
import re
from .knowledge_handler import load_knowledge_texts

class CalendarAgent:
    """カレンダー操作を行うAIエージェント (Function Calling非対応Gemini用)"""
    def __init__(self):
        self._init_knowledge()
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.system_instruction = self._build_system_instruction()
        self.chat = self.client.chats.create(model=config.MODEL_NAME)
        self.chat.send_message(self.system_instruction)
        self._last_candidates = None

    def _init_knowledge(self):
        knowledge = load_knowledge_texts()
        self.knowledge_text = "\n\n".join([f"【{k}】\n{v}" for k, v in knowledge.items()]) if knowledge else ""

    def _build_system_instruction(self):
        today = datetime.now(tools.JST).strftime('%Y-%m-%d')
        return f"""
あなたは優秀で親切な日本語カレンダーアシスタントです。ユーザーの自然言語による指示を理解し、予定の追加・確認・削除などの指示があれば、必ず下記のJSON形式で返答してください。
---
{{
  "action": "add/list/delete", // 操作種別
  "summary": "タイトル", // 追加・削除時
  "start_time": "開始日時(ISO8601)", // 追加・削除時
  "end_time": "終了日時(ISO8601)", // 追加・削除時
  "is_all_day": true/false, // 追加時
  "description": "説明", // 追加時
  "location": "場所" // 追加時
}}
---
複数予定の場合は複数のJSONコードブロックで返してください。
予定追加・削除・確認以外の質問は通常通り日本語で答えてください。
現在の日付: {today}
---\n【あなたの知識】\n{self.knowledge_text}
"""

    def start_message(self):
        print("AI秘書です。カレンダーの調整など、何でもお申し付けください。(「終了」と入力して会話を終了)")
        print("-" * 50)

    def send_message(self, user_input: str) -> str:
        # 事前分岐
        if re.fullmatch(r'[a-z0-9]{10,}', user_input.strip()):
            return self._delete_by_id(user_input.strip())
        if user_input.strip() == '詳細':
            return self.show_event_details()
        response = self.chat.send_message(user_input)
        json_blocks = self._extract_all_json_blocks(response.text)
        messages = []
        for block in json_blocks:
            action = block.get('action')
            if action == 'add':
                messages.append(self._add_event(block))
            elif action == 'delete':
                messages.append(self._delete_event(block, user_input))
            elif action == 'edit':
                messages.append(self._edit_event(block))
            elif action == 'list':
                messages.append(self._list_event_action(block))
        return '\n'.join(messages) if messages else response.text

    def _delete_by_id(self, event_id):
        del_result = tools.delete_calendar_event(event_id)
        return json.loads(del_result).get('message', f'イベントID {event_id} を削除しました。')

    def _add_event(self, block):
        result = tools.add_calendar_event(
            summary=block.get('summary'),
            start_time=block.get('start_time'),
            end_time=block.get('end_time'),
            description=block.get('description'),
            location=block.get('location'),
            is_all_day=block.get('is_all_day', False)
        )
        return json.loads(result).get('message')

    def _edit_event(self, block):
        summary = block.get('summary')
        start_time = block.get('start_time')
        end_time = block.get('end_time')
        new_summary = block.get('new_summary')
        new_start_time = block.get('new_start_time')
        new_end_time = block.get('new_end_time')
        new_description = block.get('new_description')
        new_location = block.get('new_location')
        # 検索範囲はdelete_eventと同様
        if start_time and end_time:
            list_start = start_time
            list_end = end_time
            if '+' not in list_start and 'Z' not in list_start:
                list_start += '+09:00'
            if '+' not in list_end and 'Z' not in list_end:
                list_end += '+09:00'
        else:
            now = datetime.now(tools.JST)
            list_start = (now - timedelta(days=30)).isoformat(timespec='seconds')
            list_end = (now + timedelta(days=30)).isoformat(timespec='seconds')
            if '+' not in list_start and 'Z' not in list_start:
                list_start += '+09:00'
            if '+' not in list_end and 'Z' not in list_end:
                list_end += '+09:00'
        result = tools.list_calendar_events(list_start, list_end)
        events = json.loads(result).get('events', [])
        candidates = []
        for e in events:
            if summary and summary not in e['summary']:
                continue
            if start_time and start_time[:10] not in e['start']:
                continue
            candidates.append(e)
        if not candidates:
            return '編集候補の予定が見つかりませんでした。タイトルや日付を含めてご指定ください。'
        elif len(candidates) == 1:
            event_id = candidates[0]['id']
            # tools.pyにedit_calendar_eventが必要
            edit_result = tools.edit_calendar_event(
                event_id,
                new_summary=new_summary,
                new_start_time=new_start_time,
                new_end_time=new_end_time,
                new_description=new_description,
                new_location=new_location
            )
            msg = json.loads(edit_result).get('message', '編集しました。')
            return msg
        else:
            # 複数候補がある場合はリストアップして選択 or 詳細表示
            msg = '複数の編集候補が見つかりました。番号で選ぶか「詳細」と入力してください:\n'
            for idx, e in enumerate(candidates):
                msg += f"{idx+1}: {self.format_event_date(e['start'], e['end'], e.get('is_all_day', False))}『{e['summary']}』\n"
            # 詳細表示用の情報を一時保存
            self._last_candidates = candidates
            return msg

    def _list_event_action(self, block):
        start_time = block.get('start_time')
        end_time = block.get('end_time')
        if not start_time or not end_time:
            now = datetime.now(tools.JST)
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat(timespec='seconds')
            if now.month == 12:
                end_dt = now.replace(year=now.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                end_dt = now.replace(month=now.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_time = end_dt.isoformat(timespec='seconds')
        if '+' not in start_time and 'Z' not in start_time:
            start_time += '+09:00'
        if '+' not in end_time and 'Z' not in end_time:
            end_time += '+09:00'
        period_str = self.format_period(start_time, end_time)
        event_list = self.list_events(start_time, end_time)
        return f"{period_str}の予定:\n{event_list}"

    def _delete_event(self, block, user_input):
        summary = block.get('summary')
        start_time = block.get('start_time')
        end_time = block.get('end_time')
        # 指定があればその期間、なければ直近1ヶ月
        if start_time and end_time:
            list_start = start_time
            list_end = end_time
            if '+' not in list_start and 'Z' not in list_start:
                list_start += '+09:00'
            if '+' not in list_end and 'Z' not in list_end:
                list_end += '+09:00'
        else:
            now = datetime.now(tools.JST)
            list_start = (now - timedelta(days=30)).isoformat(timespec='seconds')
            list_end = (now + timedelta(days=30)).isoformat(timespec='seconds')
            if '+' not in list_start and 'Z' not in list_start:
                list_start += '+09:00'
            if '+' not in list_end and 'Z' not in list_end:
                list_end += '+09:00'
        result = tools.list_calendar_events(list_start, list_end)
        events = json.loads(result).get('events', [])
        candidates = []
        for e in events:
            if summary and summary not in e['summary']:
                continue
            if start_time and start_time[:10] not in e['start']:
                continue
            candidates.append(e)
        if not candidates:
            return '削除候補の予定が見つかりませんでした。タイトルや日付を含めてご指定ください。'
        elif len(candidates) == 1:
            event_id = candidates[0]['id']
            del_result = tools.delete_calendar_event(event_id)
            msg = json.loads(del_result).get('message', '削除しました。')
            return msg
        else:
            # LLMに候補リストとユーザー指示を渡して判断させる
            candidate_list = '\n'.join([
                f"{idx+1}: {self.format_event_date(e['start'], e['end'], e.get('is_all_day', False))}『{e['summary']}』" for idx, e in enumerate(candidates)
            ])
            prompt = f"次の削除候補があります。\n{candidate_list}\n\nユーザー指示: {block.get('user_input', '')}\nどの予定を削除すべきか、番号または'全部'で答えてください。" 
            ai_response = self.chat.send_message(prompt).text.strip()
            # 番号や'全部'を抽出
            to_delete = []
            if '全部' in ai_response or '全て' in ai_response or 'すべて' in ai_response:
                to_delete = list(range(len(candidates)))
            else:
                nums = re.findall(r'\d+', ai_response)
                to_delete = [int(n)-1 for n in nums if 0 < int(n) <= len(candidates)]
            if not to_delete:
                return f"AIの判断が曖昧でした: {ai_response}\n番号や'全部'でご指示ください。"
            msgs = []
            for idx in to_delete:
                event_id = candidates[idx]['id']
                del_result = tools.delete_calendar_event(event_id)
                msg = json.loads(del_result).get('message', f"削除しました: {candidates[idx]['summary']}")
                msgs.append(msg)
            return '\n'.join(msgs)

    def _extract_all_json_blocks(self, text):
        # すべてのJSONコードブロックを抽出
        return [json.loads(m) for m in re.findall(r'\{[\s\S]*?\}', text)]

    @staticmethod
    def format_event_date(start, end, is_all_day=False):
        try:
            sdt = datetime.fromisoformat(start.replace('Z', '+09:00'))
            edt = datetime.fromisoformat(end.replace('Z', '+09:00'))
        except Exception:
            return f"{start}〜{end}"
        wdays = ['月', '火', '水', '木', '金', '土', '日']
        if is_all_day or (sdt.hour == 0 and edt.hour == 0 and (edt-sdt).days == 1):
            return f"{sdt.year}年{sdt.month}月{sdt.day}日（{wdays[sdt.weekday()]}）"
        elif sdt.date() == edt.date():
            return f"{sdt.year}年{sdt.month}月{sdt.day}日（{wdays[sdt.weekday()]}）{sdt.strftime('%H:%M')}〜{edt.strftime('%H:%M')}"
        else:
            return f"{sdt.year}年{sdt.month}月{sdt.day}日（{wdays[sdt.weekday()]}）{sdt.strftime('%H:%M')}〜{edt.year}年{edt.month}月{edt.day}日（{wdays[edt.weekday()]}）{edt.strftime('%H:%M')}"

    @staticmethod
    def format_period(start, end, summary=None):
        try:
            sdt = datetime.fromisoformat(start.replace('Z', '+09:00'))
            edt = datetime.fromisoformat(end.replace('Z', '+09:00'))
        except Exception:
            return f"期間: {start} - {end}"
        if sdt.date() == edt.date():
            if sdt.hour != 0 or edt.hour != 0:
                return f"期間: {sdt.year}-{sdt.month:02d}-{sdt.day:02d}, {sdt.strftime('%H:%M')} - {edt.strftime('%H:%M')}"
            else:
                return f"期間: {sdt.year}-{sdt.month:02d}-{sdt.day:02d}"
        if sdt.year == edt.year and sdt.month == edt.month and sdt.day == 1 and (edt.day == 1 or (edt - sdt).days >= 27):
            return f"{sdt.year}年{sdt.month}月"
        return f"期間: {sdt.year}-{sdt.month:02d}-{sdt.day:02d} - {edt.year}-{edt.month:02d}-{edt.day:02d}"

    def list_events(self, start_time, end_time):
        result = tools.list_calendar_events(start_time, end_time)
        events = json.loads(result).get('events', [])
        if not events:
            return '予定はありません。'
        event_list = '\n'.join([
            f"{self.format_event_date(e['start'], e['end'], e.get('is_all_day', False))}『{e['summary']}』" for e in events
        ])
        return event_list

    def show_event_details(self):
        if not hasattr(self, '_last_candidates') or not self._last_candidates:
            return '直前に候補リストがありません。'
        msg = '候補予定の詳細:\n'
        for idx, e in enumerate(self._last_candidates):
            msg += f"{idx+1}: {self.format_event_date(e['start'], e['end'], e.get('is_all_day', False))}『{e['summary']}』\n"
            msg += f"  ID: {e['id']}\n  説明: {e.get('description','')}\n  場所: {e.get('location','')}\n"
        return msg

    # delete_eventにも詳細表示ロジックを追加
    def delete_event(self, block):
        summary = block.get('summary')
        start_time = block.get('start_time')
        end_time = block.get('end_time')
        # 指定があればその期間、なければ直近1ヶ月
        if start_time and end_time:
            list_start = start_time
            list_end = end_time
            if '+' not in list_start and 'Z' not in list_start:
                list_start += '+09:00'
            if '+' not in list_end and 'Z' not in list_end:
                list_end += '+09:00'
        else:
            now = datetime.now(tools.JST)
            list_start = (now - timedelta(days=30)).isoformat(timespec='seconds')
            list_end = (now + timedelta(days=30)).isoformat(timespec='seconds')
            if '+' not in list_start and 'Z' not in list_start:
                list_start += '+09:00'
            if '+' not in list_end and 'Z' not in list_end:
                list_end += '+09:00'
        result = tools.list_calendar_events(list_start, list_end)
        events = json.loads(result).get('events', [])
        candidates = []
        for e in events:
            if summary and summary not in e['summary']:
                continue
            if start_time and start_time[:10] not in e['start']:
                continue
            candidates.append(e)
        if not candidates:
            return '削除候補の予定が見つかりませんでした。タイトルや日付を含めてご指定ください。'
        elif len(candidates) == 1:
            event_id = candidates[0]['id']
            del_result = tools.delete_calendar_event(event_id)
            msg = json.loads(del_result).get('message', '削除しました。')
            return msg
        else:
            # LLMに候補リストとユーザー指示を渡して判断させる
            candidate_list = '\n'.join([
                f"{idx+1}: {self.format_event_date(e['start'], e['end'], e.get('is_all_day', False))}『{e['summary']}』" for idx, e in enumerate(candidates)
            ])
            prompt = f"次の削除候補があります。\n{candidate_list}\n\nユーザー指示: {block.get('user_input', '')}\nどの予定を削除すべきか、番号または'全部'で答えてください。" 
            ai_response = self.chat.send_message(prompt).text.strip()
            # 番号や'全部'を抽出
            to_delete = []
            if '全部' in ai_response or '全て' in ai_response or 'すべて' in ai_response:
                to_delete = list(range(len(candidates)))
            else:
                nums = re.findall(r'\d+', ai_response)
                to_delete = [int(n)-1 for n in nums if 0 < int(n) <= len(candidates)]
            if not to_delete:
                return f"AIの判断が曖昧でした: {ai_response}\n番号や'全部'でご指示ください。"
            msgs = []
            for idx in to_delete:
                event_id = candidates[idx]['id']
                del_result = tools.delete_calendar_event(event_id)
                msg = json.loads(del_result).get('message', f"削除しました: {candidates[idx]['summary']}")
                msgs.append(msg)
            return '\n'.join(msgs)
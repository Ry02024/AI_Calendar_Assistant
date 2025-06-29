# src/calendar_agent/tools.py
import os
import json
from datetime import datetime, timedelta, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

# 日本時間のタイムゾーンを定義
JST = timezone(timedelta(hours=9))

def get_calendar_service():
    """Google Calendar APIのサービス（操作の本体）を取得する関数"""
    creds = None
    if os.path.exists(config.GOOGLE_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.GOOGLE_TOKEN_FILE, config.GOOGLE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.GOOGLE_CREDS_FILE, config.GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.GOOGLE_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

# ▼▼▼ 以下、AIが呼び出すツール群 ▼▼▼

def add_calendar_event(summary: str, start_time: str, end_time: str, is_all_day: bool = False, description: str = None, location: str = None) -> str:
    """
    新しいカレンダーイベントを作成します。時間はJSTとして扱います。
    Args:
        summary (str): イベントのタイトル
        start_time (str): イベントの開始日時 (ISO 8601形式)
        end_time (str): イベントの終了日時 (ISO 8601形式)
        is_all_day (bool, optional): 終日イベントかどうか. Defaults to False.
        description (str, optional): イベントの説明. Defaults to None.
        location (str, optional): イベントの場所. Defaults to None.
    Returns:
        str: 処理結果のJSON文字列
    """
    print(f"🛠️ ツール実行: add_calendar_event (タイトル: {summary})")
    service = get_calendar_service()
    event = {
        'summary': summary,
    }
    if is_all_day:
        event['start'] = {'date': start_time[:10]}
        event['end'] = {'date': end_time[:10]}
    else:
        event['start'] = {'dateTime': start_time, 'timeZone': 'Asia/Tokyo'}
        event['end'] = {'dateTime': end_time, 'timeZone': 'Asia/Tokyo'}
    if description:
        event['description'] = description
    if location:
        event['location'] = location
    
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return json.dumps({
            'status': 'success',
            'message': f"予定『{summary}』を追加しました。",
            'eventId': created_event.get('id')
        })
    except Exception as e:
        return json.dumps({
            'status': 'error',
            'message': f"予定追加時にエラーが発生しました: {e}"
        })

def list_calendar_events(start_time: str, end_time: str) -> str:
    """
    指定された期間のカレンダーの予定リストを取得します。時間はJSTとして扱います。
    """
    print(f"🛠️ ツール実行: list_calendar_events (期間: {start_time} - {end_time})")
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        return json.dumps({"events": [], "message": "指定された期間に予定はありませんでした。"})
    
    simplified_events = [{
        "id": event["id"],
        "summary": event.get("summary", "（タイトルなし）"),
        "start": event["start"].get("dateTime", event["start"].get("date")),
        "end": event["end"].get("dateTime", event["end"].get("date")),
    } for event in events]
    return json.dumps({"events": simplified_events})

def delete_calendar_event(event_id: str) -> str:
    """
    指定されたIDのカレンダーイベントを削除します。
    """
    print(f"🛠️ ツール実行: delete_calendar_event (ID: {event_id})")
    service = get_calendar_service()
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return json.dumps({
            "status": "success",
            "message": f"予定（ID: {event_id}）を削除しました。"
        })
    except HttpError as error:
        return json.dumps({
            "status": "error",
            "message": f"予定の削除中にエラーが発生しました: {error}"
        })
